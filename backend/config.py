"""Application configuration."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Application paths
ROOT_PATH = Path(__file__).parent.parent


class Config(BaseSettings):
    """Application configuration loaded from environment variables.

    All environment variables are prefixed with PI_PORTAL_.
    For example: PI_PORTAL_PI_EXECUTABLE, PI_PORTAL_SERVER_PORT, etc.
    """

    model_config = SettingsConfigDict(
        env_prefix="PI_PORTAL_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Pi configuration
    pi_executable: str = Field(
        default="pi",
        description="Path to the Pi executable",
    )
    pi_session_dir: Path = Field(
        default=Path("data/pi_sessions"),
        description="Directory for Pi session storage",
    )

    # Server configuration
    server_host: str = Field(
        default="0.0.0.0",
        description="Host to bind the server to",
    )
    server_port: int = Field(
        default=8000,
        description="Port to run the server on",
    )
    server_reload: bool = Field(
        default=False,
        description="Enable auto-reload during development",
    )

    # Computed paths (not configurable via env vars)
    @property
    def config_path(self) -> Path:
        """Path to config directory."""
        return ROOT_PATH / "config"

    @property
    def frontend_path(self) -> Path:
        """Path to frontend directory."""
        return ROOT_PATH / "frontend"

    def get_absolute_session_dir(self) -> Path:
        """Get absolute path to session directory, creating it if needed."""
        session_dir = self.pi_session_dir
        if not session_dir.is_absolute():
            session_dir = ROOT_PATH / session_dir
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir


# Singleton instance
config = Config()
