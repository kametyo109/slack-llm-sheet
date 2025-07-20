import os
import json
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_html_with_fallback(url):
    """Try requests first. If blocked, use Selenium."""
    try:
        print(f"[LLM] Trying requests for {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                           (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if "enable JavaScript" in response.text or "Cloudflare" in response.text:
            raise ValueError("Blocked by JavaScript or anti-bot system.")
        return response.text
    except Exception as e:
        print(f"[LLM] Fallback to Selenium due to: {e}")
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.get(url)
        time.sleep(3)  # Wait for JS to load
        html = driver.page_source
        driver.quit()
        return html

def summarize_webpage(url):
    try:
        print(f"[LLM] Fetching content from {url}")
        html = fetch_html_with_fallback(url)
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        text = text[:3000]  # Limit size for OpenAI context

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
