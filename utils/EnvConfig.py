import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def running_on_server() -> bool:
    return _is_env_variable_set_for("RUNNING_ON_SERVER")


def http_server_port() -> int:
    return _get_env_variable_for("HTTP_SERVER_PORT", 7624)


def user_pass_chochko() -> Optional[str]:
    return _get_env_variable_for("USER_PASS_CHOCHKO", None)


def notifier_server_address() -> str:
    return "http://notifier:9876" if running_on_server() else "http://localhost:9876"


def rest_server_base_url() -> str:
    return "http://rest-server-combined:9999" if running_on_server() else "http://localhost:9090"


def binance_api_key() -> Optional[str]:
    return _get_env_variable_for("BINANCE_API_KEY", None)


def binance_secret_key() -> Optional[str]:
    return _get_env_variable_for("BINANCE_KEY_SECRET", None)


def _get_env_variable_for(env_name, default):
    return __get_env_variable(env_name) if _is_env_variable_set_for(env_name) else default


def _is_env_variable_set_for(key: str) -> bool:
    return __get_env_variable(key) is not None


def __get_env_variable(key):
    return os.getenv(key)

