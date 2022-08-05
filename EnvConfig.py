import os


def running_on_server() -> bool:
    return _is_env_variable_set_for("RUNNING_ON_SERVER")


def filter_name(default: str = None) -> str:
    return _get_env_variable_for(env_name="FILTER_NAME", default=default)


def notifier_server_address() -> str:
    return "http://notifier:9876" if running_on_server() else "http://localhost:9876"


def _get_env_variable_for(env_name, default):
    return __get_env_variable(env_name) if _is_env_variable_set_for(env_name) else default


def _is_env_variable_set_for(key: str) -> bool:
    return __get_env_variable(key) is not None


def __get_env_variable(key):
    return os.getenv(key)

