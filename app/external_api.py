import httpx
from typing import Dict, Any, List
from app.config import GITHUB_USERNAME

async def fetch_github_repositories() -> Dict[str, Any]:
    """
    Query the public GitHub REST API to fetch recent repositories and metadata.
    Fulfills the external API integration requirement.
    """
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=updated&per_page=5"
    headers = {
        "User-Agent": "AI-Native-Personal-Profile/1.0",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                repos = response.json()
                summary_repos: List[Dict[str, Any]] = [
                    {
                        "name": r.get("name"),
                        "description": r.get("description"),
                        "language": r.get("language"),
                        "stars": r.get("stargazers_count"),
                        "html_url": r.get("html_url")
                    }
                    for r in repos
                ]
                return {
                    "status": "success",
                    "service": "GitHub REST API",
                    "data": summary_repos
                }
            else:
                return {
                    "status": "error",
                    "service": "GitHub REST API",
                    "message": f"GitHub returned status code {response.status_code}"
                }
    except Exception as exc:
        return {
            "status": "error",
            "service": "GitHub REST API",
            "message": str(exc)
        }
