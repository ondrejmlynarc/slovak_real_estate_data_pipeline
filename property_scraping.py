from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By  # Importing the By module for locating elements

options = Options()
driver_path = "C:/Drivers/chromedriver-win64/chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

driver.get('https://www.nehnutelnosti.sk/bratislava/')
driver.implicitly_wait(10)


# Find all elements with similar structure using contains in XPath
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
elements = soup.find_all('div', class_='col-md col-sm-12 d-flex pl-md-0 pt-md-2 pb-md-1 advertisement-item--content')

for property in elements[:2]:
    address = property.find('div', class_="advertisement-item--content__info d-block text-truncate").get('title')
    print(address)
    title = property.find('h2', class_="mb-0 d-none d-md-block").text
    print(title)
    size = property.find('div', class_="advertisement-item--content__info")
    print(size)
element = soup.select_one(
    '#adv-5329008 > div > div.col-md.col-sm-12.d-flex.pl-md-0.pt-md-2.pb-md-1.advertisement-item--content > div > div.w-100.order-last.order-md-first > div.my-2.mt-md-2.mb-md-1.mt-xl-3.mb-xl-2 > div:nth-child(2) > img')
print(element)
driver.quit()
