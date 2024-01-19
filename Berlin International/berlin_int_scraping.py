import requests
from bs4 import BeautifulSoup
import io
import pdfquery
from datetime import datetime
import time

baseurl = 'https://www.berlin-international.de/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.133'
}

url = 'https://www.berlin-international.de/hochschule/stellenangebote/'

r = requests.get(url, headers=headers)
soup = BeautifulSoup(r.content, 'html.parser')

job_postings = []

job_content = soup.find('div', class_='col-lg-12 col-md-12 col-sm-12 col-xs-12 del-padding page-content link-effect')

if job_content:
    job_list = job_content.find_all('li')

    for job in job_list:
        job_title = job.a.text.strip()
        job_link = baseurl + job.a['href'].strip()
        time.sleep(2) 
        # Extract content from the linked PDF
        pdf_response = requests.get(job_link)
        pdf_file = io.BytesIO(pdf_response.content)

        pdf = pdfquery.PDFQuery(pdf_file)
        pdf.load()

        text_content = pdf.tree.xpath('//text()')
        pdf_text = ' '.join(text_content)

        job_postings.append({'Title': job_title, 'Link': job_link, 'Description': pdf_text})

# Save to a file
current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"berlin_international_job_postings_{current_date_time}.txt"

with open(file_name, "w", encoding="utf-8") as file:
    file.write(f"Scraped Job Postings - {current_date_time}\n\n")

    for job in job_postings:
        file.write(f"Job Title: {job['Title']}\n")
        file.write(f"Link: {job['Link']}\n")
        file.write("Description:\n") 
        formatted_pdf_text = '\n'.join(['    ' + line for line in job['Description'].split('\n')])
        file.write(f"{formatted_pdf_text}\n")

        file.write(" " + "\n")