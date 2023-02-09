import os
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr
import logging.config

load_dotenv()


class BotSettings(BaseSettings):
    bot_token: SecretStr = os.getenv("BOT_TOKEN")


class SiteApiSettings(BaseSettings):
    X_RapidAPI_Key: SecretStr = os.getenv("X_RapidAPI_Key")
    X_RapidAPI_Host: SecretStr = os.getenv("X_RapidAPI_Host")


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger()
logger_message = logging.getLogger('message')

# курс доллара
USD = 71.58
