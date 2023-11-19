from ..sh_scraper import SHScraper
from ..shared.generic_command import GenericScrapingCommand


class Command(GenericScrapingCommand):
    help = "Scrape and process job vacancies from simplyhired.com"

    scraper_class = SHScraper
    site_name = "simplyhired.com"
