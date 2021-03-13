import logging


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("trade")


def log(data):
    print(data)


def info(data):
    logger.info(data)


def debug(data):
    logger.debug(data)


def warning(data):
    logger.warning(data)


def error(data):
    logger.error(data)
