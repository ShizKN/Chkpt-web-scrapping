import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse


def get_and_parse_html(wikipedia_url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(wikipedia_url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def extract_article_title(soup: BeautifulSoup) -> str:
    title_tag = soup.find("h1", id="firstHeading")
    if title_tag:
        span = title_tag.find("span", class_="mw-page-title-main")
        if span:
            return span.get_text(strip=True)
        return title_tag.get_text(strip=True)
    if soup.title:
        return soup.title.string.split(" - Wikipedia")[0].strip()
    return "Unknown Title"


def extract_article_text(soup: BeautifulSoup) -> dict:
    content_div = soup.find("div", id="mw-content-text")
    if not content_div:
        return {}
    parser_output = content_div.find("div", class_="mw-parser-output")
    content = parser_output if parser_output else content_div

    sections = {}
    current_heading = "Introduction"
    current_paragraphs = []

    for element in content.find_all(["h2", "h3", "p"]):
        if element.name in ["h2", "h3"]:
            if current_paragraphs:
                sections[current_heading] = current_paragraphs[:]
                current_paragraphs = []
            headline_span = element.find("span", class_="mw-headline")
            current_heading = (
                headline_span.get_text(strip=True)
                if headline_span
                else element.get_text(strip=True).replace("[edit]", "").strip()
            )
        elif element.name == "p":
            para_text = element.get_text(strip=True)
            if para_text:
                current_paragraphs.append(para_text)

    if current_paragraphs:
        sections[current_heading] = current_paragraphs[:]

    return sections


def collect_internal_links(soup: BeautifulSoup, wikipedia_url: str) -> list:
    parsed = urlparse(wikipedia_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    links = set()

    content_div = soup.find("div", id="mw-content-text")
    if content_div:
        parser_output = content_div.find("div", class_="mw-parser-output")
        content = parser_output if parser_output else content_div

        for a_tag in content.find_all("a", href=True):
            href = a_tag["href"]
            clean_href = href.split("#")[0].split("?")[0]
            if re.match(r"^/wiki/[^:]+$", clean_href):
                full_link = base + clean_href
                if full_link != wikipedia_url:  
                    links.add(full_link)

    return sorted(list(links))


def wikipedia_data_extraction(wikipedia_url: str) -> dict:
    soup = get_and_parse_html(wikipedia_url)
    title = extract_article_title(soup)
    sections = extract_article_text(soup)
    internal_links = collect_internal_links(soup, wikipedia_url)

    return {
        "title": title,
        "sections": sections,         
        "internal_links": internal_links  
    }


if __name__ == "__main__":
    test_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    print(f"Testing on: {test_url}\n")
    
    result = wikipedia_data_extraction(test_url)
    
    print(f"TITLE: {result['title']}")
    print(f"NUMBER OF SECTIONS: {len(result['sections'])}")
    print("\nFIRST 3 SECTIONS (showing heading + number of paragraphs):")
    for i, (heading, paragraphs) in enumerate(result["sections"].items()):
        if i >= 3:
            break
        print(f"  • {heading} → {len(paragraphs)} paragraphs")
    
    print(f"\nNUMBER OF INTERNAL WIKIPEDIA LINKS: {len(result['internal_links'])}")
    print("SAMPLE INTERNAL LINKS (first 5):")
    for link in result["internal_links"][:5]:
        print(f"  • {link}")
    
    print("\nTest completed successfully!")
