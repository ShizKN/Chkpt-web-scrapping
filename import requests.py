import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_html(url):
    return BeautifulSoup(requests.get(url).text, 'html.parser')

def get_title(soup):
    return soup.find('h1', id='firstHeading').text.strip()

def get_content(soup):
    data, current_h = {"Introduction": []}, "Introduction"
    for tag in soup.select('.mw-parser-output > *'):
        if tag.name in ['h2', 'h3', 'h4']:
            current_h = tag.text.replace('[edit]', '').strip()
            data[current_h] = []
        elif tag.name == 'p' and tag.text.strip():
            data[current_h].append(tag.text.strip())
    return {k: "\n".join(v) for k, v in data.items() if v}

def get_links(soup, base_url):
    return list({urljoin(base_url, a['href']) for a in soup.select('a[href^="/wiki/"]') if ':' not in a['href']})

def scrape_wiki(url):
    soup = get_html(url)
    return {
        "title": get_title(soup),
        "content": get_content(soup),
        "links": get_links(soup, url)
    }

if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    print(f"Scraping {url}...\n")
    result = scrape_wiki(url)
    print(f"Title: {result['title']}")
    print(f"Headings Found: {list(result['content'].keys())[:5]}...") 
    print(f"Intro snippet: {result['content']['Introduction'][:150]}...")
    print(f"Total Internal Links: {len(result['links'])}")
    print(f"Link Example: {result['links'][0]}")