#!/usr/bin/env python
import logging

from time import sleep

from config.config import config
from cryptodiversify.bot import CryptoDiversify

log_level = "DEBUG" if config['debug'] else "INFO"
logging.basicConfig(
    level=log_level,
    format="[%(asctime)s][%(threadName)16s][%(module)6s][%(levelname)8s] %(message)s")
logging.getLogger("requests").setLevel(logging.WARNING)
log = logging.getLogger()

bot = CryptoDiversify(config)
bot.start()

# Keep the main thread alive
while True:
    sleep(1)
