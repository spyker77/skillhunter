import re
import asyncio
from collections import Counter

import aiohttp
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor
from aiohttp.client_exceptions import ClientPayloadError, ServerDisconnectedError


def prepare_query(job_title):
    # Prepare job title for use in the phrase search.
    query = job_title.strip('"')
    return query


async def scan_single_search_page(query, page_num, session):
    # Scan search page for vacancy links.
    payload = {
        "L_is_autosearch": "false",
        "clusters": "true",
        "enable_snippets": "true",
        "search_field": "name",
        "search_period": 7,
        "text": query,
        "page": page_num,
    }
    for _ in range(5):
        async with session.get("https://hh.ru/search/vacancy", params=payload) as resp:
            try:
                html = await asyncio.shield(resp.text())
                soup = BeautifulSoup(html, "html.parser")
                all_vacancies = soup.find_all("a", href=re.compile(r"hh.ru/vacancy"))
                # Extract valid links to vacancy pages and clean their tails.
                links = set(vacancy["href"].split("?")[0] for vacancy in all_vacancies)
                return links
            except AttributeError:
                print(f"🚨 AttributeError occurred while scanning: {resp.url}")
                return None
            except ClientPayloadError:
                print(f"🚨 ClientPayloadError occurred while scanning: {resp.url}")
                return None
            except asyncio.TimeoutError:
                print(f"🚨 TimeoutError occurred while scanning: {resp.url}")
                await asyncio.sleep(60)
    return None


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
    for one_set in all_sets:
        if one_set is not None:
            all_links.update(one_set)
    return all_links


async def fetch_vacancy_page(link, session):
    # Put the link, title and content in a dict – so far without skills.
    for _ in range(5):
        try:
            async with session.get(link) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                title = soup.find(attrs={"data-qa": "vacancy-title"}).text
                content = soup.find(attrs={"data-qa": "vacancy-description"}).text
                vacancy_page = {"url": link, "title": title, "content": content}
                return vacancy_page
        except AttributeError:
            print(f"🚨 AttributeError occurred while fetching: {link}")
            return None
        except ClientPayloadError:
            print(f"🚨 ClientPayloadError occurred while fetching: {link}")
            return None
        except ServerDisconnectedError:
            print(f"🚨 ServerDisconnectedError occurred while fetching: {link}")
            await asyncio.sleep(60)
        except asyncio.TimeoutError:
            print(f"🚨 TimeoutError occurred while fetching: {link}")
            await asyncio.sleep(60)
    return None


async def fetch_all_vacancy_pages(all_links, hh_links_we_already_have, session):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = list()
    # Reduce pressure on hh.ru by checking if we already have the link.
    new_links = [link for link in all_links if link not in hh_links_we_already_have]
    for link in new_links:
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


async def main(job_title, hh_links_we_already_have, skills):
    # Import this function to collect vacancies for a given job title.
    async with aiohttp.ClientSession(headers={"Connection": "close"}) as session:
        query = prepare_query(job_title)
        all_links = await scan_all_search_results(query, session)
        for _ in range(10):
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(
                    all_links, hh_links_we_already_have, session
                )
                keyword_processor = KeywordProcessor()
                keyword_processor.add_keywords_from_dict(skills)
                collected_jobs = (
                    process_vacancy_content(vacancy_without_skills, keyword_processor)
                    for vacancy_without_skills in vacancies_without_skills
                    if vacancy_without_skills is not None
                )
                await asyncio.sleep(60)
                return collected_jobs
            except OSError:
                print(f"🚨 OSError occured for {job_title}.")
        # If couldn't recover after errors, then return an empty list.
        await asyncio.sleep(60)
        return []
