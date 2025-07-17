import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def enrich_with_llm(parsed_dict):
    prompt = f"""
You are helping log GitHub projects into a structured Google Sheet. Based on the information below, extract and fill in the following fields:

1. Application Name
2. Description of what it does (1–2 sentences max)
3. Developer (individual or org name)
4. GitHub Link (keep as-is)
5. Paper Link (only if clearly mentioned; else blank)

Input:
{parsed_dict}

Output format (as JSON):
{{
  "name": "...",
  "description": "...",
  "author": "...",
  "github": "...",
  "paper": "..."
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{ "role": "user", "content": prompt }]
    )

    content = response["choices"][0]["message"]["content"]

    try:
        parsed_output = json.loads(content)
    except Exception:
        parsed_output = parsed_dict  # fallback to GitHub scrape only

    return parsed_output
