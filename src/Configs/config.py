import os
from dotenv import load_dotenv
load_dotenv()

# Headers for the google sheet where the lead data will be stored.
headers = [
    "BusinessName", "Category", "City", "Phone", "Email", "Address",
    "Website", "GoogleMapsLink", "Priority", "OwnerContactPerson",
    "Rating", "WebsiteExists", "HTTPS", "MobileFriendly",
    "CurrentCopyright", "HasContactForm",
    "HasBookingQuoteCTA", "GoodTitleMetaDescription",
    "LooksOriginalAndUnique", "OutreachStatus"
]

# Ruleset for ranking the leads based on their website quality and other factors.
Rule_dict = {
    "No website": 50,
    "Website does not load": 45,
    "No HTTPS": 20,
    "Not mobile friendly": 25,
    "Old copyright year": 10,
    "No contact form": 15,
    "No clear call-to-action": 15,
    "Poor title/meta description": 10,
    "Looks like old Wix/Weebly/GoDaddy template": 15
}

# project root, no need to worry about this, it will be resolved dynamically from this file's location
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# set DEV_MODE=true in .env to run with visible browser, capped at 5 results. DO NOT CHANGE IT HERE!
DEV = os.getenv("DEV_MODE", "true").lower() == "true"

# Timing constants (change depending on your network speed)
delay = 3               # sleep after an error before retrying
delay_scroll = 1.5      # between scroll attempts in scroll_content
delay_page_load = 2     # after clicking "More results" button
delay_between_visits = 1  # between visiting each business page
request_timeout = 10    # HTTP requests timeout (evaluator + email fetch)
wait_feed = 15          # WebDriverWait for the Maps feed to appear
wait_page = 10          # WebDriverWait for business page h1 to appear

# categories for MooreAI mode — add/remove as needed
all_business_categories = [
    "Restaurant",
    "Cafe",
    "Retail Store",
    "Fitness Center",
    "Salon",
    "Auto Repair Shop",
    "Law Firm",
    "Accounting Firm",
    "Real Estate Agency",
    "Medical Clinic"
]

# in DEV, only run the first 2 to keep test runs short
if DEV:
    all_business_categories = all_business_categories[:2]


# JSON structure for storing the business data
business_data = {
    "BusinessName": "null",
    "Category": "null",
    "City": "null",
    "Phone": "null",
    "Email": "null",
    "Address": "null",
    "Website": "null",
    "GoogleMapsLink": "null",
    "Priority": "null",  # will be generated based on the score calculated in the evaluation module
    "OwnerContactPerson": "null",  # will be extracted in the future based on the website content
    "Rating": "null",
    "WebsiteExists": "null",  # YES or NO field, will be generated based on the website field
    "HTTPS": "null",  # YES or NO field, will be generated based on the website field
    "MobileFriendly": "null",  # YES or NO field, will be generated based on the website field
    "CurrentCopyright": "null",  # YES or NO field, will be generated based on the website field
    "HasContactForm": "null",  # YES or NO field, will be generated based on the website field
    "HasBookingQuoteCTA": "null",  # YES or NO field, will be generated based on the website field
    "GoodTitleMetaDescription": "null",  # YES or NO field, will be generated based on the website field
    "LooksOriginalAndUnique": "null",  # YES or NO field, will be generated based on the website field
    "OutreachStatus": "null"  # to be filled manually in the google sheet after the outreach process
}
