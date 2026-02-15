from exceptions import JobScrapingError
from logger import logger
from scraper import scrape_linkedin_job


class JobService:
    @staticmethod
    def scrape_job(url: str) -> str:
        """Scrapes job description from a URL with logging and error handling."""
        if not url:
            return ""

        try:
            logger.info(f"Attempting to scrape job from: {url}")
            content = scrape_linkedin_job(url)
            if not content:
                logger.warning(f"Scraper returned empty content for URL: {url}")
                return ""

            logger.info(f"Successfully scraped {len(content)} characters from {url}")
            return content
        except Exception as e:
            logger.error(f"Error scraping job from {url}: {str(e)}")
            raise JobScrapingError(f"Failed to extract job details from the provided URL. Error: {str(e)}") from e
