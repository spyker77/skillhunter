import logging
from collections import Counter
from urllib.parse import urlencode

from flashtext import KeywordProcessor
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from tenacity import RetryError, Retrying, stop_after_attempt, wait_random_exponential

from .utils import get_playwright_page

logger = logging.getLogger("django")

# NOTE: Disabled to test if it's still needed.
# def check_subscription_popup(page: Page):
#     # Checks and closes the subscription popup if present on the page.
#     try:
#         if page.is_visible("#popover-email-div", timeout=1000):
#             page.click("#popover-x")
#     except PlaywrightTimeoutError:
#         # If there is no pop-up, do nothing and continue the flow.
#         pass


def next_page(page: Page, page_number: int):
    # Navigates to the next page of search results, if available.
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


def scan_single_search_page(page: Page):
    # Scans and collects job vacancy links from a single search page.
    selector = "a[href*='/rc/clk']"
    with page.expect_navigation():
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
    try:
        page.wait_for_selector(selector, state="attached", timeout=5000)
    except TimeoutError:
        logger.warning("Timeout occurred while scanning the search page.")
        return set()
    else:
        all_vacancies = page.query_selector_all(selector)
        return {
            "https://www.indeed.com/viewjob?jk=" + vacancy.get_attribute("href").split("jk=")[-1]
            for vacancy in all_vacancies
        }


def scan_all_search_results(job_title: str):
    # Scans and collects job vacancy links for the specified job title.
    with get_playwright_page() as page:
        page_number = 1
        all_links = set()
        query = {"q": f'"{job_title}"', "fromage": 7}
        page.goto(f"https://www.indeed.com/jobs?{urlencode(query)}")
        while True:
            new_links = scan_single_search_page(page)
            if new_links.issubset(all_links):
                break
            all_links.update(new_links)

            page_number += 1
            if not next_page(page, page_number):
                break
        return all_links


def fetch_vacancy_page(link: str):
    # Fetches and parses the content of a specific vacancy page.
    try:
        with get_playwright_page() as page:
            title_selector = '[data-testid="jobsearch-JobInfoHeader-title"]'
            content_selector = "#jobDescriptionText"

            try:
                for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_random_exponential(min=0.1, max=1)):
                    with attempt:
                        page.goto(link)
            except RetryError:
                return

            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_selector(title_selector, state="attached", timeout=5000)

            title = page.text_content(title_selector)
            content = page.text_content(content_selector)

            if title and content:
                return {"url": link, "title": title.strip(), "content": content.strip()}
    except Exception as e:
        logger.error(f"Error fetching vacancy page: {link}", exc_info=e)


def fetch_all_vacancy_pages(new_links: set[str]):
    # Fetches all new vacancy pages from the collected links.
    vacancies_without_skills = list()
    # NOTE: Fetching pages concurrently results in bot detection.
    for link in new_links:
        if result := fetch_vacancy_page(link):
            vacancies_without_skills.append(result)
    return vacancies_without_skills


def process_vacancy_content(vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
    # Processes the vacancy content to extract and count relevant skills.
    try:
        content = vacancy_without_skills["content"]
        if keywords_found := keyword_processor.extract_keywords(content):
            return {**vacancy_without_skills, "rated_skills": Counter(keywords_found)}
    except TypeError:
        logger.warning("TypeError occurred while processing vacancy content.")


def main(job_title: str, links_we_already_have: set[str], skills: dict[str, list[str]]):
    # Main function orchestrating the flow of parsing vacancies and extracting skills.
    all_links = scan_all_search_results(job_title)
    new_links = set(all_links) - set(links_we_already_have)
    vacancies_without_skills = fetch_all_vacancy_pages(new_links)
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(skills)
    collected_jobs = [
        process_vacancy_content(vacancy, keyword_processor)
        for vacancy in vacancies_without_skills
        if vacancy is not None
    ]
    return collected_jobs
