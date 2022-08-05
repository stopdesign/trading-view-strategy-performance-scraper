import json

import requests
import logging

import EnvConfig
from utils import TimeUtils

program_name = "TradingView Scraper"
notification_type = "email"
sender = "TradingView Scraper"
recipients = ["konstantin.pl.vankov@gmail.com"]
base_url = EnvConfig.notifier_server_address()


def send_email_error(msg: str):
    r = requests.post(f'{base_url}/send', json=
    {
        "type": notification_type,
        "metadata": {
            "subject": f"{program_name} crashed",
            "sender": sender,
            "recipients": recipients,
            "body": [
                {
                    "text": msg,
                    "type": "plain"
                }
            ]
        }
    })
    __log_response(r)


def send_email(msg: str, attachments):
    payload = {
        "type": notification_type,
        "metadata": {
            "subject": f"{program_name} {TimeUtils.get_time_stamp()}",
            "sender": sender,
            "recipients": recipients,
            "body": [
                {
                    "text": msg,
                    "type": "plain"
                }
            ]
        }
    }
    r = requests.post(f'{base_url}/sendWithFiles',
                      files=attachments,
                      data=[("payload", json.dumps(payload))])
    __log_response(r)


def __log_response(r):
    # logging.info("Notifier response: " + str(r.status_code))
    # logging.info("Notifier response: " + r.text)
    pass
