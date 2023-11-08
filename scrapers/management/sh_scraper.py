import asyncio
import logging
import re
from collections import Counter
from secrets import SystemRandom

import httpx
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor

from .utils import get_user_agent

logger = logging.getLogger("django")


async def scan_single_search_page(job_title: str, page_num: int, client: httpx.AsyncClient):
    # Scan search page for vacancy links.
    payload = {"q": f'"{job_title}"', "fdb": 7, "pn": page_num}
    for _ in range(10):
        try:
            response = await client.get("https://www.simplyhired.com/search", params=payload)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            all_vacancies = soup.find_all("a", href=re.compile(r"/job/"))
            # Extract valid links to vacancy pages and clean the tail.
            links = {("https://www.simplyhired.com" + vacancy["href"]).split("?")[0] for vacancy in all_vacancies}
            timeout = SystemRandom().uniform(1.0, 10.0)
            await asyncio.sleep(timeout)
            return links
        except (httpx.HTTPError, httpx.TimeoutException):
            logger.warning("🚨 Error occurred while scanning simplyhired.com.")
            await asyncio.sleep(60)
    return None


async def scan_all_search_results(job_title: str, client: httpx.AsyncClient):
    # Schedule all search results for asynchronous processing.
    tasks = []
    sh_max_pages = 90 + 1
    for page_num in range(1, sh_max_pages):
        task = asyncio.create_task(scan_single_search_page(job_title, page_num, client))
        tasks.append(task)
    all_sets = await asyncio.gather(*tasks)
    # Unpack the list of sets into a single set of all links.
    all_links = set()
    for one_set in all_sets:
        if one_set is not None:
            all_links.update(one_set)
    return all_links


async def fetch_vacancy_page(link: str, client: httpx.AsyncClient):
    # Put the link, title and content in a dict – so far without skills.
    for _ in range(5):
        try:
            response = await client.get(link)
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find(attrs={"class": "viewjob-jobTitle h2"}).text
            content = soup.find(attrs={"class": "p"}).text
            vacancy_page = {"url": link, "title": title, "content": content}
            timeout = SystemRandom().uniform(1.0, 5.0)
            await asyncio.sleep(timeout)
            return vacancy_page
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            logger.warning(f"🚨 Error occurred while fetching: {str(e)}")
            await asyncio.sleep(60)
    return None


async def fetch_all_vacancy_pages(all_links: set[str], sh_links_we_already_have: list[str], client: httpx.AsyncClient):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = []
    new_links = [link for link in all_links if link not in sh_links_we_already_have]
    for link in new_links:
        task = asyncio.create_task(fetch_vacancy_page(link, client))
        tasks.append(task)
    vacancies_without_skills = await asyncio.gather(*tasks)
    return vacancies_without_skills


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


async def main(job_title: str, sh_links_we_already_have: list[str], skills: dict[str, list[str]]):
    # Import this function to collect vacancies for a given job title.
    fake_agent = get_user_agent()
    async with httpx.AsyncClient(headers={"user-agent": fake_agent, "Connection": "close"}) as client:
        all_links = await scan_all_search_results(job_title, client)
        for _ in range(10):
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(all_links, sh_links_we_already_have, client)
                keyword_processor = KeywordProcessor()
                keyword_processor.add_keywords_from_dict(skills)
                collected_jobs = [
                    process_vacancy_content(vacancy_without_skills, keyword_processor)
                    for vacancy_without_skills in vacancies_without_skills
                    if vacancy_without_skills is not None
                ]
                await asyncio.sleep(60)
                return collected_jobs
            except OSError as e:
                logger.warning(f"🚨 OSError occurred for {job_title}: {str(e)}")
        # If couldn't recover after errors, then return an empty list.
        await asyncio.sleep(60)
        return []
