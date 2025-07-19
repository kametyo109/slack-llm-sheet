import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarize_webpage(url):
    try:
        print(f"[LLM] Fetching content from {url}")
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        text = text[:3000]  # Trim for token limit

        prompt = f"""
You are a helpful assistant. A user visited the following website and wants a short summary.
URL: {url}

Based on the following content, please return:
- Title of the page
- Brief description (1-2 sentences max)

Content:
{text}

Return as JSON in this format:
{{"title": "...", "description": "..."}}
"""

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        raw = completion.choices[0].message.content.strip()
        print(f"[LLM] Raw response: {raw}")

        # Eval safely
        import json
        return json.loads(raw)

    except Exception as e:
        print(f"[LLM] Error summarizing {url}: {e}")
        return {"title": "N/A", "description": "N/A"}
