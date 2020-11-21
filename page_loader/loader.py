import pathlib
import re
from os import path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from page_loader import exceptions
from .logger import get_logger

logger = get_logger(__name__)

FILES_FOLDER_POSTFIX = '_files'
FILENAME_MAX_LENGTH = 255


def perform_request(url):
    response = requests.get(url)
    response.raise_for_status()

    return response


def sanitize_string(string):
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string)}"


def is_local_resource(page_url, resource_url):
    return urlparse(page_url).netloc == urlparse(resource_url).netloc


def cut_string(string, limit):
    if len(string) > limit:
        return f'{string[:100]}...'
    return string


def download_files(page_url, soup, tag, src_attribute, file_folder_path):
    file_folder_name = path.split(file_folder_path)[-1]

    for element in soup.find_all(tag):
        if not element.has_attr(src_attribute):
            logger.warning(
                'Element "%s" has no source attribute, skipping',
                cut_string(str(element), 100)
            )
            continue

        absolute_url = urljoin(page_url, element[src_attribute])

        if not is_local_resource(page_url, absolute_url):
            logger.warning(
                'Element "%s" is external, skipping',
                cut_string(str(element), 200)
            )
            continue

        parsed_url = urlparse(absolute_url)
        response = perform_request(absolute_url)
        file_data = response.content

        file_path, extension = path.splitext(
            f'{parsed_url.netloc}{parsed_url.path}'
        )
        file_name = f'{sanitize_string(file_path)[:FILENAME_MAX_LENGTH]}' \
                    f'{extension}'
        file_path = path.join(file_folder_path, file_name)

        element[src_attribute] = path.join(file_folder_name, file_name)

        with open(file_path, 'wb') as file:
            file.write(file_data)
            logger.info('Saving asset %s', file_path)


def download(url, destination):
    parsed_url = urlparse(url)
    url_without_scheme = f'{parsed_url.netloc}{parsed_url.path}'
    site_name = sanitize_string(url_without_scheme)
    output_file_path = f'{path.join(destination, site_name)}.html'
    file_folder_path = path.join(
        destination,
        f'{site_name}{FILES_FOLDER_POSTFIX}'
    )

    try:
        pathlib.Path(file_folder_path).mkdir(parents=True, exist_ok=True)

        with open(output_file_path, 'w') as file:
            data = perform_request(url)
            soup = BeautifulSoup(data.text, 'html.parser')

            download_files(url, soup, 'img', 'src', file_folder_path)
            download_files(url, soup, 'link', 'href', file_folder_path)
            download_files(url, soup, 'script', 'src', file_folder_path)

            file.write(soup.prettify())

            logger.info('Saving page %s', output_file_path)

    except requests.exceptions.HTTPError as e:
        raise exceptions.HttpError(e.args[0]) from e
    except requests.exceptions.MissingSchema as e:
        raise exceptions.MissingSchema(e) from e
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

    return output_file_path
