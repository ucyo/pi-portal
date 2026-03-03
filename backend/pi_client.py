"""Pi RPC client for communicating with Pi coding agent."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, AsyncIterator, Callable

logger = logging.getLogger(__name__)


class PiClient:
    """Client for communicating with Pi via JSON-RPC over subprocess."""

    def __init__(
        self,
        session_dir: Path | None = None,
        pi_executable: str = "pi",
    ):
        """Initialize Pi client.

        Args:
            session_dir: Directory for Pi session storage. Defaults to data/pi_sessions/.
            pi_executable: Path to Pi executable. Defaults to "pi".
        """
        self.session_dir = session_dir or Path("data/pi_sessions")
        self.pi_executable = pi_executable
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    @property
    def is_running(self) -> bool:
        """Check if Pi process is running."""
        return self._process is not None and self._process.returncode is None

    async def start(self) -> None:
        """Start the Pi subprocess in RPC mode."""
        async with self._lock:
            if self.is_running:
                logger.warning("Pi process already running")
                return

            # Ensure session directory exists
            self.session_dir.mkdir(parents=True, exist_ok=True)

            cmd = [
                self.pi_executable,
                "--mode",
                "rpc",
                "--session-dir",
                str(self.session_dir),
            ]

            logger.info(f"Starting Pi process: {' '.join(cmd)}")

            self._process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            logger.info(f"Pi process started with PID {self._process.pid}")

    async def stop(self) -> None:
        """Stop the Pi subprocess gracefully."""
        async with self._lock:
            if not self.is_running:
                logger.warning("Pi process not running")
                return

            logger.info("Stopping Pi process...")

            # Close stdin to signal EOF
            if self._process.stdin:
                self._process.stdin.close()
                await self._process.stdin.wait_closed()

            # Wait for process to terminate with timeout
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5.0)
                logger.info("Pi process stopped gracefully")
            except asyncio.TimeoutError:
                logger.warning("Pi process did not stop, terminating...")
                self._process.terminate()
                try:
                    await asyncio.wait_for(self._process.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    logger.error("Pi process did not terminate, killing...")
                    self._process.kill()
                    await self._process.wait()

            self._process = None

    async def send_command(self, command: dict[str, Any]) -> None:
        """Send a command to Pi via stdin.

        Args:
            command: JSON-RPC command dictionary.

        Raises:
            RuntimeError: If Pi process is not running.
        """
        if not self.is_running or not self._process.stdin:
            raise RuntimeError("Pi process is not running")

        line = json.dumps(command) + "\n"
        self._process.stdin.write(line.encode())
        await self._process.stdin.drain()
        logger.info(f"[PI TX] {line.strip()}")

    async def read_events(self) -> AsyncIterator[dict[str, Any]]:
        """Read events from Pi stdout as an async iterator.

        Yields:
            Parsed JSON event dictionaries.

        Raises:
            RuntimeError: If Pi process is not running.
        """
        if not self.is_running or not self._process.stdout:
            raise RuntimeError("Pi process is not running")

        while True:
            line = await self._process.stdout.readline()
            if not line:
                # EOF - process ended
                logger.info("[PI] Process stdout closed (EOF)")
                # Check if there's stderr output
                if self._process.stderr:
                    stderr = await self._process.stderr.read()
                    if stderr:
                        logger.error(f"[PI STDERR] {stderr.decode().strip()}")
                break

            line_str = line.decode().strip()
            logger.info(f"[PI RX] {line_str}")

            try:
                event = json.loads(line_str)
                yield event
            except json.JSONDecodeError as e:
                logger.warning(f"[PI] Failed to parse output as JSON: {e}")

    async def prompt(
        self,
        message: str,
        on_event: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any] | None:
        """Send a prompt and wait for completion.

        Args:
            message: The prompt message to send.
            on_event: Optional callback for each event received.

        Returns:
            The agent_end event containing all generated messages, or None if failed.

        Raises:
            RuntimeError: If Pi process is not running.
        """
        await self.send_command({"type": "prompt", "message": message})

        result = None
        async for event in self.read_events():
            if on_event:
                on_event(event)

            event_type = event.get("type")

            # Check for response to prompt command
            if event_type == "response" and event.get("command") == "prompt":
                if not event.get("success"):
                    logger.error(f"Prompt failed: {event.get('error')}")
                    return None

            # agent_end signals completion
            if event_type == "agent_end":
                result = event
                break

        return result

    async def get_state(self) -> dict[str, Any] | None:
        """Get current Pi session state.

        Returns:
            State data dictionary, or None if failed.
        """
        await self.send_command({"type": "get_state"})

        async for event in self.read_events():
            if event.get("type") == "response" and event.get("command") == "get_state":
                if event.get("success"):
                    return event.get("data")
                else:
                    logger.error(f"get_state failed: {event.get('error')}")
                    return None

        return None

    async def abort(self) -> bool:
        """Abort current Pi operation.

        Returns:
            True if abort was successful.
        """
        await self.send_command({"type": "abort"})

        async for event in self.read_events():
            if event.get("type") == "response" and event.get("command") == "abort":
                return event.get("success", False)

        return False

    async def get_commands(self) -> dict[str, Any] | None:
        """Get available commands (extensions, prompts, skills).

        Returns:
            Dictionary with 'commands' list, or None if failed.
            Each command has: name, description, source (extension/prompt/skill),
            and optionally location and path.
        """
        await self.send_command({"type": "get_commands"})

        async for event in self.read_events():
            if (
                event.get("type") == "response"
                and event.get("command") == "get_commands"
            ):
                if event.get("success"):
                    return event.get("data")
                else:
                    logger.error(f"get_commands failed: {event.get('error')}")
                    return None

        return None

    async def get_skills(self) -> list[dict[str, Any]]:
        """Get available skills.

        Returns:
            List of skill dictionaries with name, description, location, and path.
        """
        data = await self.get_commands()
        if not data:
            return []

        commands = data.get("commands", [])
        return [c for c in commands if c.get("source") == "skill"]


# Module-level client instance for convenience
_default_client: PiClient | None = None


def get_pi_client() -> PiClient:
    """Get or create the default Pi client instance."""
    global _default_client
    if _default_client is None:
        _default_client = PiClient()
    return _default_client
