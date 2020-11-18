import pathlib
import re
from os import path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

FILES_FOLDER_POSTFIX = '_files'
FILENAME_MAX_LENGTH = 255


def sanitize_string(string):
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string)}"


def is_local_resource(page_url, resource_url):
    return urlparse(page_url).netloc == urlparse(resource_url).netloc


def download_files(
    page_url, soup, tag, src_attribute, file_folder_path, is_binary=False
):
    file_folder_name = path.split(file_folder_path)[-1]

    for element in soup.find_all(tag):
        absolute_url = urljoin(page_url, element[src_attribute])

        if not is_local_resource(page_url, absolute_url):
            continue

        parsed_url = urlparse(absolute_url)
        response = requests.get(absolute_url)

        if is_binary:
            file_data = response.content
        else:
            file_data = response.text

        file_path, extension = path.splitext(
            f'{parsed_url.netloc}{parsed_url.path}'
        )
        file_name = f'{sanitize_string(file_path)[:FILENAME_MAX_LENGTH]}' \
                    f'{extension}'
        file_path = path.join(file_folder_path, file_name)

        element[src_attribute] = path.join(file_folder_name, file_name)

        mode = 'bw' if is_binary else 'w'

        with open(file_path, mode) as file:
            file.write(file_data)


def download(url, destination):
    parsed_url = urlparse(url)
    url_without_scheme = f'{parsed_url.netloc}{parsed_url.path}'
    site_name = sanitize_string(url_without_scheme)
    output_file_path = f'{path.join(destination, site_name)}.html'
    file_folder_path = path.join(
        destination,
        f'{site_name}{FILES_FOLDER_POSTFIX}'
    )

    pathlib.Path(file_folder_path).mkdir(parents=True)

    with open(output_file_path, 'w') as file:
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        download_files(url, soup, 'img', 'src', file_folder_path, True)
        download_files(url, soup, 'link', 'href', file_folder_path)
        download_files(url, soup, 'script', 'src', file_folder_path)

        file.write(soup.prettify())

    return output_file_path
