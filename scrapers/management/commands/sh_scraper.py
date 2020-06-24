import re
import random
import asyncio
from collections import Counter

import aiohttp
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor
from aiohttp.client_exceptions import ClientPayloadError


headers = {
    "user-agent": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    ]
}
RANDOM_AGENT = random.choice(headers["user-agent"])


def prepare_query(job_title):
    # Prepare job title for use in the phrase search.
    query = job_title.strip('"')
    return query


async def scan_single_search_page(query, page_num, session):
    # Scan search page for vacancy links.
    payload = {
        "q": f'"{query}"',
        "fdb": 7,
        "pn": page_num,
    }
    async with session.get(
        "https://www.simplyhired.com/search", params=payload
    ) as resp:
        try:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            all_vacancies = soup.find_all("a", href=re.compile(r"/job/"))
            # Extract valid links to vacancy pages and clean the tail.
            links = set(
                ("https://www.simplyhired.com" + vacancy["href"]).split("?tk=")[0]
                for vacancy in all_vacancies
            )
            return links
        except AttributeError:
            print(f"🚨 AttributeError occurred while scanning the URL: {resp.url}")
            return None
        except ClientPayloadError:
            print(f"🚨 ClientPayloadError occurred while scanning the URL: {resp.url}")
            return None


async def scan_all_search_results(query, session):
    # Schedule all search results for asynchronous processing.
    tasks = list()
    sh_max_pages = 90 + 1
    for page_num in range(1, sh_max_pages):
        task = asyncio.create_task(scan_single_search_page(query, page_num, session))
        tasks.append(task)
    all_sets = await asyncio.gather(*tasks)
    # Unpack the list of sets into a single set of all links.
    all_links = set()
    for s in all_sets:
        if s is not None:
            all_links.update(s)
        else:
            pass
    return all_links


async def fetch_vacancy_page(link, session):
    # Put the link, title and content in a dict – so far without skills.
    async with session.get(link) as resp:
        try:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            title = soup.find(attrs={"class": "viewjob-jobTitle h2"}).text
            content = soup.find(attrs={"class": "p"}).text
            vacancy_page = {"url": link, "title": title, "content": content}
            return vacancy_page
        except AttributeError:
            print(f"🚨 AttributeError occurred while fetching the URL: {link}")
            return None
        except ClientPayloadError:
            print(f"🚨 ClientPayloadError occurred while fetching the URL: {link}")
            return None


async def fetch_all_vacancy_pages(all_links, session):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = list()
    for link in all_links:
        task = asyncio.create_task(fetch_vacancy_page(link, session))
        tasks.append(task)
    vacancies_without_skills = await asyncio.gather(*tasks)
    return vacancies_without_skills


def process_vacancy_content(vacancy_without_skills, keyword_processor):
    # Extract keywords from the content of the vacancy and count each keyword.
    try:
        content = vacancy_without_skills["content"]
        keywords_found = keyword_processor.extract_keywords(content)
        counts = dict(Counter(keywords_found))
        skills = {"rated_skills": counts}
        vacancy_plus_skills = vacancy_without_skills.copy()
        vacancy_plus_skills.update(skills)
        return vacancy_plus_skills
    except TypeError:
        print("🚨 TypeError occurred while processing vacancy content.")
        return None


async def main(job_title, SKILLS):
    # Import this function to collect vacancies for a given job title.
    async with aiohttp.ClientSession(
        headers={"user-agent": RANDOM_AGENT, "Connection": "close"}
    ) as session:
        query = prepare_query(job_title)
        all_links = await scan_all_search_results(query, session)
        attempt = 1
        while attempt < 10:
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(
                    all_links, session
                )
                break
            except OSError:
                print(f"🚨 OSError occured on attempt {attempt}")
                attempt += 1
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_dict(SKILLS)
        collected_jobs = (
            process_vacancy_content(vacancy_without_skills, keyword_processor)
            for vacancy_without_skills in vacancies_without_skills
            if vacancy_without_skills is not None
        )
    return collected_jobs
