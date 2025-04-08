# version : 1.5

# This is a simple Flask web application that allows users to input a URL and start page number for scraping.


from flask import Flask, render_template, request, send_from_directory, redirect, url_for, flash
import os
from scraper import run_scraper

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'outputs'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        start_page = int(request.form.get('start_page') or 1)

        try:
            filename = run_scraper(url, start_page)
            flash('✅ Scraping complete!', 'success')
            return redirect(url_for('download', filename=filename))
        except Exception as e:
            flash(f'❌ Error: {str(e)}', 'danger')

    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
