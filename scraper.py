
import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://internshala.com"
OUTPUT_DIR = "outputs"
COMPANY_DATA = {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
}


def fetch_html(url: str) -> str:
    """Fetch raw HTML from the given URL."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text)


def get_number(text: str) -> int:
    match = re.search(r'\d+', text)
    return int(match.group()) if match else 0

def safe_text(soup, selector, default="N/A"):
    tag = soup.select_one(selector)
    return tag.text.strip() if tag else default

def parse_job_page(relative_url: str) -> dict:
    full_url = BASE_URL + relative_url
    html = fetch_html(full_url)
    soup = BeautifulSoup(html, "html.parser")

    
    company_name = soup.select_one("a.company-name").text.strip()
    title        = soup.select_one("h1.job-title").text.strip()
    location     = soup.select_one("div.job-location").text.strip()
    salary       = soup.select_one("div.salary-range").text.strip()
    description  = soup.select_one("div.job-description").text.strip()
    

    return {
        "company_name": company_name,
        "job_title": title,
        "location": location,
        "salary": salary,
        "description": description,
        "page_url": full_url
    }

def parse_company_page(relative_url: str) -> dict:
    if not relative_url.startswith("/"):
        print(f"Invalid company link: {relative_url}")
        return {}

    full_url = BASE_URL + relative_url
    print(f"🔍 Scraping: {full_url}")

    try:
        html = fetch_html(full_url)
        soup = BeautifulSoup(html, "html.parser")

        # company_name = soup.select_one("div.company_name p").text.strip()
        company_tag = soup.select_one("div.company a.link_display_like_text")
        # company_name = company_tag.text.strip() if company_tag else "Unknown"
        # company_name = safe_text(soup, "div.company p.company-name", default="Unknown")
        company_name = safe_text(soup, "div.company a.link_display_like_text", default="Unknown")


        if not company_tag:
            print("⚠️ Company name not found. Dumping part of HTML for debugging...")
            print(soup.select_one("div.company"))


        website = soup.select_one("div.website_link a")
        website = website["href"] if website else ""

        about = soup.select_one("div.about_company_text_container")
        about = about.text.strip() if about else ""

        activity_section = soup.select("div.activity_container .activity")
        candidates_hired = opportunities_posted = 0
        hiring_since = ""

        for item in activity_section:
            text = item.text.strip()
            if "hired" in text:
                candidates_hired = get_number(text)
            elif "posted" in text:
                opportunities_posted = get_number(text)
            else:
                hiring_since = text

        location = soup.select_one("#location_names span")
        location = location.text.strip() if location else ""

        applied = soup.select_one(".applications_message")
        candidates_applied = get_number(applied.text) if applied else 0

        # jd_container = soup.select_one("div.internship_details .text-container")
        # job_description = jd_container.text.strip() if jd_container else ""
        jd_container = soup.select_one("div.text-container.job_description")
        job_description = jd_container.text.strip() if jd_container else ""


        skills = [s.text for s in soup.select("div.round_tabs_container span.round_tabs")]

        payout_container = soup.select_one(".salary_container, .stipend_container")
        payout_type = payout = ""
        if payout_container:
            payout_type = payout_container.select_one(".item_heading span").text.strip()
            payout = payout_container.select_one(".item_body span").text.strip()

        duration_tag = soup.find(string=lambda t: "duration" in t.lower())
        duration = ""
        if duration_tag:
            try:
                duration = duration_tag.find_parent("div").find("div", class_="item_body").text.strip()
            except:
                pass

        return {
            "company_name": company_name,
            "website": website,
            "about": about,
            "candidates_hired": candidates_hired,
            "opportunities_posted": opportunities_posted,
            "hiring_since": hiring_since,
            "job_description": job_description,
            "skills": ", ".join(skills),
            "candidates_applied": candidates_applied,
            "location": location,
            "payout_type": payout_type,
            "payout": payout,
            "duration": duration,
            "page_url": full_url
        }
    except Exception as e:
        print(f"❌ Error parsing company page: {e}")
        return {}


def scrape_page(url: str, page_number: int):

    print(f"\n📄 Scraping page {page_number}")
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    with open(f"debug-page-{page_number}.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())

    # listings = soup.select(f"#internship_list_container_{page_number} .individual_internship")
    listings = soup.find_all("div", class_="individual_internship")


    if not listings:
        print("⚠️ No internship listings found. Structure may have changed.")
        with open("debug-listing.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        return

    print(f"✅ Found {len(listings)} listings")

    for internship in listings:
        # anchor = internship.select_one(".button_container_card a")
        # link = anchor.get("href") if anchor else None
        anchor = internship.find("a", class_="job-title-href")
        link = anchor.get("href") if anchor else None


        if not link:
            print("⚠️ Skipping listing: No link found")
            continue

        if link.startswith("/internship/"):
            data = parse_company_page(link)
        elif link.startswith("/jobs/"):
            data = parse_job_page(link)
        else:
            continue

        if data:
            COMPANY_DATA[data["company_name"]] = data



def save_to_excel(data: list, filename: str):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    path = os.path.join(OUTPUT_DIR, filename)
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    print(f"\n📁 Data saved to {path}")


def get_total_pages(url: str) -> int:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    try:
        return int(soup.select_one("#total_pages").text.strip())
    except:
        raise ValueError("Unable to determine total page count. DOM structure may have changed.")









def run_scraper(base_url: str, start_page: int = 1) -> str:
    total_pages = get_total_pages(base_url)
    for page in range(start_page, total_pages + 1):
        paginated_url = f"{base_url}/page-{page}"
        scrape_page(paginated_url, page)
    
    if COMPANY_DATA:
        filename = slugify("Internshala Analytics Jobs") + ".xlsx"
        save_to_excel(list(COMPANY_DATA.values()), filename)
        return filename
    else:
        raise ValueError("No data scraped.")
