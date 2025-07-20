import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_webpage(url):
    try:
        print(f"[LLM] Fetching content from {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        text = text[:3000]  # Limit size

        prompt = f"""
You are a helpful assistant. A user visited the following website and wants a short summary.
Please always respond in English. The user works for a drug discovery company so please write the summary from this perspective.

URL: {url}

Based on the content, return a JSON object:
{{
  "title": "...",
  "description": "..."
}}

Content:
{text}
"""

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        raw = completion.choices[0].message.content.strip()
        print(f"[LLM] Raw response from OpenAI: {raw}")

        return json.loads(raw)

    except Exception as e:
        print(f"[LLM] Error summarizing {url}: {e}")
        return {"title": "N/A", "description": "N/A"}
