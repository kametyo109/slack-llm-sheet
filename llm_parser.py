import openai
import os
from github_parser import parse_github_repo

openai.api_key = os.getenv("OPENAI_API_KEY")

def enrich_repository(text: str):
    import re
    match = re.search(r"https://github\.com/\S+", text)
    if not match:
        return {}

    github_url = match.group()
    author, name = parse_github_repo(github_url)

    prompt = f"Extract metadata from this GitHub repo link: {github_url}. Return as JSON with fields: name, author, description, paper_url (if any), and one-word tag."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        content = response["choices"][0]["message"]["content"]
        result = eval(content)
        result["github_url"] = github_url
        return result
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return {}
