from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from tqdm import tqdm


class Scraper:
    def __init__(self, webdriver_path, region_website):
        self.region_website = region_website
        self.driver = self.setup_driver(webdriver_path)
        self.output_file = self.generate_output_file()

    def generate_output_file(self):
        # Extract the last part of the URL (what follows the last "/")
        region_name = self.region_website.rsplit('/', 2)[-2]
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f'{region_name}_{current_date}.csv'

    def setup_driver(self, webdriver_path):
        service = Service(webdriver_path)
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument("--blink-settings=imagesEnabled=false")
        return webdriver.Chrome(service=service, options=options)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    def scrape_data(self, filename = 'scraped_data'):

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f'{filename}_{current_date}.csv'

        with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['street', 'title', 'type', 'size', 'current_datetime'])

            self.driver.get(self.region_website)
            self.driver.implicitly_wait(10)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            last_page = self.driver.find_element(By.XPATH,'//*[@id="content"]/div[7]/div/div/div[1]/div[17]/div/div/ul/li[5]/a').get_attribute('innerHTML').strip()

            # Use tqdm to create a progress bar
            # for page_num in tqdm(range(1, int(last_page) + 1), desc="Scraping Pages"):
            for page_num in tqdm(range(1, 2), desc="Scraping Pages"):
                current_url = f'{self.region_website}?p[page]={page_num}'
                self.driver.get(current_url)
                self.driver.implicitly_wait(10)
                self.scroll_to_bottom()

                html = self.driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                elements = soup.find_all('div', class_='col-md col-sm-12 d-flex pl-md-0 pt-md-2 pb-md-1 advertisement-item--content')

                for property in elements:
                    if property:
                        try:
                            street = property.find_all('div', class_="advertisement-item--content__info d-block text-truncate")[0].get('title')
                        except AttributeError:
                            street = None

                        try:
                            title = property.find('h2', class_="mb-0 d-none d-md-block").text.strip()
                        except AttributeError:
                            title = None

                        try:
                            features = property.find_all('div', class_="advertisement-item--content__info")
                            type = features[1].text.split('•')[0].strip()
                        except AttributeError:
                            type = None

                        try:
                            size = features[1].find('span').text.strip()
                        except AttributeError:
                            size = None

                    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                    # Write product details to the CSV file
                    csv_writer.writerow([street, title, type, size, current_datetime])

        scraper_instance.driver.quit()


# Assuming you have defined the Scraper class and webdriver_path
webdriver_path = r'C:\webdrivers\chromedriver.exe'
region_website = 'https://www.nehnutelnosti.sk/bratislava/'

# Create an instance of the Scraper class
scraper_instance = Scraper(webdriver_path, region_website)
scraper_instance.scrape_data()

