from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pandas as pd
from google.cloud import storage  # Import the Google Cloud Storage library
import os  # Import the os module
import pandas as pd
from google.cloud import storage
import io

        

class Scraper:
    def __init__(self, region_website):
        self.region_website = region_website
        self.driver = self.setup_driver()

    def setup_driver(self):
        options = Options()
        options.headless = True
        # options.add_argument('--headless')
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Firefox(options=options)

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    def scrape_data(self):
        data_list = []

        self.driver.get(self.region_website)
        self.driver.implicitly_wait(10)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Dynamically obtain the last page number from the website
        last_page_element = self.driver.find_element(By.XPATH, '//*[@id="content"]/div[7]/div/div/div[1]/div[17]/div/div/ul/li[5]/a')
        last_page = int(last_page_element.get_attribute('innerHTML').strip())

        for page_num in range(1, 4 + 1):
            data_list = []
            current_url = f'{self.region_website}?p[page]={page_num}'
            self.driver.get(current_url)
            self.driver.implicitly_wait(10)
            self.scroll_to_bottom()

            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.find_all('div', class_='col-md col-sm-12 d-flex pl-md-0 pt-md-2 pb-md-1 advertisement-item--content')
            
            for property in elements:
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
                
                try:
                    price = property.find_all('div', class_="advertisement-item--content__price col-auto pl-0 pl-md-3 pr-0 text-right mt-2 mt-md-0 align-self-end")
                    price = price[0]['data-adv-price']
                except AttributeError:
                    price = None

                current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

                data_list.append({'street': street, 'title': title, 'type': type, 'size': size, 'price': price, 'page_num': page_num, 'current_datetime': current_datetime})
                df = pd.DataFrame(data_list)

                # Save the DataFrame to Google Cloud Storage
            self.save_to_storage(df, page_num)

        self.driver.quit()
        return "done"  # Return the DataFrame for further processing

    def save_to_storage(self, df, page_num):
        # Set the Google Cloud credentials
        # os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'real-estate-scraping-411119-6de86518de2c.json'

        # Initialize the Google Cloud Storage client
        client = storage.Client()
        bucket = client.get_bucket('real-estate-scraping')

        # Upload the DataFrame to the "temp" folder within the "bratislava" folder
        blob = bucket.blob(f'bratislava/temp/{page_num}.csv')
        blob.upload_from_string(df.to_csv(index=False), content_type='text/csv')
        
        
def merge_dataframes(bucket_name, folder_prefix):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=f'{folder_prefix}/temp/'))

    dfs = [pd.read_csv(io.BytesIO(blob.download_as_bytes())) for blob in blobs if blob.name.endswith('.csv')]
    combined_df = pd.concat(dfs, ignore_index=True)

    # Upload the combined DataFrame to Google Cloud Storage
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    blob = bucket.blob(f'{folder_prefix}/merged_file_{current_datetime}.csv')
    blob.upload_from_string(combined_df.to_csv(index=False), content_type='text/csv')

    # Delete the files from the "temp" folder within the specified folder
    for blob in bucket.list_blobs(prefix=f'{folder_prefix}/temp/'):
        blob.delete()


region_website = 'https://www.nehnutelnosti.sk/bratislava/'
scraper_instance = Scraper(region_website)
df = scraper_instance.scrape_data()

# Call the function to merge the scraped data
merge_dataframes('real-estate-scraping', 'bratislava')
