def parse_github_repo(url: str):
    try:
        parts = url.strip("/").split("/")
        if "github.com" in parts:
            idx = parts.index("github.com")
            author, repo = parts[idx + 1], parts[idx + 2]
        else:
            author, repo = parts[-2], parts[-1]
        return author, repo
    except Exception as e:
        print(f"Error parsing GitHub URL: {e}")
        return None, None
