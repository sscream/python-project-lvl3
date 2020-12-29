import logging
import re
from os import path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

FILENAME_MAX_LENGTH = 255


def process_page(
    html,
    page_url,
    destination,
    files_folder_name_postfix,
    resources_to_download
):
    soup = BeautifulSoup(html, 'html.parser')

    parsed_url = urlparse(page_url)
    url_without_scheme = f'{parsed_url.netloc}{parsed_url.path}'
    site_name = _sanitize_string(url_without_scheme)
    output_file_path = f'{path.join(destination, site_name)}.html'
    file_folder_name = f'{site_name}{files_folder_name_postfix}'
    file_folder_path = path.join(destination, file_folder_name)

    local_resources = _retrieve_local_resources(
        soup, page_url, resources_to_download
    )

    local_resources_paths = []

    for resource in local_resources:
        src_attribute = resources_to_download[resource.name]
        resource_absolute_url = urljoin(page_url, resource[src_attribute])

        parsed_url = urlparse(resource_absolute_url)

        file_path, extension = path.splitext(
            f'{parsed_url.netloc}{parsed_url.path}'
        )

        if resource_absolute_url == page_url:
            extension = '.html'

        file_name = f'{_sanitize_string(file_path)[:FILENAME_MAX_LENGTH]}' \
                    f'{extension}'

        resource[src_attribute] = path.join(file_folder_name, file_name)

        resource_file_destination = path.join(file_folder_path, file_name)

        local_resources_paths.append(
            (resource_absolute_url, resource_file_destination)
        )

    return (
        soup.prettify(formatter='html5'),
        output_file_path,
        file_folder_path,
        local_resources_paths
    )


def _filter_by_elements(soup, resources_attributes_map):
    return soup.find_all(
        lambda element:
            element.name in resources_attributes_map and element.get(
                resources_attributes_map[element.name]
            )
    )


def _retrieve_local_resources(soup, page_url, resource_attributes):
    local_resources = []

    def _cut_string(string, limit=100):
        if len(string) > limit:
            return f'{string[:100]}...'
        return string

    for resource in _filter_by_elements(soup, resource_attributes):
        src_attribute = resource_attributes[resource.name]
        absolute_url = urljoin(page_url, resource[src_attribute])

        if not urlparse(page_url).netloc == urlparse(absolute_url).netloc:
            logging.warning(
                'Element "%s" is external, skipping',
                _cut_string(str(resource), 200)
            )
            continue

        local_resources.append(resource)

    return local_resources


def _sanitize_string(string):
    """
    Replace all non-alphanumeric characters to hyphens
    :param string:
    :return:
    """
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string.rstrip('/'))}"
