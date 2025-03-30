import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Fetch the webpage
req = requests.get("https://internshala.com/internships/analytics-internship-in-hyderabad")
soup = BeautifulSoup(req.text, 'html.parser')

# Step 2: Find the internship listings
internship_list = soup.find_all('div', class_='internship_meta')

# Step 3: Extract data and store it in a list of dictionaries
data = []
for internship in internship_list:
    internship_data = {
        "Title": internship.find('h3').get_text(strip=True) if internship.find('h3') else "N/A",
        "Company": internship.find('a', class_='link_display_like_text').get_text(strip=True) if internship.find('a', class_='link_display_like_text') else "N/A",
        "Location": internship.find('a', class_='location_link').get_text(strip=True) if internship.find('a', class_='location_link') else "N/A",
        "Stipend": internship.find('span', class_='stipend').get_text(strip=True) if internship.find('span', class_='stipend') else "N/A",
        "Duration": internship.find('div', class_='item_body').get_text(strip=True) if internship.find('div', class_='item_body') else "N/A"
    }
    data.append(internship_data)

# Step 4: Create a DataFrame from the extracted data
df = pd.DataFrame(data)

# Step 5: Save the data to an Excel file
df.to_excel("internship_data.xlsx", index=False)

print("Data saved to internship_data.xlsx")
