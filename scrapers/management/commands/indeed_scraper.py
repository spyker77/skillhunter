import asyncio
import re
from collections import Counter

import aiohttp
from aiohttp.client_exceptions import (
    ClientConnectorError,
    ClientPayloadError,
    ServerDisconnectedError,
)
from bs4 import BeautifulSoup
from fake_useragent import FakeUserAgentError, UserAgent
from flashtext import KeywordProcessor

try:
    FAKE_AGENT = UserAgent(cache=False)
except FakeUserAgentError:
    print("🚨 Failed to get fake user agent.")
    FAKE_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 11.1; rv:84.0) Gecko/20100101 Firefox/84.0"


def prepare_query(job_title):
    # Prepare job title for use in the phrase search.
    query = job_title.strip('"')
    return query


async def scan_single_search_page(query, page_num, session):
    # Scan search page for vacancy links.
    payload = {
        "q": f"title:({query})",
        "fromage": 7,
        "limit": 50,
        "start": page_num,
    }
    for _ in range(10):
        try:
            async with session.get(
                "https://www.indeed.com/jobs", params=payload
            ) as resp:
                try:
                    html = await asyncio.shield(resp.text())
                    soup = BeautifulSoup(html, "html.parser")
                    # If any CAPTCHA appears, wait for 10 minutes and try again.
                    if "captcha" in str(soup).lower():
                        print("⌛ Wait for 10 minutes.")
                        await asyncio.sleep(60 * 10)
                        continue
                    all_vacancies = soup.find_all("a", href=re.compile(r"/rc/clk"))
                    # Extract valid links to vacancy pages.
                    links = set(
                        "https://www.indeed.com/viewjob?jk="
                        + vacancy["href"].split("&")[0].split("jk=")[-1]
                        for vacancy in all_vacancies
                    )
                    return links
                except AttributeError:
                    print(f"🚨 AttributeError occurred while scanning: {resp.url}")
                    return None
                except ClientPayloadError:
                    print(f"🚨 ClientPayloadError occurred while scanning: {resp.url}")
                    return None
                except asyncio.TimeoutError:
                    print(f"🚨 TimeoutError occurred while scanning: {resp.url}")
                    return None
        except ClientConnectorError:
            print("🚨 ClientConnectorError occurred while scanning indeed.com.")
            await asyncio.sleep(60)
    return None


async def scan_all_search_results(query, session):
    # Schedule all search results for asynchronous processing.
    tasks = list()
    indeed_max_pages = 20
    for num in range(indeed_max_pages):
        multiplier = 50
        page_num = num * multiplier
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
                title = soup.find(
                    attrs={"class": "jobsearch-JobInfoHeader-title-container"}
                ).text
                content = soup.find(
                    attrs={"class": "jobsearch-jobDescriptionText"}
                ).text
                vacancy_page = {
                    "url": link,
                    "title": title,
                    "content": content,
                }
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


async def fetch_all_vacancy_pages(all_links, indeed_links_we_already_have, session):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = list()
    # Reduce pressure on indeed.com by checking if we have this link.
    new_links = [link for link in all_links if link not in indeed_links_we_already_have]
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


async def main(job_title, indeed_links_we_already_have, skills):
    # Import this function to collect vacancies for a given job title.
    async with aiohttp.ClientSession(
        headers={"user-agent": FAKE_AGENT.random, "Connection": "close"}
    ) as session:
        query = prepare_query(job_title)
        all_links = await scan_all_search_results(query, session)
        for _ in range(10):
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(
                    all_links, indeed_links_we_already_have, session
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
