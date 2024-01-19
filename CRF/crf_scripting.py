import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager 
import time
from datetime import datetime

current_date_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"crf_job_postings_{current_date_time}.txt"


baseurl = 'https://karriere.crf-education.com/stellenangebote/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.133'
}

# Provide the correct path to msedgedriver executable
options = ChromeOptions()
options.add_argument("--headless=new")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--incognito')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) 
timeout = 10
wait = WebDriverWait(driver, timeout)

def get_shadow_root(element):
    return driver.execute_script('return arguments[0].shadowRoot', element)

driver.get(baseurl)
driver.maximize_window()
time.sleep(3)

# Accept cookies button
shadow_host = wait.until(EC.presence_of_element_located((By.ID, 'usercentrics-root')))
shadow_container = get_shadow_root(shadow_host).find_element(By.CSS_SELECTOR, '[data-testid=uc-app-container]')
WebDriverWait(shadow_container, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid=uc-accept-all-button]'))).click()
wait.until(EC.invisibility_of_element_located((By.ID, 'usercentrics-root')))
time.sleep(3)

jobname_list = []
joblink_list = []
location_list = [] 
department_list = []  
contract_type_list = []  
company_name_list = []  
tasks_list = []  
profile_list = []  

# Scraping job postings from all pages
while True:
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    joblist = soup.find_all('a', class_='joblist--item')

    for item in joblist:
        jobname = item.find('h3').text
        jobname_list.append(jobname)

        # Extracting link from each job list item
        joblink = item['href'] 
        joblink_list.append(joblink)

        print(jobname, joblink)

        # Visit each job link to extract information
        driver.get(joblink)
        time.sleep(3)  # Add a delay to ensure the page loads properly

        # Extracting information using BeautifulSoup
        try:
            soup_job_page = BeautifulSoup(driver.page_source, 'html.parser')

            # Extracting location information
            location_element = soup_job_page.find('span', class_='label', string='Standort')
            if location_element:
                job_location = location_element.find_next('span', class_='value').text
                location_list.append(job_location)
                print("Location:", job_location)
            else:
                print("Location element not found")
                location_list.append("N/A")

            # Extracting department information
            department_element = soup_job_page.find('span', class_='label', string='Abteilung')
            if department_element:
                job_department = department_element.find_next('span', class_='value').text
                department_list.append(job_department)
                print("Department:", job_department)
            else:
                print("Department element not found")
                department_list.append("N/A")

            # Extracting contract type information
            contract_type_element = soup_job_page.find('span', class_='label', string='Anstellungsart')
            if contract_type_element:
                job_contract_type = contract_type_element.find_next('span', class_='value').text
                contract_type_list.append(job_contract_type)
                print("Contract Type:", job_contract_type)
            else:
                print("Contract Type element not found")
                contract_type_list.append("N/A")

            # Extracting company name information
            company_name_element = soup_job_page.find('span', class_='label', string='Unternehmen')
            if company_name_element:
                job_company_name = company_name_element.find_next('span', class_='value').text
                company_name_list.append(job_company_name)
                print("Company Name:", job_company_name)
            else:
                print("Company Name element not found")
                company_name_list.append("N/A")

            # Extracting tasks information
            tasks_element = soup_job_page.find('h3', string='Was Sie erwartet')
            if tasks_element:
                tasks_text = '\n'.join([li.text for li in tasks_element.find_next('ul').find_all('li')])
                tasks_list.append(tasks_text)
                print("Tasks:", tasks_text)
            else:
                print("Tasks element not found")
                tasks_list.append("N/A")

            # Extracting profile information
            profile_element = soup_job_page.find('h3', string='Was Sie mitbringen')
            if profile_element:
                profile_text = profile_element.find_next('ul').text
                profile_list.append(profile_text)
                print("Profile:", profile_text)
            else:
                print("Profile element not found")
                profile_list.append("N/A")

        except Exception as e:
            print("Error extracting information:", str(e))
        # Go back to the main page to continue scraping other jobs
        driver.back()
        time.sleep(3) 

    #Go to the next page if available
    try:
        next_page = driver.find_element(By.XPATH, "//ul[@class='joblist--pagination']/li[@class='next']/a")
        next_page.click()
        time.sleep(3)  # Adjust the sleep time if needed
    except:
        print("No more pages available.")
        break
    
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(f"Scraped Job Postings - {current_date_time}\n\n")

        for index, job_name in enumerate(jobname_list):
            file.write(f"{index + 1}. Job Title: {job_name}\n")
            
            if index < len(joblink_list):
                file.write(f"   Link: {joblink_list[index]}\n")
            else:
                file.write("   Link: N/A\n")

            if index < len(location_list):
                file.write(f"   Location: {location_list[index]}\n")
            else:
                file.write("   Location: N/A\n")
            
            if index < len(department_list):
                file.write(f"   Department: {department_list[index]}\n")
            else:
                file.write("   Department: N/A\n")

            if index < len(contract_type_list):
                file.write(f"   Contract Type: {contract_type_list[index]}\n")
            else:
                file.write("   Contract Type: N/A\n")

            if index < len(company_name_list):
                file.write(f"   Company Name: {company_name_list[index]}\n")
            else:
                file.write("   Company Name: N/A\n")

            if index < len(tasks_list):
                file.write(f"   Tasks:\n")
                for task_item in tasks_list[index].split('\n'):
                    file.write(f"      - {task_item}\n")
            else:
                file.write("   Tasks: N/A\n")

            if index < len(profile_list):
                file.write(f"   Profile:\n")
                for profile_item in profile_list[index].split('\n'):
                    file.write(f"      - {profile_item}\n")
            else:
                file.write("   Profile: N/A\n")

            file.write("\n")

# Close the webdriver when done
        driver.quit()
