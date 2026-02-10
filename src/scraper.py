from typing import Optional

import requests
from bs4 import BeautifulSoup


def scrape_linkedin_job(url: str) -> str:
    """
    Simple scraper for LinkedIn Job Descriptions.

    Args:
        url: The LinkedIn job posting URL.

    Returns:
        The extracted job description text or an error/warning message.
    """
    if not url.strip():
        return ""

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # LinkedIn often uses these classes for job descriptions in their public views
        # We try multiple common selectors
        description_selectors = [
            ("div", "description__text"),
            ("div", "show-more-less-html__markup"),
            ("section", "description"),
            ("div", "job-view-main-content"),
        ]

        description_div: Optional[BeautifulSoup] = None
        for tag, class_name in description_selectors:
            description_div = soup.find(tag, class_=class_name)
            if description_div:
                break

        if description_div:
            return description_div.get_text(separator="\n", strip=True)

        return "Could not find job description text on the page. You may need to paste it manually."

    except requests.exceptions.RequestException as e:
        return f"Network error scraping LinkedIn: {str(e)}"
    except Exception as e:
        return f"Unexpected error scraping LinkedIn: {str(e)}"
