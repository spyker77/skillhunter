import logging
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from flashtext import KeywordProcessor
from selenium.common.exceptions import MoveTargetOutOfBoundsException, NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from .utils import get_webdriver

logger = logging.getLogger("django")


def navigate_to_next_page(driver: WebDriver):
    # Navigates to the next page of the search results.
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, '[data-qa="pager-next"]')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        return True
    except (NoSuchElementException, MoveTargetOutOfBoundsException):
        # It usually happens on the last page when there is no Next button.
        return False


def scan_single_search_page(driver: WebDriver):
    # Scans and collects job vacancy links from a single search page.
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    soup = BeautifulSoup(driver.page_source, "lxml")
    all_vacancies = soup.select("a[href*='hh.ru/vacancy']")
    links = {str(vacancy["href"]).split("?")[0] for vacancy in all_vacancies if "href" in vacancy.attrs}
    return links


def scan_all_search_results(job_title: str):
    # Scans and collects job vacancy links for the specified job title.
    with get_webdriver() as driver:
        all_links = set()
        payload = {"text": f'"{job_title}"', "search_period": 7, "ored_clusters": "true"}
        driver.get("https://hh.ru/search/vacancy?" + urlencode(payload))
        while True:
            # Need to wait for the dynamic page to load, otherwise StaleElementReferenceException.
            WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")

            new_links = scan_single_search_page(driver)
            if new_links.issubset(all_links):
                break
            all_links.update(new_links)

            if not navigate_to_next_page(driver):
                break
        return all_links


def fetch_vacancy_page(link: str):
    # Fetches and parses the content of a specific vacancy page.
    with get_webdriver() as driver:
        try:
            driver.get(link)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            title_selector = '[data-qa="vacancy-title"]'
            content_selector = '[data-qa="vacancy-description"]'

            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, title_selector)))
            soup = BeautifulSoup(driver.page_source, "lxml")
            title = soup.select_one(title_selector).get_text(strip=True)
            content = soup.select_one(content_selector).get_text(strip=True)
            vacancy_page = {"url": link, "title": title, "content": content}
            return vacancy_page
        except TimeoutException:
            logger.warning(f"🚨 TimeoutException occurred while fetching: {link}")
        except AttributeError:
            logger.warning(f"🚨 AttributeError occurred while fetching: {link}")


def fetch_all_vacancy_pages(all_links: set[str], hh_links_we_already_have: list[str]):
    # Fetches all new vacancy pages from the collected links.
    vacancies_without_skills = []
    new_links = set(all_links) - set(hh_links_we_already_have)
    with ThreadPoolExecutor(10) as executor:
        future_to_link = {executor.submit(fetch_vacancy_page, link): link for link in new_links}
        for future in as_completed(future_to_link):
            link = future_to_link[future]
            try:
                result = future.result()
                if result:
                    vacancies_without_skills.append(result)
            except Exception as e:
                logger.error(f"🚨 {link} generated an exception: {e}")
        return vacancies_without_skills


def process_vacancy_content(vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
    # Processes the vacancy content to extract and count relevant skills.
    try:
        content = vacancy_without_skills["content"]
        keywords_found = keyword_processor.extract_keywords(content)
        counts = Counter(keywords_found)
        if not counts:
            return None
        return {**vacancy_without_skills, "rated_skills": counts}
    except TypeError:
        logger.warning("🚨 TypeError occurred while processing vacancy content.")


def main(job_title: str, hh_links_we_already_have: list[str], skills: dict[str, list[str]]):
    # Main function orchestrating the flow of parsing vacancies and extracting skills.
    all_links = scan_all_search_results(job_title)
    vacancies_without_skills = fetch_all_vacancy_pages(all_links, hh_links_we_already_have)
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(skills)
    collected_jobs = (
        process_vacancy_content(vacancy, keyword_processor)
        for vacancy in vacancies_without_skills
        if vacancy is not None
    )
    return collected_jobs
