import logging
import logging.config

logging_config = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'format': {
            'format': '[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
        }
    },
    handlers={
        'handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'format',
            'level': logging.INFO
        }
    },
    root={
        'handlers': ['handler'],
        'level': logging.INFO,
    },
)


def get_logger(name):
    logging.config.dictConfig(logging_config)
    return logging.getLogger(name)
