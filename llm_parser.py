# llm_parser.py

import os
import re
import json
import openai

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_metadata(text):
    """
    Extracts GitHub link and mentioned Slack username (e.g., @user) from the input text.
    """
    github_match = re.search(r"https?://github\.com/\S+", text)
    mention_match = re.search(r"@(\w+)", text)

    return {
        "github_link": github_match.group(0) if github_match else None,
        "mentioned_user": mention_match.group(1) if mention_match else None
    }

def enrich_with_llm(parsed):
    """
    Given metadata, use OpenAI GPT to return structured app metadata.
    Returns a dictionary with fields like app_name, purpose, author, etc.
    """
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

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            { "role": "user", "content": prompt }
        ]
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "error": "Could not parse LLM response as JSON",
            "raw_response": content
        }
