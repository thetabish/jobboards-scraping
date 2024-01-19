import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time

current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"akad_job_postings_{current_date_time}.txt"

baseurl = 'https://karriere.akad.de/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.133'
}

r = requests.get(baseurl, headers=headers)
soup = BeautifulSoup(r.content, 'html.parser')

joblist = soup.find_all('div', class_='joboffer_container')

job_data = []

for item in joblist:
    link = item.find('a', href=True)
    location = item.find('div', class_='joboffer_informations joboffer_box').text.strip()
    job_link = link['href']

    # Introduce a delay before making the next request
    time.sleep(2) 

    r = requests.get(job_link, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    job_name = soup.find('h1').text.strip()
    description = soup.find('div', class_='scheme-content scheme-margin scheme-introduction').text.strip()


    tasks = soup.find('div', class_='scheme-content scheme-margin scheme-task').find('div', class_='content_text').ul
    if tasks:
    
        task_items = [li.text.strip() for li in tasks.find_all('li')]
    else:
        task_items = []

    profile = soup.find('div', class_='scheme-content scheme-margin scheme-profile').find('div', class_='content_text').ul
    if profile:
        profile_items = [li.text.strip() for li in profile.find_all('li')]
    else:
        profile_items = []

    job_data.append({'Name': job_name, 'Location': location, 'Description': description, 'Tasks': task_items, 'Profile': profile_items, 'Link': job_link})

# Create a DataFrame
df = pd.DataFrame(job_data)

# Save to a file with well-formatted content
with open(file_name, 'w', encoding='utf-8') as file:
    file.write(f"Scraped Job Postings - {current_date_time}\n\n")

    for index, row in df.iterrows():
        file.write(f"{index + 1}. Job Title: {row['Name']}\n")
        file.write(f"   Location: {row['Location']}\n")
        file.write(f"   Description:\n   {row['Description']}\n")
        
        file.write(f"   Tasks:\n")
        for task_item in row['Tasks']:
            file.write(f"      - {task_item}\n")
        
        file.write(f"   Profile:\n")
        for profile_item in row['Profile']:
            file.write(f"      - {profile_item}\n")

        file.write(f"   Link: {row['Link']}\n\n")
