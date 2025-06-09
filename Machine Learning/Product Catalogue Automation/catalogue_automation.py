import time
import re
import logging
from typing import Set, List, Tuple
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class Browser:
    """A class to interact with the web browser for scraping."""
    
    def __init__(self, driver_path: str = None, timeout: int = 10):
        """
        Initializes the Browser object with options and settings.

        :param driver_path: Path to the Chrome WebDriver (default is None).
        :param timeout: Timeout for WebDriverWait in seconds (default is 10).
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

        self._chrome_options = Options()
        self._chrome_options.add_argument('--start-maximized')
        self._chrome_options.add_argument('--disable-extensions')
        self._chrome_options.add_argument('--headless')  # Uncomment for headless mode
        # self.chrome_options.add_argument('--disable-gpu')

        self._service = Service(driver_path)
        self._browser = webdriver.Chrome(options=self._chrome_options)
        
        self._timeout = timeout
        self._wait = WebDriverWait(self._browser, self._timeout)

    def _click_button(self, locator_type: str, locator_value: str) -> str:
        """Click a button based on the locator type and value."""
        try:
            self._wait.until(EC.element_to_be_clickable((getattr(By, locator_type), locator_value)))
            button = self._browser.find_element(getattr(By, locator_type), locator_value)
            button_text = button.text
            button.click()
            self._logger.info(f'Clicked on "{button_text}" button and navigated to {self._browser.current_url}')
        except Exception as e:
            self._logger.error(f'Failed to click the "{locator_value}" button. Error: {e}')
        return self._browser.current_url

    def _scrape_categories(self, url: str) -> Set[Tuple[str, str]]:
        """Scrape product categories from a given URL."""
        self._logger.info(f'Scraping categories from "{url}"')
        self._browser.get(url)
        base_url = self._browser.current_url.split('?')[0]
        categories = set()

        try:
            self._wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="productsMenuAnchor"]/div/div[2]/div[1]')))
            desktop_container = self._browser.find_element(By.XPATH, '//*[@id="productsMenuAnchor"]/div/div[2]/div[1]')
            category_elements = desktop_container.find_elements(By.CLASS_NAME, 'anchor')

            for element in category_elements:
                try:
                    a_tag = element.find_element(By.TAG_NAME, 'a')
                    category_name = a_tag.get_attribute('textContent').strip()
                    data_category = a_tag.get_attribute('data-category')
                    category_url = f"{base_url}?c={data_category}"

                    if category_name and category_url:
                        categories.add((category_name, category_url))
                except Exception as e:
                    self._logger.error(f"Error extracting category details: {e}")
        except Exception as e:
            self._logger.error(f"Failed to scrape categories from {url}. Error: {e}")

        return categories

    def _scrape_data(self, url: str, locator_value: str, regex: str) -> Set[Tuple[str, str]]:
        """Scrape data using a regular expression."""
        self._logger.info(f'Scraping data from "{url}"')
        desktop_container = self._browser.find_element(By.XPATH, locator_value)
        page_source: str = desktop_container.get_attribute('outerHTML')
        data_set = set()

        try:
            for match in re.findall(regex, page_source):
                data_set.add((match[0], match[1]))
        except Exception as e:
            self._logger.error(f"Error scraping data using regex: {e}")
        
        return data_set

    def save_to_excel(self, data: List[Tuple[str, str]], filename: str):
        """Save scraped data to an Excel file."""
        try:
            df = pd.DataFrame(data, columns=['Name', 'URL'])
            df.to_excel(filename, index=False, engine='openpyxl')
            self._logger.info(f'Data saved to "{filename}"')
        except Exception as e:
            self._logger.error(f"Error saving data to Excel: {e}")

    def close_browser(self):
        """Close the browser."""
        self._logger.info('Closing browser...')
        self._browser.quit()

    def open_page(self, url: str):
        """Open a page in the browser."""
        self._logger.info(f'Opening page: {url}')
        self._browser.get(url)


def scrape_product_categories(url: str, driver: Browser) -> List[Tuple[str, str]]:
    """Scrape product categories from the provided URL."""
    regex = r'<a.*data-category=\"(?P<data_category>[^\"]*).*?>(?P<text_content>.*?)</a>'
    locator_value = '//*[@id="productsMenuAnchor"]/div/div[2]'
    base_url: str = url.split('?')[0] + '?c='
    categories = driver._scrape_data(url, locator_value, regex)
    return [(category[1], base_url+category[0]) for category in categories]


def scrape_products(url: str, driver: Browser) -> List[Tuple[str, str]]:
    """Scrape product information from the provided category URL."""
    regex = r'<a.*?title=\"(?P<prod_title>[^\"]*).*?href=\"(?P<link>.*?)\">'
    locator_value = '//*[@id="productList"]'
    home_page = 'https://www.cattelanitalia.com/'
    products = driver._scrape_data(url, locator_value, regex)
    return [(product[0], home_page + product[1]) for product in products]


def main():
    url = 'https://www.cattelanitalia.com/'
    
    # Initialize the browser
    browser = Browser()

    # Open the main page
    browser.open_page(url)

    try:
        # Click necessary buttons for navigation (e.g., cookies, products menu)
        browser._click_button('XPATH', '//*[@id="cconsent-bar"]/div/div[2]/div/button')
        products_url = browser._click_button('XPATH', '//*[contains(text(), "Products")]')

        # Scrape product categories and products
        product_categories = scrape_product_categories(products_url, browser)
        # browser._logger.info(product_categories)

        # Process each product category
        for category_name, category_url in product_categories:
            _url = browser._click_button('XPATH', f'//*[contains(text(), "{category_name}")]')
            product_data = scrape_products(category_url, browser)
            browser.save_to_excel(product_data, f'{category_name}.xlsx')

    except Exception as e:
        browser._logger.error(f"An error occurred in the main workflow: {e}")

    finally:
        # Ensure the browser is closed after operations
        browser.close_browser()


if __name__ == '__main__':
    main()
