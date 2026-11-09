from mcp.server.mcpserver import MCPServer
from typing import Any, Dict, List, Optional
import os
import sys
import logging

try:
    import httpx2 as httpx
except ImportError:
    import httpx

# stdout is reserved for the MCP protocol on stdio transport
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

DEV_TO_BASE_URL = "https://dev.to/api"
MAX_PER_PAGE = 1000
MAX_TAGS = 4

# Global variable named "mcp" so `mcp dev` can find it
mcp = MCPServer("Dev.to MCP Server")


class DevToError(Exception):
    """An error with a message that is safe and readable to show to the LLM."""

def get_api_key() -> str:
    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        raise DevToError("DEVTO_API_KEY environment variable is not set.")
    return api_key


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
 
_STATUS_MESSAGES = {
    400: "Bad request - invalid data provided",
    401: "Unauthorized - invalid or missing API key",
    403: "Forbidden - you don't have permission to do that",
    404: "Not found",
    422: "Validation error",
    429: "Rate limit reached - please try again in 30 seconds",
}
 
 
async def devto_request(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    auth: bool = False,
) -> Any:
    """Call the dev.to API and turn any failure into a DevToError."""
    headers = {"Accept": "application/vnd.forem.api-v1+json"}
    if auth:
        headers["api-key"] = get_api_key()
        headers["Content-Type"] = "application/json"
 
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                f"{DEV_TO_BASE_URL}{path}",
                params=params,
                json=json,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
 
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        message = _STATUS_MESSAGES.get(status, f"Request failed (HTTP {status})")
        try:
            detail = e.response.json()
        except ValueError:
            detail = e.response.text[:500]
        logger.error("dev.to API error %s on %s %s: %s", status, method, path, detail)
        raise DevToError(f"{message}. Details: {detail}") from e
 
    except httpx.HTTPError as e:
        logger.exception("Network error on %s %s: %s", method, path, e)
        raise DevToError(f"Could not reach dev.to: {e}") from e
 
 
# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
 
@mcp.tool()
async def search_articles(
    query: str,
    per_page: int = 10,
    page: int = 1,
    tag: Optional[str] = None,
    username: Optional[str] = None,
    state: Optional[str] = None,
    top: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Search for articles on dev.to by topic/keyword.
 
    Args:
        query: The search query/topic (e.g. "laravel authentication", "react hooks").
        per_page: Number of articles to return per page (default 10, max 1000).
        page: Page number for pagination (default 1).
        tag: Filter by a specific tag.
        username: Filter by a specific username.
        state: Filter by article state ("fresh" for recent articles).
        top: Filter by top articles (7 for weekly, 30 for monthly, etc.).
 
    Returns:
        A list of article objects with title, description, URL, tags, etc.
    """
    params: Dict[str, Any] = {"per_page": min(per_page, MAX_PER_PAGE), "page": page}
 
    if query:
        params["q"] = query
    if tag:
        params["tag"] = tag
    if username:
        params["username"] = username
    if state:
        params["state"] = state
    if top:
        params["top"] = top
 
    return await devto_request("GET", "/articles", params=params)
 
 
@mcp.tool()
async def get_article(article_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific dev.to article.
 
    Args:
        article_id: The article ID or path (e.g. "2546060" or
            "devteam/join-the-worlds-largest-hackathon-1-million-in-prizes-3hfh").
 
    Returns:
        The full article object, including body_html, body_markdown,
        comment count, reactions, etc.
    """
    if not article_id or not article_id.strip():
        raise DevToError("article_id is required and cannot be empty.")
 
    return await devto_request("GET", f"/articles/{article_id.strip()}")
 
 
@mcp.tool()
async def get_tags(per_page: int = 10, page: int = 1) -> List[Dict[str, Any]]:
    """Get popular tags from dev.to.
 
    Args:
        per_page: Number of tags to return (default 10, max 1000).
        page: Page number for pagination (default 1).
 
    Returns:
        A list of popular tags with their information.
    """
    params = {"per_page": min(per_page, MAX_PER_PAGE), "page": page}
    return await devto_request("GET", "/tags", params=params)
 
 
@mcp.tool()
async def create_article(
    title: str,
    body_markdown: str,
    published: bool = False,
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
    canonical_url: Optional[str] = None,
    main_image: Optional[str] = None,
    organization_id: Optional[int] = None,
    series: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new article on dev.to.
 
    Articles are created as drafts by default (published=False). Requires a
    valid DEVTO_API_KEY. If you hit the rate limit, wait 30 seconds and retry.
 
    Args:
        title: The title of the article.
        body_markdown: The article content in markdown format.
        published: Whether to publish immediately (default False = draft).
        tags: List of tags for the article (max 4).
        description: Brief description/summary of the article.
        canonical_url: Canonical URL if this is a cross-post.
        main_image: URL of the main image for the article.
        organization_id: ID of the organization to publish under.
        series: Name of the series this article belongs to.
 
    Returns:
        The created article object including ID, URL, etc.
    """
    if not title or not title.strip():
        raise DevToError("Title is required and cannot be empty.")
    if not body_markdown or not body_markdown.strip():
        raise DevToError("body_markdown is required and cannot be empty.")
 
    article_data: Dict[str, Any] = {
        "title": title.strip(),
        "body_markdown": body_markdown,
        "published": published,
    }
 
    if tags:
        article_data["tags"] = tags[:MAX_TAGS]
    if description:
        article_data["description"] = description
    if canonical_url:
        article_data["canonical_url"] = canonical_url
    if main_image:
        article_data["main_image"] = main_image
    if organization_id:
        article_data["organization_id"] = organization_id
    if series:
        article_data["series"] = series
 
    article = await devto_request(
        "POST", "/articles", json={"article": article_data}, auth=True
    )
    logger.info("Article created: %s", article.get("title", "Unknown title"))
    return article
 
 
@mcp.tool()
async def update_article(
    article_id: str,
    title: Optional[str] = None,
    body_markdown: Optional[str] = None,
    published: Optional[bool] = None,
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
    canonical_url: Optional[str] = None,
    main_image: Optional[str] = None,
    organization_id: Optional[int] = None,
    series: Optional[str] = None,
) -> Dict[str, Any]:
    """Update an existing article on dev.to.
 
    Only the fields you provide are changed. You can only update your own
    articles. If body_markdown contains front matter, it takes precedence over
    the equivalent parameters. Requires a valid DEVTO_API_KEY.
 
    Args:
        article_id: The ID of the article to update (e.g. "2546060").
        title: New title.
        body_markdown: New content in markdown format.
        published: Publish (True) or unpublish (False) the article.
        tags: New list of tags (max 4).
        description: New brief description/summary.
        canonical_url: New canonical URL.
        main_image: New main image URL.
        organization_id: ID of the organization to publish under.
        series: Name of the series this article belongs to.
 
    Returns:
        The updated article object including ID, URL, etc.
    """
    if not article_id or not article_id.strip():
        raise DevToError("article_id is required and cannot be empty.")
 
    article_data: Dict[str, Any] = {}
 
    if title is not None:
        if not title.strip():
            raise DevToError("Title cannot be empty if provided.")
        article_data["title"] = title.strip()
    if body_markdown is not None:
        if not body_markdown.strip():
            raise DevToError("body_markdown cannot be empty if provided.")
        article_data["body_markdown"] = body_markdown
    if published is not None:
        article_data["published"] = published
    if tags is not None:
        article_data["tags"] = tags[:MAX_TAGS]
    if description is not None:
        article_data["description"] = description
    if canonical_url is not None:
        article_data["canonical_url"] = canonical_url
    if main_image is not None:
        article_data["main_image"] = main_image
    if organization_id is not None:
        article_data["organization_id"] = organization_id
    if series is not None:
        article_data["series"] = series
 
    if not article_data:
        raise DevToError("At least one field must be provided to update the article.")
 
    article = await devto_request(
        "PUT",
        f"/articles/{article_id.strip()}",
        json={"article": article_data},
        auth=True,
    )
    logger.info("Article updated: %s", article.get("title", "Unknown title"))
    return article



def main():
    try:
        key = get_api_key()
    except RuntimeError as e:
        logger.exception(str(e))
        sys.exit(1)

    # Masked, so the full token doesn't end up in your terminal history or screenshots
    masked = f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "****"
    logger.info(f"DEVTO_API_KEY found: {masked} (length: {len(key)})")
    
    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()