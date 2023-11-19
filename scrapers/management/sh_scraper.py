import logging

from playwright.sync_api import ElementHandle, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .shared.base_scraper import BaseScraper

logger = logging.getLogger("django")


class SHScraper(BaseScraper):
    def __init__(self, job_title: str):
        selectors = {
            "link": "a[href*='/job/']",
            "title": '[data-testid="viewJobTitle"]',
            "content": '[data-testid="viewJobBodyJobFullDescriptionContent"]',
        }
        query_params = {"q": f'"{job_title}"', "t": 7}
        super().__init__(
            job_title,
            "https://www.simplyhired.com/search",
            selectors,
            query_params,
            self.sh_next_page_logic,
        )

    def format_link(self, vacancy: ElementHandle):
        return f"https://www.simplyhired.com{vacancy.get_attribute('href').split('?')[0]}"

    def sh_next_page_logic(self, page: Page, page_number: int):
        try:
            next_page_selector = f'[data-testid="paginationBlock{page_number}"]'
            next_page_link = page.locator(next_page_selector)

            if next_page_link.count() > 0:
                next_page_link.scroll_into_view_if_needed()
                page.wait_for_selector(next_page_selector, state="visible", timeout=5000)
                page.click(next_page_selector)

                active_page_selector = f'{next_page_selector}[aria-current="true"]'
                page.wait_for_selector(active_page_selector, state="attached", timeout=5000)
                return True
            else:
                return False
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout error while navigating to next page: {page_number}.")
            return False
        except Exception as e:
            logger.error(f"Error navigating to next page: {page_number}.", exc_info=e)
            return False
