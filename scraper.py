import requests
from bs4 import BeautifulSoup

# Step 1: Fetch the webpage
req = requests.get("https://internshala.com/internships/analytics-internship-in-hyderabad")
soup = BeautifulSoup(req.text, 'html.parser')

# Step 2: Find the internship listings
internship_list = soup.find_all('div', class_='internship_meta')

# Step 3: Create and write to an HTML file
with open("internship_list.html", "w", encoding="utf-8") as file:
    # Add a basic HTML structure
    file.write("<html><head><title>Internship List</title></head><body>\n")
    file.write("<h1>Internship Listings from Internshala</h1>\n")
    
    # Write each internship block to the file
    for internship in internship_list:
        file.write(str(internship) + "\n")
    
    # Close the HTML tags
    file.write("</body></html>")
    
print("Internship data saved to internship_list.html")
