import logging

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .shared.base_scraper import BaseScraper

logger = logging.getLogger("django")


class HHScraper(BaseScraper):
    def __init__(self, job_title: str):
        selectors = {
            "link": "a[href*='hh.ru/vacancy']",
            "title": '[data-qa="vacancy-title"]',
            "content": '[data-qa="vacancy-description"]',
        }
        query_params = {"text": f'"{job_title}"', "search_period": 7, "ored_clusters": "true"}
        super().__init__(
            job_title,
            "https://hh.ru/search/vacancy",
            selectors,
            query_params,
            self.hh_next_page_logic,
        )

    def hh_next_page_logic(self, page: Page, page_number: int):
        try:
            wrapper_selector = (
                f'div[data-qa="pager-block"] > span[data-qa="pager-page-wrapper-{page_number}-{page_number - 1}"]'
            )

            next_page_selector = f'{wrapper_selector} > a[data-qa="pager-page"]'
            next_page_link = page.locator(next_page_selector)

            if next_page_link.count() > 0:
                next_page_link.scroll_into_view_if_needed()
                page.wait_for_selector(next_page_selector, state="visible", timeout=5000)
                page.click(next_page_selector)

                active_page_selector = f"{wrapper_selector} .bloko-button_pressed"
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
