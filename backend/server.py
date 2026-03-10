"""Server entry point using configuration."""

import uvicorn

from backend.config import config

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=config.server_host,
        port=config.server_port,
        reload=config.server_reload,
    )
