"""Module to configure the logger."""

import logging
import os
from datetime import datetime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# HANDLERS
# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
logs_dir = "./.logs"
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)
filename = datetime.today().strftime("%Y%m%d") + ".log"
file_handler = logging.FileHandler(os.path.join(logs_dir, filename))
file_handler.setLevel(logging.DEBUG)

# FORMATTERS
# Console formatter
console_format = logging.Formatter("%(levelname)s - %(message)s")
console_handler.setFormatter(console_format)

# File formatter
file_format = logging.Formatter("%(levelname)s - %(asctime)s - %(message)s")
file_handler.setFormatter(file_format)

# CRAFTING LOGGER
# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
