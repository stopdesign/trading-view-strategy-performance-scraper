import logging
import signal
from contextlib import contextmanager
from datetime import datetime
import time


@contextmanager
def measure_time(msg=None):
    time_start = datetime.now()
    try:
        yield
    finally:
        time_end = datetime.now()
        time_spent = __format_time_delta_to_str(start_date=time_start, end_date=time_end)
        print_msg = msg.format(time_spent) if msg else f"It took {time_spent}."
        logging.info(print_msg)


def __format_time_delta_to_str(start_date: datetime, end_date: datetime) -> str:
    delta = end_date - start_date
    spent_millis = int(delta.microseconds / 1_000)
    spent_secs = delta.seconds
    spent_min = int(spent_secs / 60)
    spent_hours = int(spent_min / 60)
    if spent_hours > 0:
        rest_secs = spent_secs - spent_min * 60
        rest_mins = spent_min % 60
        return f"{spent_hours}h {rest_mins}min {rest_secs}s {spent_millis}ms"
    elif spent_min > 0:
        rest_secs = spent_secs - spent_min * 60
        return f"{spent_min}min {rest_secs}s {spent_millis}ms"
    elif spent_secs > 0:
        return f"{spent_secs}s {spent_millis}ms"
    else:
        return f"{spent_millis}ms"


@contextmanager
def timeout(duration):
    def timeout_handler(signum, frame):
        raise Exception(f'block timedout after {duration} seconds')
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(duration)
    yield
    signal.alarm(0)


def current_time():
    return datetime.now()


def get_date_from_str(date_str: str, time_format='%d-%b-%yT%H:%M:%S') -> datetime:
    return datetime.strptime(date_str, time_format)


def get_time_stamp_from(date: datetime, time_format='%d-%b-%yT%H:%M:%S') -> str:
    return date.strftime(time_format)


def to_UTC_str(time_millis: int, time_format: str = '%d-%b-%yT%H:%M:%S') -> str:
    return to_date_time_from(time_millis).strftime(time_format)


def to_date_time_from(time_millis: int) -> datetime:
    return datetime.fromtimestamp(time_millis / 1000.0)


def get_time_stamp() -> str:
    return get_time_stamp_formatted('%d-%b-%yT%H:%M:%S')


def get_time_stamp_formatted(time_format: str) -> str:
    return current_time().strftime(time_format)


def current_milli_time():
    return round(time.time() * 1000)


def is_today_the_same_day_as(date: datetime) -> bool:
    current = current_time()
    return current.day == date.day and current.month == date.month
