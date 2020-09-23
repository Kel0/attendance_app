import json
import logging.config

from services.auth import Auth


def setup_logging(path: str = "../logging.json") -> None:
    with open(path, "rt") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


auth = Auth()

auth.login(username="username", password="password")
