import json
import logging
import logging.config
import platform
import random
import re
from collections import Counter
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from faker import Faker
from flashtext import KeywordProcessor
from selenium import webdriver
from selenium.common.exceptions import MoveTargetOutOfBoundsException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scrapers.management.logging_config import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger()


def get_user_agent():
    # Generate user-agent appropriate for the platform.
    faker = Faker()
    os_name = platform.system().lower()
    if os_name == "darwin":
        while True:
            user_agent = faker.firefox()
            if "Mac" in user_agent:
                return user_agent
    elif os_name == "windows":
        while True:
            user_agent = faker.firefox()
            if "Windows" in user_agent:
                return user_agent
    else:
        while True:
            user_agent = faker.firefox()
            if "Linux" in user_agent:
                return user_agent


def initialize_webdriver():
    # Run webdriver with a new user agent each time it starts.
    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    profile = FirefoxProfile()
    profile.set_preference("general.useragent.override", get_user_agent())
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("useAutomationExtension", False)
    profile.update_preferences()
    driver = webdriver.Firefox(firefox_profile=profile, options=firefox_options, service_log_path="/dev/null")
    driver.maximize_window()
    return driver


def check_subscription_popup(driver):
    # Check if there is a subscription popup, then close it.
    try:
        WebDriverWait(driver, random.SystemRandom().uniform(2.0, 5.0)).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="popover-email-div"]'))
        )
        close_alert = driver.find_element_by_xpath('//*[@id="popover-x"]')
        webdriver.ActionChains(driver).move_to_element(close_alert).perform()
        close_alert.click()
    except TimeoutException:
        # If there is no pop-up, do nothing and continue the flow.
        pass


def scan_all_search_results(job_title):
    # Scan each search page for vacancy links and continue while the Next button is presented.
    all_links = set()
    driver = initialize_webdriver()
    try:
        payload = {"q": f"title:({job_title})", "fromage": 1, "filter": 0}
        driver.get("https://www.indeed.com/jobs?" + urlencode(payload))
        while True:
            check_subscription_popup(driver)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            all_vacancies = soup.find_all("a", href=re.compile(r"/rc/clk"))
            links = set(
                "https://www.indeed.com/viewjob?jk=" + vacancy["href"].split("jk=")[-1] for vacancy in all_vacancies
            )
            # Exit if we started collecting the same links or vacancies are not displayed at all.
            if links.issubset(all_links):
                return all_links
            all_links.update(links)
            # Or if there is no the Next button.
            if 'aria-label="Next"' not in html:
                return all_links
            # Otherwise, continue with normal flow.
            else:
                next_button = driver.find_element_by_css_selector('[aria-label="Next"]')
                webdriver.ActionChains(driver).move_to_element(next_button).perform()
                next_button.click()
    except MoveTargetOutOfBoundsException:
        logger.warning(f'🚨 MoveTargetOutOfBoundsException occurred while parsing "{job_title}"')
        return all_links
    finally:
        driver.quit()


def fetch_vacancy_page(link, driver):
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
        return vacancy_page
    except AttributeError:
        logger.warning(f"🚨 AttributeError occurred while fetching: {link}")
        return None


def fetch_all_vacancy_pages(all_links, indeed_links_we_already_have):
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


def process_vacancy_content(vacancy_without_skills, keyword_processor):
    # Extract keywords from the content of the vacancy and count each keyword.
    try:
        content = vacancy_without_skills["content"]
        keywords_found = keyword_processor.extract_keywords(content)
        counts = json.dumps(Counter(keywords_found))
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


def main(job_title, indeed_links_we_already_have, skills):
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
