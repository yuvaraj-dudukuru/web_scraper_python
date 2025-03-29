

#   Date: 02-04-2024
#   Version: 1.0

#   Description: This script scrapes internship data from Internshala's website, extracting company details and job post information.
#   It utilizes BeautifulSoup and requests libraries for web scraping, organizing data into a pandas DataFrame, and exporting it to an Excel file.
#   The script supports pagination and offers flexibility to specify start and stop page numbers for scraping.


import requests, io, re, pandas, os
from bs4 import BeautifulSoup
import urllib.parse

HOST = 'https://internshala.com'

OUTPUTS_DIR = 'outputs'
COMPANIES_MAP = {}

def handleRequests(query):
    '''Returns HTML document'''

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"}
    try:
        request = requests.get(query, headers=headers, allow_redirects=False)
        return request.text
    except Exception:
        raise ConnectionError("Error occured while fetching data from the web, please try checking the internet connection.")

def getSoup(data):
    '''Returns parsed Soup Object from html text'''
    return BeautifulSoup(data, "html.parser")

def slugify(s, separator='-'):
  s = s.lower().strip()
  s = re.sub(r'[^\w\s-]', '', s)
  s = re.sub(r'[\s_-]+', separator, s)
  s = re.sub(r'^-+|-+$', '', s)
  return s

def get_number_from_text(text):
    found = re.findall(r'\d+', text)
    if len(found):
        return found[0]
    
    return 0

def scrape_company_data(url):
    url = HOST + url
    page = handleRequests(url)
    page_content = getSoup(page)

    company_name = str(page_content.find('div', attrs={'class': 'company_name'}).p.text).strip()
    website = page_content.find('div', attrs={'class': 'website_link'})
    about = page_content.find('div', attrs={'class':'about_company_text_container'})

    candidates_hired = 0
    opportunities_posted = 0
    hiring_since = ''

    activities = page_content.find('div', attrs={'class': 'activity_container'})
    jd_details = page_content.find('div', attrs={'class': 'internship_details'})
    other_details = page_content.find('div', attrs={'class': 'internship_other_details_container'})
    location = page_content.find(attrs={'id': 'location_names'}).find('span')
    applied_candidates = page_content.find('div', attrs={'class': 'applications_message'}).text

    jd = str(jd_details.find('div', attrs={'class': 'text-container'}).text).strip()
    skills = jd_details.find('div', attrs={'class': 'round_tabs_container'})
    if skills:
        skills = skills.find_all('span', attrs={'class': 'round_tabs'})
        skills =  [skill.text for skill in skills]
    else:
        skills = []

    payout_container = page_content.find('div', attrs={'class': 'salary_container'})
    if not payout_container:
        payout_container = page_content.find('div', attrs={'class': 'stipend_container'})
        
    payout_type = str(payout_container.find('div', attrs={'class': 'item_heading'}).find('span').text).strip()
    payout = str(payout_container.find('div', attrs={'class': 'item_body'}).find('span').text).strip()

    duration = ''
    _duration = other_details.find(string=lambda text: 'duration' in text.lower())
    if _duration:
        if _duration.parent.parent.parent:
            _duration = _duration.parent.parent.parent
            duration = str(_duration.find(attrs={'class': 'item_body'}).text).strip()

    if website:
        website = website.a['href']
    
    if location:
        location = str(location.text).strip()

    if about:
        about = str(about.text).strip()
    else:
        about = ''

    if activities:
        activities = activities.select('.activity')
    else:
        activities = []

    for activity in activities:
        activity = str(activity.text).strip()

        if 'hired' in activity:
            candidates_hired = get_number_from_text(activity)
        elif 'posted' in activity:
            opportunities_posted = get_number_from_text(activity)
        else:
            hiring_since = activity

    return {
        "company_name": company_name, "website": website, 
        "about": about, "candidates_hired": candidates_hired, "opportunities_posted": opportunities_posted, 
        "hiring_since": hiring_since, "job_description": jd, "skills": ', '.join(skills),
        "candidates_applied": get_number_from_text(applied_candidates),
        "location": location, "payout_type": payout_type, "payout":  payout, "duration": duration,
        "page_url": url
    }
    

def scrape(link, page=1):
    data = handleRequests(link)
    soup = getSoup(data)

    results = soup.find('div', attrs={'id': 'internship_list_container_' + str(page)}).find_all('div', attrs={'class': 'individual_internship'})
    
    print(f'Found a total of {len(results)} results on this page.' + (' \n' if results else ' Skipping... \n'))
    if not results:
        return
    
    count = 1
    total = len(results)

    for each in results:
        btn = each.find('div', attrs={'class': 'button_container_card'})
        if not btn:
            pass
        else:
            link = btn.a['href']
            data = scrape_company_data(link)
            company_name = data['company_name']
            
            if not company_name in COMPANIES_MAP:
                COMPANIES_MAP[company_name] = data

        print(f'Scraping: {count}/{total} completed', end='\r')
        count += 1


def main(url='', start=1, stop=1):
    page_url = url
    filename = str(url).strip().split('/')
    if not url.endswith('/'):
        url = url + '/'
        
    if not filename[-1]:
        filename = filename[-2]
    else:
        filename = filename[-1]

    for x in range(start, stop):
        page = x
        print(f'Scraping data in page: {page}')

        page_url = '{}page-{}'.format(url, str(page))
        scrape(link=page_url, page=page)

    companies = []
    for company_key in COMPANIES_MAP:
        companies.append(COMPANIES_MAP[company_key])

    filename = slugify(filename) + '.xlsx'
    file_path = os.path.join(OUTPUTS_DIR, filename)

    print('Process completed. Writing it to ' +  filename)

    if not os.path.exists(OUTPUTS_DIR):
        os.makedirs(OUTPUTS_DIR)

    df = pandas.DataFrame(companies)
    df.to_excel(file_path, index=False, header=True)

if __name__ == '__main__':
    target_url = str(input('Input target page url: '))

    home_page = handleRequests(target_url);
    home_page_content = getSoup(home_page)
    total_pages = home_page_content.find('div', attrs={'id': 'pagination'}).find('div', attrs={'class': 'page_number'}).find('span', attrs={'id': 'total_pages'}).get_text(" ", strip=True)
    total_pages = int(total_pages)
    print(f'Found a total of {total_pages} pages')

    start = input('Enter start page number (default is 1 - first page): ')
    start = int(start) if start else 1

    main(url=target_url, start=start, stop=(total_pages + 1))