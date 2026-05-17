"""
Example configuration for AKImaxLink.

Copy this file to `config.py` (inside the AKImaxLink folder) and fill in real
values or set the corresponding environment variables. The real `config.py`
is in `.gitignore` to avoid leaking secrets.
"""

import os
from os import getenv


class Var(object):
    # Telegram API credentials (get these from https://my.telegram.org)
    API_ID = int(getenv("API_ID", "123456"))
    API_HASH = getenv("API_HASH", "your_api_hash_here")
    BOT_TOKEN = getenv("BOT_TOKEN", "123456:ABCDEF-ghIJKLmnoP")
    SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))

    # Channel IDs (use -100... for channels)
    LOG_CHANNEL = int(getenv("LOG_CHANNEL", "-1000000000000"))
    BIN_CHANNEL = int(getenv("BIN_CHANNEL", "-1000000000000"))

    # Database (MongoDB) configuration
    DATABASE_URI = getenv("DATABASE_URI", "mongodb://user:pass@host:27017")
    DATABASE_NAME = getenv("DATABASE_NAME", "akimax_db")
    COLLECTION_NAME = getenv("COLLECTION_NAME", "files")

    # Owner / admin user id
    OWNER_ID = int(getenv("OWNER_ID", "123456789"))

    # Multi-client support (optional)
    MULTI_CLIENT = getenv("MULTI_CLIENT", "False").lower() in ("1", "true", "yes")
    # If using MULTI_CLIENT you can provide tokens via env vars:
    # MULTI_TOKEN1, MULTI_TOKEN2, ...

    # Web server settings
    PORT = int(getenv("PORT", "8080"))
    NO_PORT = getenv("NO_PORT", "False").lower() in ("1", "true", "yes")
    WEB_SERVER_BIND_ADDRESS = getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
    FQDN = getenv("FQDN", "example.com")
    HAS_SSL = getenv("HAS_SSL", "False").lower() in ("1", "true", "yes")
    URL = ("https://{}/".format(FQDN) if HAS_SSL else "http://{}/".format(FQDN))

    # Additional optional settings
    # -- Add any project-specific overrides here --
