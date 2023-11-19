from ..indeed_scraper import IndeedScraper
from ..shared.generic_command import GenericScrapingCommand


class Command(GenericScrapingCommand):
    help = "Scrape and process job vacancies from indeed.com"

    scraper_class = IndeedScraper
    site_name = "indeed.com"
