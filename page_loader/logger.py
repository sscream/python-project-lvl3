import logging


def setup_logger(log_level):
    logging.basicConfig(
        level=logging.getLevelName(log_level),
        format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
