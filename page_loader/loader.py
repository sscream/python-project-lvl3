import pathlib
import re
from os import path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

FILES_FOLDER_POSTFIX = '_files'
FILENAME_MAX_LENGTH = 255


def sanitize_string(string):
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', string)}"


def remove_schema_from_url(url):
    return url.split('//')[-1]


def download(url, destination):
    site_name = sanitize_string(remove_schema_from_url(url))
    output_file_path = f'{path.join(destination, site_name)}.html'
    file_folder_name = f'{site_name}{FILES_FOLDER_POSTFIX}'
    file_folder_path = path.join(destination, file_folder_name)

    pathlib.Path(file_folder_path).mkdir(parents=True)

    with open(output_file_path, 'w') as file:
        data = requests.get(url)
        soup = BeautifulSoup(data.text, 'html.parser')

        for img in soup.find_all('img'):
            src = urljoin(url, img['src'])
            img_data = requests.get(src).content
            file_path, extension = path.splitext(remove_schema_from_url(src))
            file_name = f'{sanitize_string(file_path)[:FILENAME_MAX_LENGTH]}' \
                        f'{extension}'
            img_file_path = path.join(file_folder_path, file_name)

            img['src'] = path.join(file_folder_name, file_name)

            with open(img_file_path, 'bw+') as img_file:
                img_file.write(img_data)

        file.write(soup.prettify())

    return output_file_path
