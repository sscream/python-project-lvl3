import logging
import pathlib
import re
from os import path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from progress.bar import Bar

from page_loader import exceptions

logger = logging.getLogger(__name__)

FILES_FOLDER_POSTFIX = '_files'
FILENAME_MAX_LENGTH = 255

RESOURCE_ELEMENTS_ATTRIBUTES_MAP = {
    'img': 'src',
    'link': 'href',
    'script': 'src'
}


def perform_request(url):
    response = requests.get(url)
    response.raise_for_status()

    return response


def _sanitize_string(string):
    """
    Replace all non-alphanumeric characters to hyphens
    :param string:
    :return:
    """
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string)}"


def _filter_by_elements(soup, resources_attributes_map):
    return soup.find_all(
        lambda element:
            element.name in resources_attributes_map
            and element.get(resources_attributes_map[element.name])
    )


def _retrieve_local_resources(soup, site_url, resource_attributes):
    local_resources = []

    def _cut_string(string, limit=100):
        if len(string) > limit:
            return f'{string[:100]}...'
        return string

    for resource in _filter_by_elements(soup, resource_attributes):
        src_attribute = resource_attributes[resource.name]
        absolute_url = urljoin(site_url, resource[src_attribute])

        if not urlparse(site_url).netloc == urlparse(absolute_url).netloc:
            logger.warning(
                'Element "%s" is external, skipping',
                _cut_string(str(resource), 200)
            )
            continue

        local_resources.append(resource)

    return local_resources


def _download_resource(resource_url, destination):
    file_folder_name = path.split(destination)[-1]

    parsed_url = urlparse(resource_url)
    response = perform_request(resource_url)
    file_data = response.content

    file_path, extension = path.splitext(
        f'{parsed_url.netloc}{parsed_url.path}'
    )
    file_name = f'{_sanitize_string(file_path)[:FILENAME_MAX_LENGTH]}' \
                f'{extension}'
    file_path = path.join(destination, file_name)

    with open(file_path, 'wb') as file:
        file.write(file_data)
        logger.info('Saving asset %s', file_path)

    return path.join(file_folder_name, file_name)


def download(url, destination, resources_to_download=None):
    if resources_to_download is None:
        resources_to_download = RESOURCE_ELEMENTS_ATTRIBUTES_MAP

    parsed_url = urlparse(url)
    url_without_scheme = f'{parsed_url.netloc}{parsed_url.path}'
    site_name = _sanitize_string(url_without_scheme)
    output_file_path = f'{path.join(destination, site_name)}.html'
    file_folder_path = path.join(
        destination,
        f'{site_name}{FILES_FOLDER_POSTFIX}'
    )

    try:
        data = perform_request(url)

        with open(output_file_path, 'w') as file:
            soup = BeautifulSoup(data.text, 'html.parser')

            local_resources = _retrieve_local_resources(
                soup, url, resources_to_download
            )

            pathlib.Path(file_folder_path).mkdir(parents=True, exist_ok=True)

            with Bar('Processing', max=len(local_resources) + 1) as bar:
                for resource in local_resources:
                    src_attribute = resources_to_download[resource.name]
                    absolute_url = urljoin(url, resource[src_attribute])

                    local_resource_url = _download_resource(
                        resource_url=absolute_url,
                        destination=file_folder_path
                    )

                    resource[src_attribute] = local_resource_url
                    bar.next()

                file.write(soup.prettify())
                bar.next()

                logger.info('Saving page %s', output_file_path)

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

    return output_file_path
