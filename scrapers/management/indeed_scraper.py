import logging

from playwright.sync_api import ElementHandle, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from .shared.base_scraper import BaseScraper

logger = logging.getLogger("django")


# # NOTE: Disabled to test if it's still needed.
# # def check_subscription_popup(page: Page):
# #     # Checks and closes the subscription popup if present on the page.
# #     try:
# #         if page.is_visible("#popover-email-div", timeout=1000):
# #             page.click("#popover-x")
# #     except PlaywrightTimeoutError:
# #         # If there is no pop-up, do nothing and continue the flow.
# #         pass


class IndeedScraper(BaseScraper):
    def __init__(self, job_title: str):
        selectors = {
            "link": "a[href*='/rc/clk']",
            "title": '[data-testid="jobsearch-JobInfoHeader-title"]',
            "content": "#jobDescriptionText",
        }
        query_params = {"q": f'"{job_title}"', "fromage": 7}
        super().__init__(
            job_title,
            "https://www.indeed.com/jobs",
            selectors,
            query_params,
            self.indeed_next_page_logic,
        )

    def format_link(self, vacancy: ElementHandle):
        return f"https://www.indeed.com/viewjob?jk={vacancy.get_attribute('href').split('jk=')[-1]}"

    def indeed_next_page_logic(self, page: Page, page_number: int):
        try:
            next_page_selector = f'[data-testid="pagination-page-{page_number}"][aria-label="{page_number}"]'
            next_page_link = page.locator(next_page_selector)

            if next_page_link.count() > 0:
                next_page_link.scroll_into_view_if_needed()
                page.wait_for_selector(next_page_selector, state="visible", timeout=5000)
                page.click(next_page_selector)

                active_page_selector = '[data-testid="pagination-page-current"][aria-current="page"]'
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
