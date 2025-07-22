import os
import openai
import requests
from bs4 import BeautifulSoup

# Create the OpenAI client using the API key from environment
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
        return None  # Exit early if nothing to summarize

    # Construct the prompt
    prompt = (
        "You are a helpful assistant that summarizes Slack app pages.\n"
        f"URL: {url}\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        "Return a JSON object with the following fields: title, description, and link. "
        "Make it concise and informative for logging into a spreadsheet."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a concise Slack app explainer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        output = response.choices[0].message.content.strip()
        print("[LLM] Response:", output)

        # Try to eval the string to convert to dict (be cautious with unknown input)
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
