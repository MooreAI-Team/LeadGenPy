from Configs import config
from Configs.chatgpt_config import client
import json
import re
import time
import requests
from bs4 import BeautifulSoup


class Evaluator:

    # This method fetches the page and returns a structured summary with metadata signals GPT needs
    # to evaluate mobile-friendliness, title/meta quality, and page bloat.
    def _fetch_website_content(self, website):
        self._raw_html = ""
        if website == "null":
            return ""
        try:
            url = website if website.startswith("http") else f"https://{website}"
            resp = requests.get(url, timeout=config.request_timeout, headers={"User-Agent": "Mozilla/5.0"})
            self._raw_html = resp.text

            soup = BeautifulSoup(resp.text, 'lxml')
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "(none)"

            meta_desc = soup.find('meta', attrs={'name': lambda n: n and n.lower() == 'description'})
            meta_desc_text = meta_desc.get('content', '').strip() if meta_desc else "(none)"
            viewport = soup.find('meta', attrs={'name': lambda n: n and n.lower() == 'viewport'})
            viewport_text = viewport.get('content', '').strip() if viewport else "(none)"
            script_count = len(soup.find_all('script'))
            img_count = len(soup.find_all('img'))

            # extract copyright from raw HTML before tags are stripped
            copyright_match = re.search(r'(?:\©|&copy;|Copyright)\s*(\d{4})', resp.text, re.I)
            copyright_year = copyright_match.group(1) if copyright_match else "(not found in HTML)"

            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            body_text = soup.get_text(separator=" ", strip=True)[:3000]

            return (
                f"<title>: {title_text}\n"
                f"<meta description>: {meta_desc_text}\n"
                f"<meta viewport>: {viewport_text}\n"
                f"Copyright year in HTML: {copyright_year}\n"
                f"Script tags: {script_count}, Image tags: {img_count}\n\n"
                f"Page text sample:\n{body_text}"
            )
        except Exception as e:
            print(f"[LOG] Could not fetch {website}: {e}")
            return ""

    def evaluate(self, website, rating):
        print(f"[LOG] Evaluating: {website}")

        website_content = self._fetch_website_content(website)
        if website_content:
            context = f"Website URL: {website}\n\n{website_content}"
        else:
            context = f"Website URL: {website}\n\n(Website could not be loaded, inferring from URL only)"

        # retry once so we don't lose all data points. if it fails twice, we'll just return nulls.
        response = None
        for attempt in range(2):
            try:
                response = client.chat.completions.create(model="gpt-5.4-mini", messages=[{"role": "user", "content": f"""Inspect this business website and return ONLY valid JSON. No markdown, no explanation.

{context}

For each rule, return true only if the issue clearly applies. Return false if it clearly does not apply. If unsure, return null.

Rules to check:
- No website
- Website does not load
- No HTTPS
- Not mobile friendly
- Old copyright year
- No contact form
- No clear call-to-action
- Poor title/meta description
- Looks like old Wix/Weebly/GoDaddy template

Return exactly this JSON structure:

{{
    "No website": null,
    "Website does not load": null,
    "No HTTPS": null,
    "Not mobile friendly": null,
    "Old copyright year": null,
    "No contact form": null,
    "No clear call-to-action": null,
    "Poor title/meta description": null,
    "Looks like old Wix/Weebly/GoDaddy template": null
}}"""}])
                break
            except Exception as e:
                print(f"[LOG] GPT attempt {attempt + 1} failed: {e}")
                if attempt == 0:
                    time.sleep(config.delay)
                else:
                    raise

        # strip markdown fences if GPT wrapped the JSON (which it shouldn't have, but just in case)
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

        evaluation_dict = json.loads(raw)
        priority = self.calculate_priority(evaluation_dict, rating)
        return priority, evaluation_dict

    # sums rule scores; +10 bonus if rating is below 3.0
    def calculate_priority(self, evaluation_result, rating):
        priority_score = 0
        for rule, applies in evaluation_result.items():
            if applies:
                priority_score += config.Rule_dict.get(rule, 0)
        try:
            if float(rating) < 3.0:
                priority_score += 10
        except (ValueError, TypeError):
            pass
        return priority_score


### ====================== ###
### === GETTER METHODS === ###
### ====================== ###

    # checks both whether a URL exists and whether it actually loaded

    def get_website_exists(self, website):
        if website == 'null':
            return 'No'
        if self._raw_html:
            return 'Yes'
        return 'No'  # URL present but fetch failed

    # prefers mailto: links, falls back to regex with noise filtering
    def get_email(self):
        if not self._raw_html:
            return "null"
        # I found mailto: links to be the most reliable source
        mailto = re.findall(r'href=["\']mailto:([^"\'?]+)', self._raw_html, re.I)
        if mailto:
            return mailto[0].strip()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', self._raw_html)
        noise = {'noreply', 'no-reply', 'example', 'schema', 'w3', 'sentry', 'domain'}
        for email in emails:
            domain = email.split('@')[1].split('.')[0].lower()
            if domain not in noise:
                return email
        return "null"

    # looks for owner/founder name patterns in the website body text
    def get_owner_contact(self):
        if not self._raw_html:
            return "null"
        soup = BeautifulSoup(self._raw_html, 'lxml')
        for tag in soup(['script', 'style']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        match = re.search(r'(?:Owner|Founder|Proprietor|President|CEO)[\s:,]+([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)', text)
        return match.group(1) if match else "null"

    def get_https(self, evaluation):
        value = evaluation.get("No HTTPS")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_mobile_friendly(self, evaluation):
        value = evaluation.get("Not mobile friendly")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_copyright(self, evaluation):
        value = evaluation.get("Old copyright year")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_contact_form(self, evaluation):
        value = evaluation.get("No contact form")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_booking_quote_cta(self, evaluation):
        value = evaluation.get("No clear call-to-action")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_title_meta_description(self, evaluation):
        value = evaluation.get("Poor title/meta description")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"

    def get_looks_original_unique(self, evaluation):
        value = evaluation.get("Looks like old Wix/Weebly/GoDaddy template")
        if value is True:
            return "No"
        if value is False:
            return "Yes"
        return "null"
