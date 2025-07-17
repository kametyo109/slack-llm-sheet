import re
import requests
from bs4 import BeautifulSoup
import openai
from datetime import datetime
import os

# Set up OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_slack_app_url(text: str) -> str:
    """Extract Slack app URL from text"""
    slack_app_patterns = [
        r'https://[\w\-\.]+\.slack\.com/apps/[\w\-]+',
        r'https://slack\.com/apps/[\w\-]+',
        r'https://[\w\-]+\.slack\.com/marketplace/[\w\-]+',
        r'https://slack\.com/marketplace/[\w\-]+'
    ]

    for pattern in slack_app_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def scrape_slack_app_page(url: str) -> dict:
    """Scrape Slack app page to get title and description"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to extract title
        title = None
        title_selectors = [
            'h1',
            '.app-title',
            '.app-name',
            '[data-qa="app-name"]',
            'title'
        ]

        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                break

        # Try to extract description
        description = None
        desc_selectors = [
            '.app-description',
            '.app-summary',
            '[data-qa="app-description"]',
            'meta[name="description"]',
            '.description'
        ]

        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    description = element.get('content', '').strip()
                else:
                    description = element.get_text(strip=True)
                break

        return {
            'title': title or 'Unknown App',
            'raw_description': description or 'No description available'
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            'title': 'Unknown App',
            'raw_description': 'Unable to fetch description'
        }

def generate_llm_summary(title: str, raw_description: str) -> str:
    """Use LLM to create a concise summary of what the app does"""
    try:
        prompt = f"""
        Based on the following Slack app information, provide a concise 1-2 sentence summary of what this application does:

        App Name: {title}
        Description: {raw_description}

        Please focus on the main functionality and purpose of the app. Keep it clear and professional.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes Slack app functionality concisely."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating LLM summary: {e}")
        return f"A Slack app called {title}. " + (raw_description[:100] + "..." if len(raw_description) > 100 else raw_description)

def enrich_slack_app(text: str) -> dict:
    """Main function to enrich Slack app mention"""
    slack_url = extract_slack_app_url(text)

    if not slack_url:
        return {}

    # Scrape the page
    scraped_data = scrape_slack_app_page(slack_url)

    # Generate LLM summary
    llm_summary = generate_llm_summary(scraped_data['title'], scraped_data['raw_description'])

    # Return enriched data
    return {
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "app_name": scraped_data['title'],
        "app_description": llm_summary,
        "original_link": slack_url
    }
