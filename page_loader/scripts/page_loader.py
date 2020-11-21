import sys

from page_loader import download
from page_loader.cli import parse_args
from page_loader.exceptions import PageLoaderError
from page_loader.logger import get_logger

logger = get_logger(__name__)


def main():
    url, output = parse_args()

    try:
        download(url, output)
    except PageLoaderError as e:
        logger.error(e)
        sys.exit(e.error_number)
