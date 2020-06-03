import re
import random
import asyncio
from time import sleep

import aiohttp
from bs4 import BeautifulSoup
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
    stripped = job_title.strip('"')
    query = f'"{stripped}"'
    return query


async def scan_single_search_page(query, page_num, session):
    # Scan search page for vacancy links.
    payload = {
        "text": query,
        "page": page_num,
    }
    async with session.get("https://hh.ru/search/vacancy", params=payload) as resp:
        try:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            all_vacancies = soup.find_all(
                "a", href=re.compile(r"https://hh.ru/vacancy/")
            )
            # Extract valid links to vacancy pages and clean their tails.
            links = set(vacancy["href"].split("?")[0] for vacancy in all_vacancies)
            return links
        except AttributeError:
            print(f"AttributeError occurred while scanning the URL: {link}")


async def scan_all_search_results(query, session):
    # Schedule all search results for asynchronous processing.
    tasks = list()
    hh_max_pages = 40
    for page_num in range(hh_max_pages):
        task = asyncio.create_task(scan_single_search_page(query, page_num, session))
        tasks.append(task)
    all_sets = await asyncio.gather(*tasks)
    # Unpack the list of sets into a single set of all links.
    all_links = set()
    for s in all_sets:
        all_links.update(s)
    return all_links


async def fetch_vacancy_page(link, session):
    # Put the link, title and content in a dict – so far without skills.
    async with session.get(link) as resp:
        attempt = 1
        while attempt < 10:
            sleep(0.5)
            try:
                html = await resp.text()
                soup = BeautifulSoup(html, "lxml")
                title = soup.find(attrs={"data-qa": "vacancy-title"}).text
                content = soup.find(attrs={"data-qa": "vacancy-description"}).text
                vacancy_page = {"url": link, "title": title, "content": content}
                return vacancy_page
            except AttributeError:
                print(f"AttributeError occurred while fetching the URL: {link}")
                attempt += 1
            except ClientPayloadError:
                print(f"ClientPayloadError occurred while fetching the URL: {link}")
                attempt += 1


async def fetch_all_vacancy_pages(all_links, session):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = list()
    for link in all_links:
        task = asyncio.create_task(fetch_vacancy_page(link, session))
        tasks.append(task)
    vacancies_without_skills = await asyncio.gather(*tasks)
    return vacancies_without_skills


async def main(job_title):
    # Import this function to collect vacancies for a given job title.
    async with aiohttp.ClientSession(headers={"user-agent": RANDOM_AGENT}) as session:
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
                print(f"OSError occured on attempt {attempt}")
                attempt += 1
    return vacancies_without_skills
