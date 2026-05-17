<div align="center">
  <p>
      <img width="30%" src="https://i.imgur.com/vOWLuzY.png">
  </p>

  ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/selenium)
  ![License](https://img.shields.io/badge/License-MIT-blue.svg)

</div>

LeadGenPy scrapes business data from Google Maps, evaluates each website using GPT, scores each lead by quality, and saves results to Google Sheets and a local JSON file.

## What it does

For each business found on Google Maps, LeadGenPy:

1. Extracts name, category, phone, email, address, website, rating, and Maps link
2. Fetches the business website and sends the HTML to GPT for evaluation
3. Scores the lead based on website quality issues (no HTTPS, no mobile, old copyright, etc.)
4. Tries to find the owner/contact name from the website text
5. Saves everything to Google Sheets and `assets/data.json`

Data captured per business:

```json
{
    "BusinessName": "Sample Business",
    "Category": "Restaurant",
    "City": "Fargo",
    "Phone": "701-123-4567",
    "Email": "info@samplebusiness.com",
    "Address": "123 Main Street, Fargo, ND",
    "Website": "https://samplebusiness.com",
    "GoogleMapsLink": "https://www.google.com/maps/place/...",
    "Priority": 45,
    "OwnerContactPerson": "John Smith",
    "Rating": "3.8",
    "WebsiteExists": "Yes",
    "HTTPS": "Yes",
    "MobileFriendly": "No",
    "CurrentCopyright": "No",
    "HasContactForm": "No",
    "HasBookingQuoteCTA": "No",
    "GoodTitleMetaDescription": "Yes",
    "LooksOriginalAndUnique": "No",
    "OutreachStatus": "null"
}
```

## Modes

| Mode | Description |
|------|-------------|
| `1` | Single category extract — enter a category and location |
| `2` | MooreAI mode — runs all categories in `config.all_business_categories` for a given location |
| `0` | Exit |

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/MooreAI-Team/LeadGenPy.git
cd LeadGenPy
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your-openai-api-key
SPREADSHEET_ID=your-google-sheet-id
DEV_MODE=true
```

`DEV_MODE=true` opens a visible browser and caps results at 5 per run. Set to `false` for a full headless run.

### 4. Add your Google service account

Place your Google Sheets service account JSON file at:

```
assets/service_account.json
```

Make sure the service account has edit access to your spreadsheet.

### 5. Run

```bash
python src/main.py
```

ChromeDriver is managed automatically by Selenium, no need to download manually.

## Configuration

All tunable values live in `src/Configs/config.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `DEV` | reads `DEV_MODE` from `.env` | Visible browser + 5-result cap when true |
| `delay` | `3` | Sleep (seconds) after an error |
| `delay_scroll` | `1.5` | Pause between scroll attempts |
| `delay_page_load` | `2` | Pause after clicking "More results" |
| `delay_between_visits` | `1` | Pause between visiting each business page |
| `request_timeout` | `10` | HTTP timeout for website fetches |
| `wait_feed` | `15` | Selenium wait for Maps feed to appear |
| `wait_page` | `10` | Selenium wait for business page to load |
| `all_business_categories` | Categories used in MooreAI mode |

## Priority scoring

Each lead gets a priority score based on website issues found by GPT. Higher = worse website = better lead for outreach.

| Issue | Points |
|-------|--------|
| No website | 50 |
| Website does not load | 45 |
| Not mobile friendly | 25 |
| No HTTPS | 20 |
| No contact form | 15 |
| No clear call-to-action | 15 |
| Looks like old Wix/Weebly/GoDaddy template | 15 |
| Old copyright year | 10 |
| Poor title/meta description | 10 |
| Rating below 3.0 (bonus) | +10 |


---

This is a fork of the original [LeadGenPy](https://github.com/Wikkiee/LeadGenPy) project by [WikkiE](https://github.com/Wikkiee). All original work and credit belongs to him.
