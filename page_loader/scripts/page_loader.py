import logging
import sys

from page_loader import download
from page_loader.cli import get_argument_parser
from page_loader.exceptions import PageLoaderError
from page_loader.logger import setup_logger


def _parse_arguments():
    argument_parser = get_argument_parser()
    args = argument_parser.parse_args()

    return args.url, args.output, args.log_level


def main():
    url, output, log_level = _parse_arguments()

    setup_logger(log_level)

    try:
        download(url, output)
    except PageLoaderError as e:
        logging.error(e)
        sys.exit(e.error_number)
    except Exception as e:
        logging.critical(e)
        sys.exit(1)
