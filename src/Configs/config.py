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
page_load_timeout = 30  # Chrome page load timeout — gives up and moves on if a page hangs

# categories for MooreAI mode — add/remove as needed
all_business_categories = [
    # Home services, usually high value leads
    "Roofing Contractor",
    "Plumbing Company",
    "Electrical Contractor",
    "HVAC Contractor",
    "Landscaping Company",
    "Lawn Care Service",
    "Snow Removal Service",
    "General Contractor",
    "Home Remodeling Contractor",
    "Kitchen Remodeler",
    "Bathroom Remodeler",
    "Flooring Contractor",
    "Painting Contractor",
    "Concrete Contractor",
    "Fence Contractor",
    "Deck Builder",
    "Garage Door Company",
    "Window Installation Service",
    "Siding Contractor",
    "Pest Control Service",
    "Cleaning Service",
    "Carpet Cleaning Service",
    "Mold Remediation Service",
    "Water Damage Restoration Service",
    "Fire Damage Restoration Service",

    # Medical, wellness, and appointment-based businesses
    "Dental Clinic",
    "Orthodontist",
    "Chiropractor",
    "Physical Therapy Clinic",
    "Massage Therapist",
    "Medical Spa",
    "Skin Care Clinic",
    "Mental Health Clinic",
    "Counseling Center",
    "Optometrist",
    "Veterinary Clinic",
    "Urgent Care Clinic",

    # Beauty and personal care
    "Salon",
    "Hair Salon",
    "Barber Shop",
    "Nail Salon",
    "Spa",
    "Tanning Salon",
    "Tattoo Shop",
    "Piercing Studio",

    # Auto and vehicle services
    "Auto Repair Shop",
    "Auto Body Shop",
    "Car Detailing Service",
    "Tire Shop",
    "Oil Change Service",
    "Car Wash",
    "Towing Service",
    "Used Car Dealer",
    "Motorcycle Dealer",
    "RV Dealer",

    # Professional services
    "Law Firm",
    "Accounting Firm",
    "Tax Preparation Service",
    "Insurance Agency",
    "Real Estate Agency",
    "Property Management Company",
    "Financial Advisor",
    "Marketing Agency",
    "Consulting Firm",
    "Business Broker",

    # Food and hospitality
    "Restaurant",
    "Cafe",
    "Bakery",
    "Catering Service",
    "Food Truck",
    "Ice Cream Shop",
    "Coffee Shop",
    "Hotel",
    "Motel",
    "Event Venue",
    "Wedding Venue",

    # Fitness, recreation, and training
    "Fitness Center",
    "Gym",
    "Yoga Studio",
    "Pilates Studio",
    "Dance Studio",
    "Martial Arts School",
    "Personal Trainer",
    "Sports Training Facility",

    # Education and childcare
    "Daycare Center",
    "Preschool",
    "Tutoring Service",
    "Driving School",
    "Music School",
    "Language School",

    # Local retail with service angle
    "Retail Store",
    "Furniture Store",
    "Mattress Store",
    "Jewelry Store",
    "Florist",
    "Gift Shop",
    "Boutique",
    "Pet Store",
    "Bike Shop",
    "Hardware Store",

    # Events and creative services
    "Photographer",
    "Videographer",
    "Wedding Photographer",
    "DJ Service",
    "Event Planner",
    "Party Rental Service",
    "Printing Service",
    "Sign Shop",

    # Trades and B2B services
    "Machine Shop",
    "Welding Shop",
    "Security System Installer",
    "IT Service Company",
    "Commercial Cleaning Service",
    "Janitorial Service",
    "Staffing Agency",
    "Moving Company",
    "Storage Facility"
]

# all_business_categories = [
#     "Restaurant",
#     "Cafe",
#     "Retail Store",
#     "Fitness Center",
#     "Salon",
#     "Auto Repair Shop",
#     "Law Firm",
#     "Accounting Firm",
#     "Real Estate Agency",
#     "Medical Clinic"
# ]

# Temporary: resume from "Daycare Center" for the Fargo run. delete this line when starting fresh for other locations
# all_business_categories = all_business_categories[all_business_categories.index("Daycare Center"):]

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
