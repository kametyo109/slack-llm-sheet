import os
import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Set up the OpenAI client
client = openai.OpenAI()

def fetch_page_metadata(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.title.string.strip() if soup.title else "No Title Found"
        meta_desc_tag = soup.find("meta", attrs={"name": "description"}) or \
                        soup.find("meta", attrs={"property": "og:description"})
        description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else "No Description Found"

        return title, description
    except Exception as e:
        print(f"[Fetch] Failed to fetch metadata from {url}: {e}")
        return None, None

def summarize_webpage(url):
    print(f"[LLM] Summarizing webpage: {url}")
    title, description = fetch_page_metadata(url)

    if not title and not description:
        return None

    prompt = (
        "You are a helpful assistant. A user visited the following website and wants a short summary.\n"
        "Please always respond in English. The user works for a drug discovery company so please write the summary from this perspective.\n\n"
        f"URL: {url}\n"
        f"Title: {title}\n"
        f"Description: {description}\n\n"
        "Please return a JSON object with the following fields:\n"
        "- title: string\n"
        "- description: string\n"
        "- link: string (same as URL)\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a concise assistant helping with drug discovery summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        output = response.choices[0].message.content.strip()
        print("[LLM] Response:", output)

        result = eval(output, {"__builtins__": {}})
        if isinstance(result, dict) and "title" in result and "description" in result:
            result["link"] = url
            return result
        else:
            print("[LLM] Invalid format from LLM.")
            return None
    except Exception as e:
        print(f"[LLM] Failed to summarize webpage: {e}")
        return None
