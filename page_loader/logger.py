import logging
import logging.config

logging_config = dict(
    version=1,
    formatters={
        'format': {
            'format': '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
        }
    },
    handlers={
        'handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'format',
            'level': logging.DEBUG
        }
    },
    root={
        'handlers': ['handler'],
        'level': logging.DEBUG,
    },
)


def get_logger(name):
    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)
