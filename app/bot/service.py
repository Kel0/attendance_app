import datetime
import time
from typing import Dict, List, Optional

import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from app.services.swagger import Auth, SiteEvents


def _calc_lesson_time(minute: int, multiplayer: int) -> int:
    if minute + multiplayer > 60:
        return minute + multiplayer - 60
    return minute + multiplayer


class Bot:
    def __init__(self, username: str, password: str, is_windows: bool = False):
        self.username = username
        self.password = password
        self.login_url = "https://zhambyltipo.kz/kk/site/login"

        if is_windows:
            geckodriver_autoinstaller.install()

    def _login(self, headless: bool = True) -> webdriver:
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")

        driver = webdriver.Firefox(options=options)  # Web driver

        driver.get(self.login_url)
        username_input = driver.find_element_by_css_selector("#username")
        password_input = driver.find_element_by_css_selector("#password")
        login_button = driver.find_element_by_xpath("//button[@name='login-button']")

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_button.click()

        return driver

    def _scrape_schedule(self) -> Optional[List[Dict[str, str]]]:
        auth = Auth()
        logged_in_session = auth.login(self.username, self.password)

        if logged_in_session is None:
            raise ValueError("Logging in failed")

        site = SiteEvents(logged_in_session)
        schedule = site.get_todays_schedule()

        return schedule

    def wait_time(self, subject_minute: int, current_minute: int):
        wait_time: int = int(abs(subject_minute - current_minute) * 60)
        time.sleep(wait_time)

    def go_to_lesson(self, headless: bool = True) -> None:
        now = datetime.datetime.now()
        driver = self._login(headless)
        schedule = self._scrape_schedule()

        if schedule is None:
            return None

        for subject in schedule:
            sub_hour, sub_min = subject["time"].split(":")
            subject_hour: int = int(sub_hour)
            subject_minute: int = int(sub_min)

            if subject_hour == now.hour and now.minute > _calc_lesson_time(
                subject_minute, 35
            ):
                continue

            elif (
                subject_hour == now.hour
                or subject_hour == now.hour - 1
                and now.minute < _calc_lesson_time(subject_minute, 35)
            ):
                driver.get(f"https://zhambyltipo.kz{subject['link']}")
                self.wait_time(subject_minute, now.minute)  # Wait until lesson is end
                break

        driver.close()
        return None
