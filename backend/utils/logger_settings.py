import logging
import sys
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s"
)

stream_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("app.log")

stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.handlers = [stream_handler,file_handler]

logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "app.log",
    maxBytes=1024*1024,
    backupCount=5
)

