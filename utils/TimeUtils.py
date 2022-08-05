import logging
import signal
from contextlib import contextmanager
from datetime import datetime, time


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
    if spent_min > 0:
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


def get_time_stamp() -> str:
    return f"{datetime.now().strftime('%Y-%m-%d')}"
