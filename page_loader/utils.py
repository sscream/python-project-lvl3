import re
from functools import wraps

import requests

from page_loader import exceptions


def sanitize_string(string):
    """
    Replace all non-alphanumeric characters to hyphens
    :param string:
    :return:
    """
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string)}"


def handle_errors(func):  # noqa: C901
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            raise exceptions.HttpError(e.args[0]) from e
        except requests.exceptions.MissingSchema as e:
            raise exceptions.MissingSchema(e) from e
        except requests.exceptions.ConnectionError as e:
            raise exceptions.ConnectionError(e) from e
        except requests.exceptions.RequestException as e:
            raise exceptions.RequestError('URL is unreachable') from e
        except PermissionError as e:
            raise exceptions.PermissionDenied(
                'Can not get access to destination folder, permission denied'
            ) from e
        except NotADirectoryError as e:
            raise exceptions.DestinationNotADirectoryError(
                'Destination is not a directory'
            ) from e
        except FileNotFoundError as e:
            raise exceptions.DirectoryNotFound(
                'Destination directory not found'
            ) from e

    return inner


def perform_request(url):
    response = requests.get(url)
    response.raise_for_status()

    return response
