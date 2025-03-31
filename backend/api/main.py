"""Main FastAPI application for ATLAS."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="ATLAS API",
    description="API for transforming web articles into valuable knowledge assets",
    version="0.1.0",
)


class ArticleURL(BaseModel):
    """Model for article URL submission."""

    url: str
    purpose_tag: str | None = None


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to ATLAS API"}


@app.post("/prospecting/")
async def prospect_article(article: ArticleURL) -> dict[str, str]:
    """Endpoint for article prospecting (Taste stage)."""
    # This is a placeholder for the actual implementation
    return {
        "status": "received",
        "url": article.url,
        "purpose_tag": article.purpose_tag or "general",
    }
