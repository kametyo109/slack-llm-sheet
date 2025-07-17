from fastapi import FastAPI, Request
from pydantic import BaseModel
import re
import os
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Message(BaseModel):
    text: str

def extract_metadata(text):
    github_match = re.search(r"https?://github\.com/\S+", text)
    mention_match = re.search(r"@(\w+)", text)

    return {
        "github_link": github_match.group(0) if github_match else None,
        "mentioned_user": mention_match.group(1) if mention_match else None
    }

def enrich_with_llm(metadata: dict):
    prompt = f"""
Based on the following metadata, provide:
- App name
- Purpose
- Author (GitHub handle if possible)
- GitHub link
- Related paper (if available)

Metadata: {metadata}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

@app.get("/")
def health_check():
    return {"status": "LLM service is live"}

@app.post("/parse")
def parse_message(message: Message):
    metadata = extract_metadata(message.text)
    enriched_info = enrich_with_llm(metadata)
    return {
        "extracted": metadata,
        "enriched": enriched_info
    }
