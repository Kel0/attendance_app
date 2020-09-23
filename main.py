import json
import logging
import logging.config

from app.bot.service import Bot
from app.services.swagger import Auth, SiteEvents
from app.services.utils import read_json_file
from platform import platform


def setup_logging(path: str = "logging.json") -> None:
    with open(path, "rt") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


def scrape_schedule(creds_file_path: str) -> None:
    auth = Auth()
    credentials: dict = read_json_file(creds_file_path)

    logged_session = auth.login(
        username=credentials["username"], password=credentials["password"]
    )  # login
    site = SiteEvents(logged_session)  # Provide logged in session to class

    r = site.get_todays_schedule()  # Get today's schedule
    site.write_schedule(r)  # writes it into file


def activate_bot(creds_file_path: str, headless: bool = True) -> None:
    credentials: dict = read_json_file(creds_file_path)

    is_windows = False
    if "windows" in platform().lower():
        is_windows = True

    bot = Bot(username=credentials["username"], password=credentials["password"], is_windows=is_windows)
    bot.go_to_lesson(headless=headless)


if __name__ == "__main__":
    import sys

    setup_logging()
    logger = logging.getLogger(__name__)

    if sys.argv[1] == "scrape":
        logger.info("Scraper started its' work")
        scrape_schedule(creds_file_path="credentials.json")
        logger.info("Finished")

    elif "bot" in sys.argv[1]:
        headless: bool = bool(int(sys.argv[1].split("_")[1]))
        logger.info("Launching the bot")
        activate_bot(headless=headless, creds_file_path="credentials.json")
        logger.info("Finished")
