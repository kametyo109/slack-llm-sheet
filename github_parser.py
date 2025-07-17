import requests
from bs4 import BeautifulSoup

def parse_github_repo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    name = soup.find("strong", {"itemprop": "name"})
    description = soup.find("p", {"class": "f4 my-3"})
    author = soup.find("span", {"class": "author"})

    return {
        "name": name.text.strip() if name else "",
        "description": description.text.strip() if description else "",
        "author": author.text.strip() if author else "",
        "github": url,
        "paper": ""
    }
