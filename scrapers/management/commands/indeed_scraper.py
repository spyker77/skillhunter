import re
import sys
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
        "q": f"title:({query})",
        "fromage": 7,
        "limit": 50,
        "start": page_num,
    }
    for attempt in range(60):
        async with session.get("https://www.indeed.com/jobs", params=payload) as resp:
            try:
                html = await asyncio.shield(resp.text())
                current_page_size = sys.getsizeof(html)
                # Usually, a single search page with results is larger if
                # it contains links to a vacancy pages (bytes).
                page_with_results_size = 800 * 1000
                # This is an empirically found threshold for a reCAPTCHA page (bytes).
                recaptcha_page_size = 500 * 1000
                # Check if the search page has the results then parse it.
                if current_page_size > page_with_results_size:
                    soup = BeautifulSoup(html, "html.parser")
                    all_vacancies = soup.find_all("a", href=re.compile(r"/rc/clk"))
                    # Extract valid links to vacancy pages.
                    links = set(
                        "https://www.indeed.com/viewjob?jk="
                        + vacancy["href"].split("&")[0].split("jk=")[-1]
                        for vacancy in all_vacancies
                    )
                    return links
                # If there are no results on the search page then exit.
                elif recaptcha_page_size < current_page_size < page_with_results_size:
                    return None
                # If none of the above and reCAPTCHA appears, then wait and try again.
                else:
                    await asyncio.sleep(60)
            except AttributeError:
                print(f"🚨 AttributeError occurred while scanning: {resp.url}")
                return None
            except ClientPayloadError:
                print(f"🚨 ClientPayloadError occurred while scanning: {resp.url}")
                return None
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
    for s in all_sets:
        if s is not None:
            all_links.update(s)
    return all_links


async def fetch_vacancy_page(link, session):
    # Put the link, title and content in a dict – so far without skills.
    for _ in range(1, 6):
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


async def fetch_all_vacancy_pages(all_links, indeed_links_we_already_have, session):
    # Schedule all the vacancy pages for asynchronous processing.
    tasks = list()
    # Reduce pressure on indeed.com by checking if we already have the link.
    only_new_links = [
        link for link in all_links if link not in indeed_links_we_already_have
    ]
    for link in only_new_links:
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


async def main(job_title, indeed_links_we_already_have, SKILLS):
    # Import this function to collect vacancies for a given job title.
    async with aiohttp.ClientSession() as session:
        query = prepare_query(job_title)
        all_links = await scan_all_search_results(query, session)
        attempt = 1
        while attempt < 10:
            try:
                vacancies_without_skills = await fetch_all_vacancy_pages(
                    all_links, indeed_links_we_already_have, session
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
    await asyncio.sleep(60)
    return collected_jobs
