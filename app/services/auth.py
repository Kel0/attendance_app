import logging
from typing import Dict, Optional

import requests

from .utils import HEADERS, get_csrf_token

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

    def login(self, username: str, password: str):
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
            logger.info("Logging...")

            if login_response.status_code == 200:
                return login_response
            else:
                logger.warning(f"Login failed | {login_response.status_code}")

    def logout(self) -> bool:
        data: Dict[str, Optional[str]] = {
            "_csrf": self.csrf_token,
        }

        with requests.Session() as session:
            response: requests.Response = session.post(
                url=self.logout_url, headers=self.headers, data=data
            )  # login post request
            logger.info("Logging...")

            if response.status_code == 200:
                return True
            else:
                logger.warning(f"Logout failed | {response.status_code}")
                return False
