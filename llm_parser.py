import re

def enrich_repository(text: str) -> dict:
    github_match = re.search(r'https://github.com/([\w\-]+)/([\w\-]+)', text)
    author = re.search(r'@([\w\-]+)', text)

    if github_match:
        owner, repo = github_match.groups()
        return {
            "app_name": repo,
            "purpose": "TBD",
            "author": author.group(1) if author else "unknown",
            "github_link": github_match.group(0),
            "paper_link": "N/A"
        }
    return {}
