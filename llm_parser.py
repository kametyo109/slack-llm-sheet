import re
import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_metadata(text):
    github_match = re.search(r"https?://github\.com/\S+", text)
    mention_match = re.search(r"@(\w+)", text)

    return {
        "github_link": github_match.group(0) if github_match else None,
        "mentioned_user": mention_match.group(1) if mention_match else None
    }

def enrich_with_llm(parsed):
    prompt = f"""
You are an assistant that extracts structured metadata for a GitHub project.
Return a JSON with the following fields:
- app_name
- purpose
- author
- github_link
- paper_link (optional)

Metadata: {parsed}
Respond in JSON only.
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }]
    )

    raw_content = response.choices[0].message.content.strip()

    try:
        enriched = json.loads(raw_content)
    except json.JSONDecodeError:
        enriched = {"error": "LLM output could not be parsed", "raw": raw_content}

    return enriched
