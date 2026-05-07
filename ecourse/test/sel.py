from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

service= Service(executable_path='../.venv/chromedriver.exe')
driver= webdriver.Chrome(service=service)
driver.get('https://vnexpress.net/')

articles=driver.find_elements(By.CSS_SELECTOR, '#automation_TV0 > article')

for article in articles:
    tittle = article.find_element(By.TAG_NAME, 'h3')
    print(tittle.text)
    print('----------')

driver.quit()