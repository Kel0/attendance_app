import json
import logging
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup as bs

from .utils import HEADERS, get_csrf_token, get_today_date

logger = logging.getLogger(__name__)


class Auth:
    """
    Authenticate methods class
    """

    def __init__(self) -> None:
        self.csrf_token = get_csrf_token()
        self.headers = HEADERS
        self.login_url = "https://zhambyltipo.kz/kk/site/login"
        self.logout_url = "https://zhambyltipo.kz/site/logout"

    def login(self, username: str, password: str) -> Optional[requests.Session]:
        """
        Login to account

        :param username: Username
        :param password: Password
        :return: Logged in requests.Session object
        """
        data: Dict[str, Optional[str]] = {
            "_csrf": self.csrf_token,
            "LoginForm[username]": username,
            "LoginForm[password]": password,
            "login-button": "",
        }

        with requests.Session() as session:
            login_response: requests.Response = session.post(
                url=self.login_url, headers=self.headers, data=data
            )  # login post request
            logger.info("Logging in...")

            if login_response.status_code == 200:
                return session
            else:
                logger.warning(f"Login failed | {login_response.status_code}")
                return None

    def logout(self) -> bool:
        """
        Logout from accout

        :return: if response.status_code is 200 returns True else False
        """
        data: Dict[str, Optional[str]] = {
            "_csrf": self.csrf_token,
        }

        with requests.Session() as session:
            response: requests.Response = session.post(
                url=self.logout_url, headers=self.headers, data=data
            )  # logout post request
            logger.info("Logging out...")

            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Logout failed | {response.status_code}")
                return False


class SiteEvents:
    def __init__(self, login_session: requests.Session):
        self.login_session = login_session

    @staticmethod
    def write_schedule(data: List[Dict[str, str]]) -> None:
        """
        Write schedule to json file

        :param data: List of dicts which contains info about time and subject's remote lesson link.
            {"time": "09:00", "link": "some_link"}.
        """
        with open("schedule.json", "w+") as f:
            f.truncate()
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_todays_schedule(self) -> Optional[List[Dict[str, str]]]:
        """
        Get today's schedule

        :return objects: List of dicts which contains info about time and subject's remote lesson link.
            {"time": "09:00", "link": "some_link"}.
        """
        today_date = get_today_date()
        response: requests.Response = self.login_session.get(
            url="https://zhambyltipo.kz/admin/student/schedules", headers=HEADERS
        )

        soup = bs(response.content, "lxml")
        schedules = soup.find("table", attrs={"id": "schedules"})

        schedules_dates = schedules.find("thead").find_all("th")  # Get topics
        schedules_objects = schedules.find("tbody").find_all("tr")  # Get contents

        for key, schedules_date in enumerate(schedules_dates):
            date_span = schedules_date.find("span", attrs={"class": "text-muted"})
            if date_span is None:  # skip if date is None
                continue

            date: str = date_span.text.strip()
            if str(date) == str(today_date):
                objects: list = [
                    {
                        "time": [
                            time
                            for time in object_.find_all("td")[0].text.split(
                                " "
                            )  # split time text 09:00-09:35
                            if len(time) > 4
                        ][
                            0
                        ],  # get time of subject
                        "link": (
                            object_.find_all("td")[key]
                            .find("div")
                            .find("a")
                            .get("href")
                        ),  # get link of subject
                    }
                    for object_ in schedules_objects
                    if (
                        object_.find_all("td")[key].find("div").find("a")
                    )  # if element <a> is not None
                ]
                return objects
        return None

    def go_to_lesson(self) -> None:
        schedule = self.get_todays_schedule()
        if schedule is None:
            raise ValueError("No schedule")

        for subject in schedule:
            self.login_session.get(
                url=f"https://zhambyltipo.kz{subject['link']}", headers=HEADERS
            )
            logger.info(f"Requested https://zhambyltipo.kz{subject['link']}")
