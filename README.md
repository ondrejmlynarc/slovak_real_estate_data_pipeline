# Real Estate Data Scraper

This Python script utilizes Selenium and BeautifulSoup to scrape real estate data from a specific website in Slovakia. The data is then stored in a CSV file and uploaded to Google Cloud Storage.

## Usage

Install the required Python libraries by running:

```bash
pip install selenium beautifulsoup4 tqdm pandas google-cloud-storage


Download the appropriate webdriver for Firefox and set the path in the script:

webdriver_path = r'C:\path\to\your\webdriver\geckodriver.exe'


Modify the region_website variable to the desired real estate website:
````bash
region_website = 'https://www.nehnutelnosti.sk/bratislava/'

Run the script to initiate the scraping process:

```bash
python your_script_name.py

Dependencies
- selenium
- beautifulsoup4
- tqdm
- pandas
- google-cloud-storage
