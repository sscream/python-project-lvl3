import requests
import logging


def perform_request(url):
    logging.debug('Performing request, url: %s', url)
    response = requests.get(url)
    response.raise_for_status()

    return response
