import json
import logging


def print_beautiful_json(data: dict):
    logging.info(json.dumps(data, indent=4))
