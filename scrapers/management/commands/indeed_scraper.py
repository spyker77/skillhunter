import re
from collections import Counter
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgentError, UserAgent
from flashtext import KeywordProcessor
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.options import Options as FirefoxOptions

try:
    FAKE_AGENT = UserAgent(cache=False)
except FakeUserAgentError:
    print("🚨 Failed to get fake user agent.")
    FAKE_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1; rv:84.0) Gecko/20100101 Firefox/84.0"


def initialize_webdriver():
    # Launch new webdriver on each request in order to generate new user-agent.
    # Hint to hide selenium usage from browsers: https://stackoverflow.com/a/60252464/10748367
    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("general.useragent.override", FAKE_AGENT.random)
    firefox_profile.set_preference("dom.webdriver.enabled", False)
    firefox_profile.set_preference("useAutomationExtension", False)
    firefox_profile.update_preferences()
    driver = webdriver.Firefox(
        firefox_profile=firefox_profile,
        options=firefox_options,
        service_log_path="/dev/null",
    )
    driver.maximize_window()
    return driver


def prepare_query(job_title):
    # Prepare job title for use in the phrase search.
    query = job_title.strip('"')
    return query


def scan_single_search_page(query, page_num):
    # Scan search page for vacancy links.
    try:
        payload = {
            "as_ttl": query,
            "fromage": 7,
            "limit": 50,
            "start": page_num,
        }
        driver = initialize_webdriver()
        driver.get("https://www.indeed.com/jobs?" + urlencode(payload))
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        all_vacancies = soup.find_all("a", href=re.compile(r"/rc/clk"))
        # Extract valid links to vacancy pages.
        links = set(
            "https://www.indeed.com/viewjob?jk="
            + vacancy["href"].split("&")[0].split("jk=")[-1]
            for vacancy in all_vacancies
        )
        return links
    finally:
        driver.quit()


def scan_all_search_results(query):
    # Collect results from all search pages.
    all_links = set()
    indeed_max_pages = 20
    for num in range(indeed_max_pages):
        multiplier = 50
        page_num = num * multiplier
        links = scan_single_search_page(query, page_num)
        all_links.update(links)
    return all_links


def fetch_vacancy_page(link):
    # Put the link, title and content in a dict – so far without skills.
    try:
        driver = initialize_webdriver()
        driver.get(link)
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        title = soup.find(
            attrs={"class": "jobsearch-JobInfoHeader-title-container"}
        ).text
        content = soup.find(attrs={"class": "jobsearch-jobDescriptionText"}).text
        vacancy_page = {
            "url": link,
            "title": title,
            "content": content,
        }
        return vacancy_page
    finally:
        driver.quit()


def fetch_all_vacancy_pages(all_links, indeed_links_we_already_have):
    # Parse all the vacancy pages one by one.
    vacancies_without_skills = list()
    # Reduce pressure on indeed.com by checking if we have this link.
    new_links = [link for link in all_links if link not in indeed_links_we_already_have]
    for link in new_links:
        result = fetch_vacancy_page(link)
        vacancies_without_skills.append(result)
    return tuple(vacancies_without_skills)


def process_vacancy_content(vacancy_without_skills, keyword_processor):
    # Extract keywords from the content of the vacancy and count each keyword.
    try:
        content = vacancy_without_skills["content"]
        keywords_found = keyword_processor.extract_keywords(content)
        counts = dict(Counter(keywords_found))
        # Only return vacancies with relevant skills, otherwise it is useless.
        if len(counts) == 0:
            return None
        skills = {"rated_skills": counts}
        vacancy_plus_skills = vacancy_without_skills.copy()
        vacancy_plus_skills.update(skills)
        return vacancy_plus_skills
    except TypeError:
        print("🚨 TypeError occurred while processing vacancy content.")
        return None


def main(job_title, indeed_links_we_already_have, skills):
    query = prepare_query(job_title)
    all_links = scan_all_search_results(query)
    vacancies_without_skills = fetch_all_vacancy_pages(
        all_links, indeed_links_we_already_have
    )
    keyword_processor = KeywordProcessor()
    keyword_processor.add_keywords_from_dict(skills)
    collected_jobs = (
        process_vacancy_content(vacancy_without_skills, keyword_processor)
        for vacancy_without_skills in vacancies_without_skills
        if vacancy_without_skills is not None
    )
    return collected_jobs
