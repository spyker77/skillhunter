from ..hh_scraper import HHScraper
from ..shared.generic_command import GenericScrapingCommand


class Command(GenericScrapingCommand):
    help = "Scrape and process job vacancies from hh.ru"

    scraper_class = HHScraper
    site_name = "hh.ru"
