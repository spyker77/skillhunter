import logging
import re
from collections import Counter
from secrets import SystemRandom
from time import sleep
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from flashtext import KeywordProcessor
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .utils import get_user_agent

logger = logging.getLogger("django")


def initialize_webdriver():
    # Run webdriver with a new user agent each time it starts.
    service = Service(log_path="/dev/null")
    options = Options()
    options.headless = True
    options.set_preference("general.useragent.override", get_user_agent())
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    driver = webdriver.Firefox(service=service, options=options)
    driver.maximize_window()
    return driver


def check_subscription_popup(driver: webdriver):
    # Check if there is a subscription popup, then close it.
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="popover-email-div"]')))
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popover-x"]')))
        close_alert_button = driver.find_element(By.XPATH, '//*[@id="popover-x"]')
        webdriver.ActionChains(driver).move_to_element(close_alert_button).perform()
        close_alert_button.click()
    except TimeoutException:
        # If there is no pop-up, do nothing and continue the flow.
        pass


def scan_all_search_results(job_title: str):
    # Scan each search page for vacancy links and continue while the Next button is presented.
    all_links: set[str] = set()
    driver = initialize_webdriver()
    try:
        payload = {"q": f"title:({job_title})", "fromage": 7, "filter": 0}
        driver.get("https://www.indeed.com/jobs?" + urlencode(payload))
        while True:
            check_subscription_popup(driver)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            all_vacancies = soup.find_all("a", href=re.compile(r"/rc/clk"))
            links = {
                "https://www.indeed.com/viewjob?jk=" + vacancy["href"].split("jk=")[-1] for vacancy in all_vacancies
            }
            # Exit if we started collecting the same links or vacancies are not displayed at all.
            if links.issubset(all_links):
                return all_links
            all_links.update(links)
            # Or if there is no the Next button.
            if 'aria-label="Next"' not in html:
                return all_links
            # Otherwise, continue with normal flow.
            else:
                next_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]')
                webdriver.ActionChains(driver).move_to_element(next_button).perform()
                next_button.click()
    except MoveTargetOutOfBoundsException:
        logger.warning(f'🚨 MoveTargetOutOfBoundsException occurred while parsing "{job_title}"')
        return all_links
    finally:
        driver.quit()


def fetch_vacancy_page(link: str, driver: webdriver):
    # Put the link, title and content in a dict – so far without skills.
    try:
        driver.get(link)
        check_subscription_popup(driver)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find(attrs={"class": "jobsearch-JobInfoHeader-title-container"}).text
        content = soup.find(attrs={"class": "jobsearch-jobDescriptionText"}).text
        vacancy_page = {"url": link, "title": title, "content": content}
        timeout = SystemRandom().uniform(1.0, 5.0)
        sleep(timeout)
        return vacancy_page
    except AttributeError:
        logger.warning(f"🚨 AttributeError occurred while fetching: {link}")
        return None


def fetch_all_vacancy_pages(all_links: set[str], indeed_links_we_already_have: list[str]):
    # Parse all the vacancy pages one by one.
    driver = initialize_webdriver()
    try:
        vacancies_without_skills = list()
        # Reduce pressure on indeed.com by checking if we have this link.
        new_links = [link for link in all_links if link not in indeed_links_we_already_have]
        for link in new_links:
            result = fetch_vacancy_page(link, driver)
            vacancies_without_skills.append(result)
        return tuple(vacancies_without_skills)
    finally:
        driver.quit()


def process_vacancy_content(vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
    # Extract keywords from the content of the vacancy and count each keyword.
    try:
        content = vacancy_without_skills["content"]
        keywords_found = keyword_processor.extract_keywords(content)
        counts = Counter(keywords_found)
        # Only return vacancies with relevant skills, otherwise it is useless.
        if len(counts) == 0:
            return None
        skills = {"rated_skills": counts}
        vacancy_plus_skills = vacancy_without_skills.copy()
        vacancy_plus_skills.update(skills)
        return vacancy_plus_skills
    except TypeError:
        logger.warning("🚨 TypeError occurred while processing vacancy content.")
        return None


def main(job_title: str, indeed_links_we_already_have: list[str], skills: dict[str, list[str]]):
    # Main flow of parsing the vacancies and counting the relevant skills.
    all_links = scan_all_search_results(job_title)
    vacancies_without_skills = fetch_all_vacancy_pages(all_links, indeed_links_we_already_have)
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(skills)
    collected_jobs = (
        process_vacancy_content(vacancy_without_skills, keyword_processor)
        for vacancy_without_skills in vacancies_without_skills
        if vacancy_without_skills is not None
    )
    return collected_jobs
