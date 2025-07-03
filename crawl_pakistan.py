import requests
from bs4 import BeautifulSoup
import PyPDF2
from urllib.parse import urljoin, urlparse
import time
import re
import hashlib
from io import BytesIO
import os
import sys
from requests.exceptions import RequestException

# Increase recursion limit as a fallback
sys.setrecursionlimit(2000)

# Configuration
BASE_URLS = [
    "https://www.finance.gov.pk/",
    "https://fabs.gov.pk/",
    "http://www.pbs.gov.pk/"
]
OUTPUT_FILE = "pakistan_dataset.txt"
URLS_FILE = "scraped_urls.txt"
MIN_WORDS = 1000000
CRAWL_DELAY = 1  # Seconds between requests
ALLOWED_DOMAINS = [".gov.pk", ".edu.pk", ".gov", ".edu"]
USER_AGENT = "Mozilla/5.0 (compatible; AcademicCrawler/1.0)"
TEXT_FILTER = re.compile(r'(\bcopyright\b|\©|\(c\))', re.IGNORECASE)
CONTENT_BLOCKLIST = re.compile(r'(\bblog\b|\bnews\b|\barticle\b|\bpress release\b|\bpublication\b|\bposted by\b|\bread more\b)', re.IGNORECASE)
GENERIC_PHRASES = {"home", "contact us", "site map", "privacy policy", "read more", "posted by", "subscribe", "newsletter"}
SKIPPED_LOG = "skipped_content.log"
MAX_DEPTH = 10  # Limit recursion depth
SAVE_INTERVAL = 100000  # Save dataset every 100,000 words

# Initialize
visited_urls = set()
text_hashes = set()
word_count = 0
output_data = []
robots_cache = {}
skipped_urls = []
skipped_texts = []
scraped_urls = []

def log_skipped(reason, url=None, text_snippet=None):
    """Log skipped URLs or texts for debugging/reporting."""
    with open(SKIPPED_LOG, "a", encoding="utf-8") as f:
        if url:
            f.write(f"Skipped URL: {url} | Reason: {reason}\n")
            skipped_urls.append((url, reason))
        if text_snippet:
            f.write(f"Skipped Text: {text_snippet[:100]}... | Reason: {reason}\n")
            skipped_texts.append((text_snippet[:100], reason))

def log_scraped_url(url, description):
    """Log successfully scraped URLs with descriptions."""
    with open(URLS_FILE, "a", encoding="utf-8") as f:
        f.write(f"URL: {url} | Description: {description}\n")
    scraped_urls.append((url, description))

def save_dataset():
    """Save cleaned dataset to file."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for paragraph in output_data:
            f.write(paragraph + "\n")
    print(f"Saved dataset to {OUTPUT_FILE} with {word_count} words.")

def check_robots_txt(url):
    """Manually check robots.txt for disallow rules."""
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    robots_url = f"{base}/robots.txt"
    
    if robots_url in robots_cache:
        disallowed = robots_cache[robots_url]
    else:
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(robots_url, headers=headers, timeout=5)
            response.raise_for_status()
            disallowed = []
            for line in response.text.splitlines():
                line = line.strip().lower()
                if line.startswith("disallow:"):
                    path = line.split("disallow:")[1].strip()
                    if path:
                        disallowed.append(path)
            robots_cache[robots_url] = disallowed
        except:
            print(f"Failed to read robots.txt for {robots_url}, assuming open access")
            robots_cache[robots_url] = []
        disallowed = robots_cache[robots_url]
    
    path = parsed.path + ("?" + parsed.query if parsed.query else "")
    for disallow_path in disallowed:
        if path.startswith(disallow_path):
            return False
    return True

def clean_text(text):
    """Remove extra whitespace and short/irrelevant texts."""
    text = re.sub(r'\s+', ' ', text.strip())
    if len(text.split()) <= 10 or any(phrase in text.lower() for phrase in GENERIC_PHRASES) or CONTENT_BLOCKLIST.search(text):
        log_skipped("Short or blocked content (blog/news/article)", text_snippet=text)
        return ""
    return text

def extract_text_from_html(html, url):
    """Extract clean text from HTML, excluding navigation and footers."""
    if CONTENT_BLOCKLIST.search(url.lower()):
        log_skipped("URL contains blog/news/article", url=url)
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for elem in soup(["nav", "footer", "script", "style", "header"]):
        elem.decompose()
    text = soup.get_text(separator=" ", strip=True)
    if TEXT_FILTER.search(text) or CONTENT_BLOCKLIST.search(text):
        log_skipped("Copyrighted or blog/news/article content", text_snippet=text)
        return ""
    return clean_text(text)

def extract_text_from_pdf(url, content):
    """Extract text from PDF content using PyPDF2."""
    if CONTENT_BLOCKLIST.search(url.lower()):
        log_skipped("PDF URL contains blog/news/article", url=url)
        return ""
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text and not TEXT_FILTER.search(page_text) and not CONTENT_BLOCKLIST.search(page_text):
                text += page_text + " "
        return clean_text(text)
    except Exception as e:
        print(f"Error extracting PDF {url}: {e}")
        return ""

def is_valid_url(url, base_domain):
    """Check if URL is valid and within allowed domains."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(allowed in domain for allowed in ALLOWED_DOMAINS) and parsed.scheme in ["http", "https"]

def get_links(html, base_url):
    """Extract links from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        link = urljoin(base_url, a["href"])
        if is_valid_url(link, urlparse(base_url).netloc):
            links.add(link)
    return links

def crawl_url(url, depth=0):
    """Crawl a single URL and process HTML or PDF with depth limit."""
    global word_count
    if depth > MAX_DEPTH:
        log_skipped("Maximum recursion depth exceeded", url=url)
        return
    if url in visited_urls:
        return
    visited_urls.add(url)

    if not check_robots_txt(url):
        log_skipped("Blocked by robots.txt", url=url)
        return

    try:
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10, verify=True)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "").lower()
        is_pdf = "pdf" in content_type
        text = ""
        description = ""

        if is_pdf:
            text = extract_text_from_pdf(url, response.content)
            description = "Government or educational PDF (e.g., policy, report, or manual)"
        else:
            text = extract_text_from_html(response.text, url)
            description = "Government or educational webpage (e.g., policy, service description, or educational material)"

        if text:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash not in text_hashes:
                text_hashes.add(text_hash)
                paragraphs = [p for p in text.split("\n") if clean_text(p)]
                for para in paragraphs:
                    words = len(para.split())
                    if words > 10:
                        output_data.append(para)
                        word_count += words
                if paragraphs:  # Log URL only if content was added
                    log_scraped_url(url, description)
                print(f"Processed {url}: {len(paragraphs)} paragraphs, {word_count}/{MIN_WORDS} words")
                
                # Save dataset incrementally
                if word_count >= SAVE_INTERVAL * (word_count // SAVE_INTERVAL):
                    save_dataset()

        if not is_pdf and word_count < MIN_WORDS:
            links = get_links(response.text, url)
            for link in links:
                time.sleep(CRAWL_DELAY)
                crawl_url(link, depth + 1)

    except RequestException as e:
        print(f"Error crawling {url}: {e}")
        log_skipped(f"Request error: {e}", url=url)
    except Exception as e:
        print(f"Unexpected error crawling {url}: {e}")
        log_skipped(f"Unexpected error: {e}", url=url)

def main():
    """Main crawling function."""
    if os.path.exists(SKIPPED_LOG):
        os.remove(SKIPPED_LOG)
    if os.path.exists(URLS_FILE):
        os.remove(URLS_FILE)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)  # Remove old dataset to avoid confusion
    for base_url in BASE_URLS:
        if word_count >= MIN_WORDS:
            break
        crawl_url(base_url)
        time.sleep(CRAWL_DELAY)

    save_dataset()

if __name__ == "__main__":
    main()