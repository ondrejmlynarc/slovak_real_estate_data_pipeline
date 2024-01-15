from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
from tqdm import tqdm
import csv
from io import StringIO
from google.cloud import storage


class Scraper:
    def __init__(self, region_website):
        self.region_website = region_website
        self.driver = self.setup_driver()
        self.output_file = self.generate_output_file()

    def generate_output_file(self):
        # Extract the last part of the URL (what follows the last "/")
        region_name = self.region_website.rsplit('/', 2)[-2]
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f'{region_name}_{current_date}.csv'

    def setup_driver(self):
        options = Options()
        options.headless = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Firefox(options=options)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    def scrape_data(self, filename = 'scraped_data'):

        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f'{filename}_{current_date}.csv'

        data_list = []

        csv_data = StringIO()
        csv_writer = csv.writer(csv_data)

        # Check if the file is empty (write header if it is)
        if csv_data.tell() == 0:
            csv_writer.writerow(['street', 'title', 'type', 'size', 'current_datetime'])

        # with open(self.output_file, mode='w', newline='', encoding='utf-8') as file:
        #     csv_writer = csv.writer(file)
        #     csv_writer.writerow(['street', 'title', 'type', 'size', 'current_datetime'])

        self.driver.get(self.region_website)
        self.driver.implicitly_wait(10)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        last_page = self.driver.find_element(By.XPATH,'//*[@id="content"]/div[7]/div/div/div[1]/div[17]/div/div/ul/li[5]/a').get_attribute('innerHTML').strip()

        # Use tqdm to create a progress bar
        # for page_num in tqdm(range(1, int(last_page) + 1), desc="Scraping Pages"):
        for page_num in tqdm(range(1, 3), desc="Scraping Pages"):
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

                # # Write product details to the CSV file
                # csv_writer.writerow([street, title, type, size, current_datetime])

                # append the results to a dataframe
                # data_list.append({'title': title, 'street': street, 'type': type,
                #                   'current_datetime': current_datetime})
                csv_writer.writerow([street, title, type, size, current_datetime])

        # df = pd.DataFrame(data_list)
        csv_data.seek(0)
        csv_content = csv_data.read()
        self.driver.quit()
        return csv_content


# Assuming you have defined the Scraper class and webdriver_path
webdriver_path = r'C:\webdrivers\chromedriver.exe'
region_website = 'https://www.nehnutelnosti.sk/bratislava/'

# Create an instance of the Scraper class
scraper_instance = Scraper(region_website)
csv_data = scraper_instance.scrape_data()

# Define the blob path (including the folder) and filename
bucket_name = 'real_estate_scraping'
current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
blob_path = f'bratislava/scrape-{current_datetime}.csv'


# Upload the CSV data as a blob to the GCS bucket's root
def upload_csv_to_bucket(bucket_name, blob_path, csv_data):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        blob.upload_from_string(csv_data, content_type='text/csv')
        print("CSV file uploaded successfully to Google Cloud Storage.")
    except Exception as e:
        print(f"An error occurred while uploading the CSV file: {str(e)}")

# Upload the CSV data to the root of the specified bucket
upload_csv_to_bucket(bucket_name, blob_path, csv_data)