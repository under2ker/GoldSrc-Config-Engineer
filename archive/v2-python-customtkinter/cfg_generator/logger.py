import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR = os.path.join(os.environ.get("APPDATA", "."), "GoldSrcConfigEngineer", "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "GoldSrcConfigEngineer.log")
_FMT = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def setup_logger():
    os.makedirs(_LOG_DIR, exist_ok=True)
    logger = logging.getLogger("GoldSrcConfigEngineer")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return logger

    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=1_048_576,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_FMT)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_FMT)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False
    return logger


log = setup_logger()
