#   Date: 02-04-2024
#   Version: 1.1
#   Fixes: URL construction, error handling, and updated selectors

import requests
import re
import pandas as pd
import os
from bs4 import BeautifulSoup

HOST = 'https://internshala.com'
OUTPUTS_DIR = 'outputs'
COMPANIES_MAP = {}

def handleRequests(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
    try:
        response = requests.get(query, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Request failed for {query}: {str(e)}")
        return None

def getSoup(data):
    return BeautifulSoup(data, "html.parser") if data else None

def slugify(s, separator='-'):
    s = re.sub(r'[^\w\s-]', '', s.lower().strip())
    return re.sub(r'[\s_-]+', separator, s)

def get_number_from_text(text):
    return re.findall(r'\d+', text)[0] if text and re.findall(r'\d+', text) else 0

def scrape_company_data(url):
    try:
        page = handleRequests(url)
        if not page:
            return None
            
        soup = getSoup(page)
        if not soup:
            return None

        # Updated selectors based on current Internshala layout
        company_header = soup.find('div', class_='company-header')
        if not company_header:
            return None

        data = {
            "company_name": "N/A",
            "website": "N/A",
            "about": "N/A",
            "candidates_hired": 0,
            "opportunities_posted": 0,
            "hiring_since": "N/A",
            "job_description": "N/A",
            "skills": [],
            "candidates_applied": 0,
            "location": "N/A",
            "payout_type": "N/A",
            "payout": "N/A",
            "duration": "N/A",
            "page_url": url
        }

        # Company name
        name_tag = company_header.find('h1', class_='company-name')
        if name_tag:
            data['company_name'] = name_tag.get_text(strip=True)

        # Website
        website_tag = soup.find('a', class_='website_link')
        if website_tag and 'href' in website_tag.attrs:
            data['website'] = website_tag['href']

        # About
        about_tag = soup.find('div', class_='about_company_text_container')
        if about_tag:
            data['about'] = about_tag.get_text(strip=True)

        # Activity metrics
        activity_tags = soup.find_all('div', class_='activity')
        for tag in activity_tags:
            text = tag.get_text(strip=True)
            if 'hired' in text:
                data['candidates_hired'] = get_number_from_text(text)
            elif 'posted' in text:
                data['opportunities_posted'] = get_number_from_text(text)
            elif 'hiring since' in text.lower():
                data['hiring_since'] = text.replace('Hiring since', '').strip()

        # Job details
        details_container = soup.find('div', class_='internship_details')
        if details_container:
            # Job description
            jd_tag = details_container.find('div', class_='text-container')
            if jd_tag:
                data['job_description'] = jd_tag.get_text(strip=True)
            
            # Skills
            skills_tags = details_container.find_all('span', class_='round_tabs')
            data['skills'] = [tag.get_text(strip=True) for tag in skills_tags]

        # Location
        location_tag = soup.find('span', id='location_names')
        if location_tag:
            data['location'] = location_tag.get_text(strip=True)

        # Applications
        apps_tag = soup.find('div', class_='applications_message')
        if apps_tag:
            data['candidates_applied'] = get_number_from_text(apps_tag.get_text())

        # Payout
        stipend_tag = soup.find('div', class_='stipend_container')
        if stipend_tag:
            data['payout_type'] = stipend_tag.find('div', class_='item_heading').get_text(strip=True)
            data['payout'] = stipend_tag.find('div', class_='item_body').get_text(strip=True)

        # Duration
        duration_tag = soup.find('div', class_='other_detail_item', string=re.compile('duration', re.I))
        if duration_tag:
            data['duration'] = duration_tag.find_next('div', class_='item_body').get_text(strip=True)

        return data

    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def scrape_listing_page(url, page_num):
    print(f"\nScraping page {page_num}")
    page_content = handleRequests(url)
    if not page_content:
        return False

    soup = getSoup(page_content)
    container_id = f'internship_list_container_{page_num}'
    container = soup.find('div', id=container_id)
    
    if not container:
        print(f"Container {container_id} not found")
        return False

    internships = container.find_all('div', class_='individual_internship')
    print(f"Found {len(internships)} internships")

    for idx, internship in enumerate(internships, 1):
        try:
            link_tag = internship.find('a', class_='view_detail_button')
            if not link_tag or 'href' not in link_tag.attrs:
                continue

            # FIX 1: Construct full URL
            relative_path = link_tag['href']
            full_url = urllib.parse.urljoin(HOST, relative_path)
            
            company_data = scrape_company_data(full_url)
            if company_data and company_data['company_name'] != 'N/A':
                COMPANIES_MAP[company_data['company_name']] = company_data
                print(f"Scraped ({idx}/{len(internships)}): {company_data['company_name']}")
            else:
                print(f"Failed to scrape internship {idx}")

        except Exception as e:
            print(f"Error processing internship {idx}: {str(e)}")

    return True

def main(base_url):
    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)

    # Get total pages
    first_page = handleRequests(base_url)
    if not first_page:
        print("Failed to fetch initial page")
        return

    soup = getSoup(first_page)
    pagination = soup.find('div', id='pagination')
    total_pages = int(pagination.find('span', id='total_pages').get_text(strip=True)) if pagination else 1
    print(f"Total pages detected: {total_pages}")

    # Scrape all pages
    for page in range(1, total_pages + 1):
        page_url = f"{base_url}page-{page}/" if page > 1 else base_url
        if not scrape_listing_page(page_url, page):
            break

    # Export data
    if COMPANIES_MAP:
        df = pd.DataFrame(COMPANIES_MAP.values())
        filename = slugify(base_url.split('/')[-2] if base_url.endswith('/') else base_url.split('/')[-1]) + '.xlsx'
        output_path = os.path.join(OUTPUTS_DIR, filename)
        df.to_excel(output_path, index=False)
        print(f"\nSuccessfully exported {len(df)} records to {output_path}")
    else:
        print("\nNo data collected")

if __name__ == '__main__':
    target_url = input("Enter Internshala search URL: ").strip()
    if not target_url.startswith(HOST):
        print("Please provide a valid Internshala URL")
    else:
        main(target_url)