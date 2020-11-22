import logging
import sys

from page_loader import download
from page_loader.cli import parse_args
from page_loader.exceptions import PageLoaderError


def main():
    url, output, log_level = parse_args()

    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    logger = logging.getLogger(__name__)

    try:
        download(url, output)
    except PageLoaderError as e:
        logger.error(e)
        sys.exit(e.error_number)
    except Exception as e:
        logger.critical(e)
        sys.exit(1)
