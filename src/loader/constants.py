"""
Loads configuration from environment variables and `.env` files.

By default, the values defined in the classes are used, these can be overridden by an env var with the same name.

An `.env` file is used to populate env vars, if present.
"""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):
    """Our default configuration for models that should load from .env files."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


class _Dragonfly(EnvConfig, env_prefix="dragonfly"):
    """Configuration for the Dragonfly API."""

    base_url: str = "https://dragonfly.vipyrsec.com"
    auth0_domain: str = "vipyrsec.us.auth0.com"
    client_id: SecretStr = ""
    client_secret: SecretStr = ""
    username: SecretStr = ""
    password: SecretStr = ""
    audience: str = "https://dragonfly.vipyrsec.com"


Dragonfly = _Dragonfly()
