import asyncio
import json
import logging
import re
from collections import Counter
from secrets import SystemRandom

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ClientOSError, ClientPayloadError, ServerDisconnectedError
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor

from .utils import get_user_agent

logger = logging.getLogger("django")


async def scan_single_search_page(job_title: str, page_num: int, session: ClientSession):
    # Scan search page for vacancy links.
    payload = {
        "L_is_autosearch": "false",
        "clusters": "true",
        "enable_snippets": "true",
        "search_field": "name",
        "search_period": 7,
        "text": job_title,
        "page": page_num,
    }
    for _ in range(10):
        try:
            async with session.get("https://hh.ru/search/vacancy", params=payload) as resp:
                try:
                    html = await asyncio.shield(resp.text())
                    soup = BeautifulSoup(html, "html.parser")
                    all_vacancies = soup.find_all("a", href=re.compile(r"hh.ru/vacancy"))
                    # Extract valid links to vacancy pages and clean their tails.
                    links = {vacancy["href"].split("?")[0] for vacancy in all_vacancies}
                    timeout = SystemRandom().uniform(1.0, 10.0)
                    await asyncio.sleep(timeout)
                    return links
                except AttributeError:
                    logger.warning(f"🚨 AttributeError occurred while scanning: {resp.url}")
                    return None
                except ClientPayloadError:
                    logger.warning(f"🚨 ClientPayloadError occurred while scanning: {resp.url}")
                    return None
                except asyncio.TimeoutError:
                    logger.warning(f"🚨 TimeoutError occurred while scanning: {resp.url}")
                    await asyncio.sleep(60)
        except ClientConnectorError:
            logger.warning("🚨 ClientConnectorError occurred while scanning hh.ru.")
            await asyncio.sleep(60)
        except ServerDisconnectedError:
            logger.warning("🚨 ServerDisconnectedError occurred while scanning hh.ru.")
            await asyncio.sleep(60)
        except ClientOSError:
            logger.warning("🚨 ClientOSError occurred while scanning hh.ru.")
            await asyncio.sleep(60)
    return None


async def scan_all_search_results(job_title: str, session: ClientSession):
    # Schedule all search results for asynchronous processing.
    tasks = []
    hh_max_pages = 40
    for page_num in range(hh_max_pages):
        task = asyncio.create_task(scan_single_search_page(job_title, page_num, session))
        tasks.append(task)
    all_sets = await asyncio.gather(*tasks)
    # Unpack the list of sets into a single set of all links.
    all_links = set()
    for one_set in all_sets:
        if one_set is not None:
            all_links.update(one_set)
    return all_links


async def fetch_vacancy_page(link: str, session: ClientSession):
    # Put the link, title and content in a dict – so far without skills.
    for _ in range(5):
        try:
            async with session.get(link) as resp:
                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")
                title = soup.find(attrs={"data-qa": "vacancy-title"}).text
                content = soup.find(attrs={"data-qa": "vacancy-description"}).text
                vacancy_page = {"url": link, "title": title, "content": content}
                timeout = SystemRandom().uniform(1.0, 5.0)
                await asyncio.sleep(timeout)
                return vacancy_page
        except AttributeError:
            logger.warning(f"🚨 AttributeError occurred while fetching: {link}")
            return None
        except ClientPayloadError:
            logger.warning(f"🚨 ClientPayloadError occurred while fetching: {link}")
            return None
        except ServerDisconnectedError:
            logger.warning(f"🚨 ServerDisconnectedError occurred while fetching: {link}")
            await asyncio.sleep(60)
        except asyncio.TimeoutError:
            logger.warning(f"🚨 TimeoutError occurred while fetching: {link}")
            await asyncio.sleep(60)
    return None


async def fetch_all_vacancy_pages(all_links: set[str], hh_links_we_already_have: list[str], session: ClientSession):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = []
    # Reduce pressure on hh.ru by checking if we have this link.
    new_links = [link for link in all_links if link not in hh_links_we_already_have]
    for link in new_links:
        task = asyncio.create_task(fetch_vacancy_page(link, session))
        tasks.append(task)
    vacancies_without_skills = await asyncio.gather(*tasks)
    return vacancies_without_skills


def process_vacancy_content(vacancy_without_skills: dict[str, str], keyword_processor: KeywordProcessor):
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


async def main(job_title: str, hh_links_we_already_have: list[str], skills: dict[str, list[str]]):
    # Import this function to collect vacancies for a given job title.
    fake_agent = get_user_agent()
    async with ClientSession(headers={"user-agent": fake_agent, "Connection": "close"}) as session:
        all_links = await scan_all_search_results(job_title, session)
        for _ in range(10):
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(all_links, hh_links_we_already_have, session)
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
                logger.warning(f"🚨 OSError occured for {job_title}.")
        # If couldn't recover after errors, then return an empty list.
        await asyncio.sleep(60)
        return []
