import logging
from abc import ABC, abstractmethod
from collections import Counter
from urllib.parse import urlencode

from flashtext import KeywordProcessor
from playwright.sync_api import ElementHandle, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from tenacity import RetryError, Retrying, stop_after_attempt, wait_random_exponential

from .utils import get_playwright_page

logger = logging.getLogger("django")


class AbstractScraper(ABC):
    """
    Abstract base class for web scrapers.
    """

    @abstractmethod
    def scan_all_search_results(self):
        """
        Scans all search result pages and collects job vacancy links.
        """

    @abstractmethod
    def fetch_vacancy_page(self, link: str):
        """
        Fetches and parses the content of a specific vacancy page.
        """

    @abstractmethod
    def process_vacancy_content(self, vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
        """
        Processes the content of a vacancy to extract and count relevant skills.
        """


class BaseScraper(AbstractScraper):
    """
    A base class for web scraping using Playwright.
    """

    def __init__(self, job_title, search_url, selectors, query_params, next_page_logic):
        """
        Args:
            job_title (str): The job title to run scrapers with.
            search_url (str): The base URL to start scraping from.
            selectors (dict): CSS selectors for various elements to scrape.
            query_params (dict): Query parameters for the URL.
            next_page_logic (function): A function to navigate to the next page in pagination.
        """
        self.job_title = job_title
        self.search_url = search_url
        self.selectors = selectors
        self.query_params = query_params
        self.next_page_logic = next_page_logic

    def next_page(self, page: Page, page_number: int):
        """
        Navigates to the next page using the provided pagination logic.

        Args:
            page (Page): The current page object from Playwright.
            page_number (int): The current page number.

        Returns:
            bool: True if navigation to the next page was successful, False otherwise.
        """
        return self.next_page_logic(page, page_number)

    def format_link(self, vacancy: ElementHandle):
        """
        Formats the extracted link from a vacancy ElementHandle.

        Args:
            vacancy (ElementHandle): The ElementHandle object representing a vacancy link.

        Returns:
            str: Formatted URL string.
        """
        return vacancy.get_attribute("href").split("?")[0]

    def scan_single_search_page(self, page: Page):
        """
        Scans a single search page for job vacancy links.

        Args:
            page (Page): The current page object from Playwright.

        Returns:
            set: A set of extracted vacancy URLs.
        """
        page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
        try:
            page.wait_for_selector(self.selectors["link"], state="attached", timeout=5000)
        except PlaywrightTimeoutError:
            logger.warning(f"Timeout error while waiting for selector: {self.selectors['link']}")
            return set()
        else:
            all_vacancies = page.query_selector_all(self.selectors["link"])
            return {self.format_link(vacancy) for vacancy in all_vacancies}

    def scan_all_search_results(self):
        """
        Scans all search result pages and collects job vacancy links.

        Returns:
            set: A set of all extracted vacancy URLs across all pages.
        """
        with get_playwright_page() as page:
            page_number = 1
            all_links = set()
            page.goto(f"{self.search_url}?{urlencode(self.query_params)}")
            while True:
                new_links = self.scan_single_search_page(page)
                if new_links.issubset(all_links):
                    break
                all_links.update(new_links)

                page_number += 1
                if not self.next_page(page, page_number):
                    break
            return all_links

    def fetch_vacancy_page(self, link: str):
        """
        Fetches and parses the content of a specific vacancy page.

        Args:
            link (str): The URL of the vacancy page.

        Returns:
            dict: A dictionary containing vacancy details such as URL, title, and content.
        """
        try:
            with get_playwright_page() as page:
                try:
                    for attempt in Retrying(stop=stop_after_attempt(3), wait=wait_random_exponential(min=0.1, max=1)):
                        with attempt:
                            page.goto(link)
                except RetryError:
                    return

                page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                page.wait_for_selector(self.selectors["title"], state="attached", timeout=5000)

                title = page.text_content(self.selectors["title"])
                content = page.text_content(self.selectors["content"])

                if title and content:
                    return {"url": link, "title": title.strip(), "content": content.strip()}
        except Exception as e:
            logger.error(f"Error fetching vacancy page: {link}", exc_info=e)

    def fetch_all_vacancy_pages(self, links: set[str]):
        """
        Fetches all vacancy pages from a set of links.

        Args:
            links (set[str]): A set of vacancy page URLs.

        Returns:
            list: A list of dictionaries, each containing details of a vacancy.
        """
        vacancies_without_skills = list()
        # NOTE: Fetching pages concurrently results in bot detection.
        for link in links:
            result = self.fetch_vacancy_page(link)
            if result:
                vacancies_without_skills.append(result)
        return vacancies_without_skills

    def process_vacancy_content(self, vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
        """
        Processes the content of a vacancy to extract and count relevant skills.

        Args:
            vacancy_without_skills (dict[str, str]): A dictionary containing vacancy details.
            keyword_processor (KeywordProcessor): An instance of flashtext.KeywordProcessor.

        Returns:
            dict: A dictionary with vacancy details and extracted skills.
        """
        try:
            content = vacancy_without_skills["content"]
            if keywords_found := keyword_processor.extract_keywords(content):
                return {**vacancy_without_skills, "rated_skills": Counter(keywords_found)}
        except TypeError:
            logger.warning("TypeError occurred while processing vacancy content.")
            return vacancy_without_skills
