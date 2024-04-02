import logging
import sys

from app.utils.pathmgr import PathManager


def get_logger(name="app", level=logging.DEBUG) -> logging.Logger:
    """Logging to logfile as well as to console"""
    FORMAT = "[%(levelname)s  %(name)s %(module)s:%(lineno)s - %(funcName)s() - %(asctime)s]\n\t %(message)s \n"
    TIME_FORMAT = "%d.%m.%Y %I:%M:%S %p"
    FILENAME = PathManager.get_log_dir().joinpath("limo_log.log")

    logging.basicConfig(
        format=FORMAT
        , datefmt=TIME_FORMAT
        , level=level
        , filename=FILENAME
    )

    logger_instance = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    logger_instance.addHandler(handler)
    return logger_instance


logger = get_logger(__name__)

logger.info("Limo logger initiated")
