import re
import time
import traceback
from bs4 import BeautifulSoup
from Configs.selenium_config import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from WebScrapper.store import Store
from Configs import config
from Evaluation.evaluator import Evaluator


class Scrappers:

    # This function is the main function that will be called to start the scraping process. It takes the business category and location as input and performs the following steps:

    # 1. It sets up the query based on the user input and opens the google maps page with the search results based on the query.
    # 2. It scrolls the results list to load more items, loads up to 120 items based on the scroll and the "More results" button.
    # 3. It extracts all business links from the page and visits each business page to extract details.

    def scrape(self, business_category, location):
        try:
            print(f"[LOG] Scraping: {business_category} in {location}")

            scrapeDetail = ScrapeDetails()
            store = Store()
            ev = Evaluator()

            # Setup query based on the user input.
            query = f'{business_category} in {location}' if business_category and location else business_category

            # This will open the google maps page with the search results based on the query.
            driver.get(f'https://www.google.com/maps/search/{query}')

            # Scroll the results list to load more items. usually limit is around 120 items based on the scroll and the "More results" button.
            self.scroll_content()

            # Extract all business links from the page
            links = self.extract_links()

            total = min(len(links), 5) if config.DEV else len(links)
            count = 0

            print(f"[LOG] {total} businesses to process\n")

            # Visit each business page and extract details
            for link in links:
                if config.DEV and count == 5:
                    break

                # skip if already in the JSON from a previous run
                if store.is_duplicate(link):
                    print(f"[LOG] Skipping duplicate")
                    continue

                print(f"\n[{count + 1}/{total}] ----------------------------------------")
                try:
                    soup, business_data = self.extract_details(link, scrapeDetail)

                    # website and rating must be set before evaluate() so the priority score is accurate
                    business_data["Website"] = scrapeDetail.get_website(soup)
                    business_data["Rating"] = scrapeDetail.get_rating(soup)

                    priority, evaluation = ev.evaluate(business_data["Website"], business_data["Rating"])

                    business_data["BusinessName"] = scrapeDetail.get_business_name(soup)
                    business_data["Category"] = scrapeDetail.get_category(soup)
                    business_data["City"] = location
                    business_data["Phone"] = scrapeDetail.get_phone(soup)
                    business_data["Email"] = ev.get_email()  # reuses the HTML already fetched in the evaluate() method
                    business_data["Address"] = scrapeDetail.get_address(soup)
                    business_data["GoogleMapsLink"] = link
                    business_data["Priority"] = priority
                    business_data["OwnerContactPerson"] = ev.get_owner_contact()
                    business_data["WebsiteExists"] = ev.get_website_exists(business_data["Website"])
                    business_data["HTTPS"] = ev.get_https(evaluation)
                    business_data["MobileFriendly"] = ev.get_mobile_friendly(evaluation)
                    business_data["CurrentCopyright"] = ev.get_copyright(evaluation)
                    business_data["HasContactForm"] = ev.get_contact_form(evaluation)
                    business_data["HasBookingQuoteCTA"] = ev.get_booking_quote_cta(evaluation)
                    business_data["GoodTitleMetaDescription"] = ev.get_title_meta_description(evaluation)
                    business_data["LooksOriginalAndUnique"] = ev.get_looks_original_unique(evaluation)
                    business_data["OutreachStatus"] = "null"

                    name = business_data.get("BusinessName", "Unknown")
                    print(f"[DONE] {name} | Priority: {priority}")

                    row = [business_data.get(key, "null") for key in config.headers]
                    store.insert_one_row([row])
                    store.append_to_json(business_data)
                    print("[LOG] Saved to sheet + JSON")
                    count += 1
                except Exception:
                    # one bad page shouldn't kill the whole category — log and move on
                    traceback.print_exc()
                    print("[LOG] Skipping business due to error above")
                    try:
                        driver.execute_script("window.stop()")  # unblock Chrome if it's mid-load
                    except Exception:
                        pass

                time.sleep(config.delay_between_visits)

            print(f"\n[LOG] Done -- {count} businesses processed")
            time.sleep(config.delay)

        except Exception:
            # category-level failure (Maps navigation, scroll, or extract_links) — log and move on
            traceback.print_exc()
            print(f"[LOG] Category failed, skipping: {business_category}")
            time.sleep(config.delay)

    def scroll_content(self):
        feed = WebDriverWait(driver, config.wait_feed).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[role="feed"]')))
        prev_count = 0

        while True:
            feed.send_keys(Keys.END)
            time.sleep(config.delay_scroll)

            # end of list signal
            if driver.find_elements(By.XPATH, "//*[contains(text(), 'reached the end')]"):
                break
            # "More results" button
            more_btn = driver.find_elements(By.XPATH, "//button[contains(@jsaction, 'pane.paginationSection')]")
            if more_btn:
                more_btn[0].click()
                time.sleep(config.delay_page_load)

            # stop if the feed stopped growing
            new_items = driver.find_elements(By.CSS_SELECTOR, '[role="feed"] > div')
            if len(new_items) == prev_count:
                break
            prev_count = len(new_items)

        print("[LOG] Page loaded")

    def extract_links(self):
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Business links inside the feed all point to /maps/place/
        res = soup.select('[role="feed"] a[href*="/maps/place/"]')

        # deduplicate, preserve order
        links = list(dict.fromkeys(link.attrs['href'] for link in res))
        print(f"[LOG] Found {len(links)} listings")
        return links

    def extract_details(self, link, scrapeDetail):
        driver.get(link)
        try:
            WebDriverWait(driver, config.wait_page).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')))
        except Exception:
            print("[LOG] WARNING: page may not have fully loaded")
        soup = BeautifulSoup(driver.page_source, 'lxml')
        business_data = scrapeDetail.initialize_data()
        return soup, business_data


class ScrapeDetails:

    def initialize_data(self):
        return config.business_data.copy()


### ====================== ###
### === GETTER METHODS === ###
### ====================== ###

    @staticmethod
    def get_business_name(soup):
        try:
            el = soup.find('h1')
            return el.text.strip() if el else "null"
        except Exception as error:
            print(error)
            return "null"

    @staticmethod
    def get_category(soup):
        try:
            # using jsaction for category
            el = soup.find('button', {'jsaction': re.compile(r'category', re.I)})
            return el.text.strip() if el else "null"
        except Exception as error:
            print(error)
            return "null"

    @staticmethod
    def get_phone(soup):
        try:
            el = soup.find('button', {'aria-label': re.compile(r'^Phone:', re.I)})
            if el:
                label = el.get('aria-label', '')
                return label[len('Phone: '):].strip() or "null"
            return "null"
        except Exception as error:
            print(error)
            return "null"

    @staticmethod
    def get_address(soup):
        try:
            el = soup.find(attrs={'data-item-id': 'address'})
            if el:
                label = el.get('aria-label', '')
                return label.replace('Address: ', '').strip() or "null"
            return "null"
        except Exception as error:
            print(error)
            return "null"

    @staticmethod
    def get_website(soup):
        try:
            el = soup.find('a', {'data-item-id': re.compile(r'^authority')})
            if el:
                return el.get('href', '').strip() or "null"
            return "null"
        except Exception as error:
            print(error)
            return "null"

    @staticmethod
    def get_rating(soup):
        try:
            el = soup.find(attrs={'aria-label': re.compile(r'[\d.]+ stars', re.I)})
            if el:
                match = re.search(r'([\d.]+)\s+stars', el.get('aria-label', ''), re.I)
                return match.group(1) if match else "null"
            return "null"
        except Exception as error:
            print(error)
            return "null"
