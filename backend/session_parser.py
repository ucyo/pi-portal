"""
Session Parser for Pi's JSONL session files.

Parses Pi's native JSONL format to extract session metadata and messages.
Sessions are stored as JSON Lines files with a tree structure linked via id/parentId.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SessionHeader:
    """Session metadata from the header line."""

    id: str
    timestamp: str
    cwd: str
    version: int = 3
    parent_session: str | None = None


@dataclass
class ParsedMessage:
    """A message extracted from the session."""

    id: str
    parent_id: str | None
    timestamp: str
    role: str  # user, assistant, toolResult, bashExecution, custom, etc.
    content: str  # Rendered text content
    raw_message: dict[str, Any]  # Original message data
    message_timestamp: int | None = None  # Unix ms timestamp from message


@dataclass
class FeedbackEntry:
    """Feedback stored in session via CustomEntry."""

    target_timestamp: int
    rating: int  # -1, 0, or 1
    comment: str | None
    timestamp: int  # When feedback was recorded


@dataclass
class ParsedSession:
    """Fully parsed session data."""

    header: SessionHeader
    messages: list[ParsedMessage] = field(default_factory=list)
    feedback: list[FeedbackEntry] = field(default_factory=list)
    name: str | None = None  # From session_info entry
    title: str = ""  # Generated from first user message if no name

    @property
    def display_name(self) -> str:
        """Return session name or generated title."""
        return self.name or self.title or "Untitled Session"


def parse_session_file(path: Path) -> ParsedSession:
    """
    Parse a Pi session JSONL file.

    Args:
        path: Path to the .jsonl session file

    Returns:
        ParsedSession with header, messages, feedback, and metadata

    Raises:
        ValueError: If file format is invalid
        FileNotFoundError: If file doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Session file not found: {path}")

    entries: list[dict[str, Any]] = []

    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                entries.append(entry)
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON at line {line_num}: {e}")
                continue

    if not entries:
        raise ValueError(f"Empty session file: {path}")

    # First entry should be session header
    header_entry = entries[0]
    if header_entry.get("type") != "session":
        raise ValueError(
            f"First entry must be session header, got: {header_entry.get('type')}"
        )

    header = SessionHeader(
        id=header_entry.get("id", ""),
        timestamp=header_entry.get("timestamp", ""),
        cwd=header_entry.get("cwd", ""),
        version=header_entry.get("version", 1),
        parent_session=header_entry.get("parentSession"),
    )

    # Build entry lookup and find leaf
    entry_map: dict[str, dict[str, Any]] = {}
    children: dict[str | None, list[str]] = {None: []}
    session_name: str | None = None
    feedback_entries: list[FeedbackEntry] = []

    for entry in entries[1:]:  # Skip header
        entry_id = entry.get("id")
        if entry_id:
            entry_map[entry_id] = entry
            parent_id = entry.get("parentId")
            if parent_id not in children:
                children[parent_id] = []
            children[parent_id].append(entry_id)

        # Extract session name from session_info entries
        if entry.get("type") == "session_info":
            name = entry.get("name")
            if name:
                session_name = name

        # Extract feedback from custom entries
        if (
            entry.get("type") == "custom"
            and entry.get("customType") == "pi-portal-feedback"
        ):
            data = entry.get("data", {})
            feedback_entries.append(
                FeedbackEntry(
                    target_timestamp=data.get("targetTimestamp", 0),
                    rating=data.get("rating", 0),
                    comment=data.get("comment"),
                    timestamp=data.get("timestamp", 0),
                )
            )

    # Find leaf by walking to entries with no children
    leaf_id = _find_leaf(children)

    # Build message list by walking from leaf to root
    messages = _build_message_chain(leaf_id, entry_map)

    # Generate title from first user message
    title = _generate_title(messages)

    return ParsedSession(
        header=header,
        messages=messages,
        feedback=feedback_entries,
        name=session_name,
        title=title,
    )


def _find_leaf(children: dict[str | None, list[str]]) -> str | None:
    """
    Find the leaf entry ID (entry with no children).

    For a linear session, this is simply the last entry.
    For branched sessions, we follow the "rightmost" path (last child at each level).
    """
    current: str | None = None

    # Start from root (parentId = None)
    while True:
        child_ids = children.get(current, [])
        if not child_ids:
            return current
        # Follow the last child (most recent in linear sessions)
        current = child_ids[-1]


def _build_message_chain(
    leaf_id: str | None, entry_map: dict[str, dict[str, Any]]
) -> list[ParsedMessage]:
    """
    Build message list by walking from leaf to root, then reversing.

    Only includes message entries (type="message"), skipping metadata entries.
    """
    messages: list[ParsedMessage] = []
    current_id = leaf_id

    while current_id:
        entry = entry_map.get(current_id)
        if not entry:
            break

        if entry.get("type") == "message":
            message = entry.get("message", {})
            parsed = _parse_message_entry(entry, message)
            if parsed:
                messages.append(parsed)

        current_id = entry.get("parentId")

    # Reverse to get chronological order
    messages.reverse()
    return messages


def _parse_message_entry(
    entry: dict[str, Any], message: dict[str, Any]
) -> ParsedMessage | None:
    """Parse a message entry into ParsedMessage."""
    role = message.get("role", "")

    # Extract text content based on role
    content = _extract_content(message)

    return ParsedMessage(
        id=entry.get("id", ""),
        parent_id=entry.get("parentId"),
        timestamp=entry.get("timestamp", ""),
        role=role,
        content=content,
        raw_message=message,
        message_timestamp=message.get("timestamp"),
    )


def _extract_content(message: dict[str, Any]) -> str:
    """Extract readable text content from a message."""
    role = message.get("role", "")
    content = message.get("content")

    if role == "user":
        # User content can be string or array of content blocks
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return _extract_text_from_blocks(content)

    elif role == "assistant":
        # Assistant content is array of content blocks
        if isinstance(content, list):
            return _extract_text_from_blocks(content)

    elif role == "toolResult":
        # Tool result content is array
        if isinstance(content, list):
            return _extract_text_from_blocks(content)
        return str(content) if content else ""

    elif role == "bashExecution":
        # Bash execution has command and output
        cmd = message.get("command", "")
        output = message.get("output", "")
        return f"$ {cmd}\n{output}"

    elif role == "custom":
        # Custom message from extensions
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return _extract_text_from_blocks(content)

    return str(content) if content else ""


def _extract_text_from_blocks(blocks: list[dict[str, Any]]) -> str:
    """Extract text from content blocks, ignoring thinking/toolCall blocks."""
    texts = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type", "")
        if block_type == "text":
            text = block.get("text", "")
            if text:
                texts.append(text)
        # Skip thinking, toolCall, image blocks for text extraction
    return "\n".join(texts)


def _generate_title(messages: list[ParsedMessage], max_length: int = 50) -> str:
    """Generate a session title from the first user message."""
    for msg in messages:
        if msg.role == "user" and msg.content:
            title = msg.content.strip()
            # Truncate if too long
            if len(title) > max_length:
                title = title[:max_length].rsplit(" ", 1)[0] + "..."
            return title
    return ""


def get_session_metadata(path: Path) -> dict[str, Any]:
    """
    Get lightweight session metadata without parsing all messages.

    Returns:
        Dict with id, timestamp, cwd, name/title, message_count
    """
    if not path.exists():
        raise FileNotFoundError(f"Session file not found: {path}")

    header: dict[str, Any] | None = None
    session_name: str | None = None
    first_user_message: str | None = None
    message_count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_type = entry.get("type")

            if entry_type == "session" and header is None:
                header = entry

            elif entry_type == "session_info":
                name = entry.get("name")
                if name:
                    session_name = name

            elif entry_type == "message":
                message_count += 1
                # Capture first user message for title
                msg = entry.get("message", {})
                if msg.get("role") == "user" and first_user_message is None:
                    content = msg.get("content")
                    if isinstance(content, str):
                        first_user_message = content
                    elif isinstance(content, list):
                        first_user_message = _extract_text_from_blocks(content)

    if not header:
        raise ValueError(f"No session header found: {path}")

    # Generate title
    title = ""
    if first_user_message:
        title = first_user_message.strip()
        if len(title) > 50:
            title = title[:50].rsplit(" ", 1)[0] + "..."

    return {
        "id": header.get("id", ""),
        "timestamp": header.get("timestamp", ""),
        "cwd": header.get("cwd", ""),
        "name": session_name,
        "title": title,
        "display_name": session_name or title or "Untitled Session",
        "message_count": message_count,
        "file_path": str(path),
    }
