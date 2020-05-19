import re
import random
import asyncio
import collections
from multiprocessing import Pool

import nltk
import aiohttp
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from aiohttp.client_exceptions import ClientPayloadError


headers = {
    "user-agent": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    ]
}
RANDOM_AGENT = random.choice(headers["user-agent"])

try:
    russian_stopwords = stopwords.words("russian")
    english_stopwords = stopwords.words("english")
    STOPWORDS = [*russian_stopwords, *english_stopwords]
except LookupError:
    nltk.download("stopwords")

with open("static/tech.txt", mode="r", encoding="utf-8",) as file:
    TECH = file.read().replace(",", "").splitlines()


def ask_vacancy(raw_query):
    # Ask for vacancy to parse.
    query = f'"{raw_query}"'
    return query


async def scan_single_search_page(query, page_num, session):
    # Scan search page for vacancy links.
    payload = {
        "text": query,
        "page": page_num,
    }
    async with session.get("https://hh.ru/search/vacancy", params=payload) as resp:
        html = await resp.text()
        soup = BeautifulSoup(html, "lxml")
        all_vacancies = soup.find_all("a", href=re.compile(r"https://hh.ru/vacancy/"))
        # Extract valid links to vacancy pages and clean their tails.
        links = set(vacancy["href"].split("?")[0] for vacancy in all_vacancies)
        return links


async def scan_all_search_results(query, session):
    # Schedule all search results for further asynchronous processing.
    tasks = list()
    for page_num in range(100):
        task = asyncio.create_task(scan_single_search_page(query, page_num, session))
        tasks.append(task)
    all_sets = await asyncio.gather(*tasks)
    # Unpack the list of sets into a single set of all links.
    all_links = set()
    for s in all_sets:
        all_links.update(s)
    return all_links


async def fetch_vacancy_page(link, session):
    # Extract vacancy description from the provided link.
    async with session.get(link) as resp:
        try:
            html = await resp.text()
            soup = BeautifulSoup(html, "lxml")
            description = soup.find(attrs={"data-qa": "vacancy-description"}).text
            return description
        # except AttributeError:
        #     print(f"AttributeError occurred with the following URL: {link}")
        #     pass
        except ClientPayloadError:
            print(f"ClientPayloadError occurred with the following URL: {link}")
            pass


async def fetch_all_vacancy_pages(all_links, session):
    # Schedule all the vacancy pages for further asynchronous processing.
    tasks = list()
    for link in all_links:
        task = asyncio.create_task(fetch_vacancy_page(link, session))
        tasks.append(task)
    all_descriptions = await asyncio.gather(*tasks)
    return all_descriptions


def process_vacancy_descriptions(description):
    # Extract keywords from the descriptions and count each keyword.
    counts = dict()
    # This pattern doesn't identify phrases like "Visual Basic .NET"!
    pattern = r"\w+\S+\w+|[a-zA-Z]+[+|#]+|\S+[a-zA-Z]|\w+"
    if description != None:
        separated_words = re.findall(pattern, description.casefold())
        # Clean from the unnecessary stopwords.
        cleaned_words = (word for word in separated_words if word not in STOPWORDS)
        for word in cleaned_words:
            case_insensitive_counts = (key.casefold() for key in counts)
            case_insensitive_tech = [element.casefold() for element in TECH]

            # Option 1. Rate technologies by frequency.
            if word in case_insensitive_counts and word in case_insensitive_tech:
                position = case_insensitive_tech.index(word)
                counts[TECH[position]] += 1
            elif word not in case_insensitive_counts and word in case_insensitive_tech:
                position = case_insensitive_tech.index(word)
                counts[TECH[position]] = 1
            else:
                pass

            # Option 2. Identify new technologies in the entire list of words.
            # if word in case_insensitive_counts:
            #     counts[word] += 1
            # else:
            #     counts[word] = 1

        return counts
    else:
        pass


def unite_counts(tupled_separate_counts):
    # Unite all the dicts created by multiprocessing.
    super_dict = collections.defaultdict(list)
    for count in tupled_separate_counts:
        if count != None:
            for k, v in count.items():
                super_dict[k].append(v)
        else:
            pass
    united_counts = {k: sum(v) for k, v in super_dict.items()}
    return united_counts


def show_skills(united_counts):
    # Sort key, value pairs by value in descending order and slice the first 20 items.
    sorted_counts = sorted(united_counts.items(), key=lambda x: x[1], reverse=True)[:20]
    # for pair in sorted_counts:
    #     print(f'"{pair[0]}" – {pair[1]}')
    return sorted_counts


async def main(raw_query):
    async with aiohttp.ClientSession(headers={"user-agent": RANDOM_AGENT}) as session:
        query = ask_vacancy(raw_query)
        all_links = await scan_all_search_results(query, session)
        all_descriptions = await fetch_all_vacancy_pages(all_links, session)
        with Pool() as p:
            separate_counts = p.imap_unordered(
                process_vacancy_descriptions, all_descriptions
            )
            tupled_separate_counts = tuple(separate_counts)
            united_counts = unite_counts(tupled_separate_counts)
            sorted_counts = show_skills(united_counts)
    return sorted_counts


# if __name__ == "__main__":
#     raw_query = "junior python developer"
#     asyncio.run(main(raw_query))
