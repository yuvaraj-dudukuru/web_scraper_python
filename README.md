# web_scraper_python
# version: 0.1.5
# 🕸️ Internshala Job/Internship Scraper (Flask Web App)

This project is a Flask-based web application that allows users to **scrape job or internship listings from [Internshala](https://internshala.com)** by simply providing a valid listing URL. The scraped data is automatically parsed and exported into a downloadable **Excel (.xlsx)** file with detailed information about each company or job post.

---

## 📌 Features

- 🔗 Accepts any **Internshala job/internship listing URL**
- 🌐 Web-based UI built with **Flask and HTML**
- 🧹 Scrapes data using **BeautifulSoup**
- 📊 Outputs clean, structured Excel files using **Pandas**
- 📁 Excel file is generated and served as a **downloadable file**
- 🐞 Includes debug files for troubleshooting any scraping issues

---

## 🚀 How It Works

1. You enter a valid Internshala job or internship URL (e.g., work-from-home analytics jobs).
2. The app scrapes all available pages starting from a given page (default: 1).
3. It parses important details such as:
   - Company Name  
   - Website  
   - Job Description  
   - Location  
   - Payout  
   - Duration  
   - Skills Required  
   - Number of Hires, Applicants, and more  
4. A clean Excel file is generated and available for **download**.

---

## 🧰 Tech Stack

- **Backend**: Flask (Python)
- **Scraping**: BeautifulSoup4 + Requests
- **Data Handling**: Pandas
- **Export**: Excel via OpenPyXL
- **Frontend**: HTML (Jinja2 Templates)

---

## 📁 Folder Structure

```
internshala_scraper/
├── app.py               # Flask application
├── scraper.py           # Scraper logic (modularized)
├── templates/
│   └── index.html       # Home page with input form
├── outputs/             # Folder for Excel files
├── requirements.txt     # Python dependencies
└── README.md            # You are here!
```

---

## 📦 Setup & Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yuvaraj-dudukuru/web_scraper_python.git
    cd internshala-scraper
    ```

2. **Create virtual environment (optional but recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask app**:
    ```bash
    python app.py
    ```

5. **Open your browser** and go to:
    ```
    http://127.0.0.1:5000/
    ```

---

## 📝 How to Use

1. Copy a valid URL from Internshala like:
    - `https://internshala.com/jobs/analytics-jobs/work-from-home`
    - `https://internshala.com/internships/data-science-internship`

2. Paste it in the form on the web page.

3. (Optional) Enter the start page (e.g., `2` to begin scraping from page 2 onward).

4. Submit the form. The app scrapes the data and gives you a downloadable Excel file.

---

## 📦 Output Example

The Excel file includes the following columns:

| Company Name | Website | About | Job Description | Skills | Location | Payout Type | Payout | Duration | Hired | Posted | Applied | Page URL |
|--------------|---------|-------|------------------|--------|----------|--------------|--------|----------|--------|--------|---------|----------|

---

## ⚠️ Disclaimer

This tool is made for educational purposes. Be mindful of Internshala's [Terms of Service](https://internshala.com/terms) before using it at scale. This tool is not affiliated with or endorsed by Internshala.

---

## 🙌 Credits

- Original Python script by [Yuvaraj](https://github.com/yuvaraj-dudukuru)
- Flask adaptation and UI integration by [ChatGPT + Yuvaraj]

---

## 📬 Want to Extend It?

Here are some ideas that i am thinking of:

- Add filters (e.g., skill-based, stipend-based)
- Deploy it on Render, Vercel (Flask), or Replit
- Add a dashboard using **Dash** or integrate with **Power BI**
