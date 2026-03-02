"""Pi Portal - FastAPI backend."""

from fastapi import FastAPI

app = FastAPI(title="Pi Portal")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
