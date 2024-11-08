import requests
from bs4 import BeautifulSoup
import os
#selenium stuff here
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

USER = os.environ.get('USER', 'test')
PASS = os.environ.get('PASS', 'test')


def send_metric(job_name, metric_name, value, help_text, metric_type, pushgateway_url='http://localhost:9091'):
    data = (
        f"# HELP {metric_name} {help_text}\n"
        f"# TYPE {metric_name} {metric_type}\n"
        f"{metric_name} {value}\n"
    )
        
    response = requests.post(
        f"{pushgateway_url}/metrics/job/{job_name}",
        data=data,
        headers={'Content-Type': 'text/plain'}
    )
    
    if response.status_code == 202 or response.status_code == 200 :
        print("Metric sent successfully.")
    else:
        print(f"Failed to send metric: {response.status_code} {response.text}")



loginURL = ('https://www.resume-library.com/hiring/login')
keywords = 'IT'
#keywords = 'blablabla' 
#keywords = 'blebleblee' 
checkURL = (f'https://www.resume-library.com/client/resume-search/results?csrf_rl=6d31e39e4dfccf07bb50568b87d4c2e8&enc=&saved_search_id=&sort=&hidden-per-page=&advanced_search=0&search_builder=0&popular_search_id=&id=&recipients=&name=&frequency=daily&keywords={keywords}&keywords_exclude=%5B%22sales%22%5D&national=true&lat=&lon=&salary_from=&salary_to=&job_type%5B%5D=any&updated_on=4+months&education_level%5B%5D=any&work_experience%5B%5D=any&submt_btn=1')


#selenium stuff here
# Configurar opções do Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # do not open browser
chrome_options.add_argument('--no-sandbox')  # needed by docker
chrome_options.add_argument('--disable-dev-shm-usage')  # avoid sharing memory
chrome_options.add_argument('--disable-gpu') # performance
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)



driver.get(loginURL)
#time.sleep(1)
# wait the page being loaded
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'user')))

driver.find_element(By.NAME, 'user').send_keys(USER)
driver.find_element(By.NAME, 'pass').send_keys(PASS)
time.sleep(1)
driver.find_element(By.NAME, 'pass').send_keys(Keys.RETURN)



driver.get(checkURL)
#time.sleep(1)

#WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'resume-search-displaying-left')))


#print(driver.page_source)

soup = BeautifulSoup(driver.page_source, 'html.parser')

result_container = soup.find('div', class_='resume-search-displaying-left')
if result_container:
    matched_number = result_container.text.split("of")[-1].strip()
#    print(f"Resumes matched: {matched_number}")
    if 'Displaying 0 Resumes matched' in matched_number:
        print("error")
        print(matched_number)
        result = int_value = int(''.join(filter(str.isdigit, matched_number)))
    else:
        print("passed")
        print(matched_number)
        result = int_value = int(''.join(filter(str.isdigit, matched_number)))

print(result)


driver.save_screenshot('screenshot.png')
#time.sleep(1)
driver.quit()


send_metric(
    job_name='synthetix',
    metric_name='synthetix_rl_hiring_results',
    value=result,
    help_text='Synthetix check to gather the results on rl/hiring',
    metric_type='gauge'
)
