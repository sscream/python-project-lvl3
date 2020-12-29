import os
import logging
import pathlib

from progress.bar import Bar
import requests

from .page_processor import process_page
from .request import perform_request
from .storage import save_html_page, download_resource

FILES_FOLDER_POSTFIX = '_files'

RESOURCE_ELEMENTS_ATTRIBUTES_MAP = {
    'img': 'src',
    'link': 'href',
    'script': 'src'
}


def download(url, destination, resources_to_download=None):
    assert_directory_valid(destination)

    if resources_to_download is None:
        resources_to_download = RESOURCE_ELEMENTS_ATTRIBUTES_MAP

    html_page_data = perform_request(url).text

    process_results = process_page(
        html=html_page_data,
        page_url=url,
        destination=destination,
        files_folder_name_postfix=FILES_FOLDER_POSTFIX,
        resources_to_download=resources_to_download
    )

    modified_html_page_data, html_page_file_path, file_folder_path, resources \
        = process_results

    resources_count = len(resources)

    logging.debug(
        'Local resources count: %s, list: %s', resources_count, '\n\n'.join([
            f'url: {resource_url} \ndestination: {resource_destination}'
            for resource_url, resource_destination in resources
        ])
    )

    with Bar('Processing', max=resources_count + 1) as progress_bar:
        save_html_page(modified_html_page_data, html_page_file_path)
        progress_bar.next()

        if resources:
            pathlib.Path(file_folder_path).mkdir(exist_ok=True)
            logging.info(
                'Files folder was created, path: %s', file_folder_path
            )

            for resource_url, resource_destination in resources:
                try:
                    download_resource(resource_url, resource_destination)
                    logging.info('Saving asset %s', resource_destination)
                except requests.HTTPError as e:
                    logging.warning(str(e))
                    continue

                progress_bar.next()

    return html_page_file_path


def assert_directory_valid(directory):
    if not os.path.exists(directory):
        raise FileNotFoundError(f'No such file or directory: `{directory}`')

    if not os.path.isdir(directory):
        raise NotADirectoryError(f'Not a directory: `{directory}`')

    if not os.access(directory, os.W_OK):
        raise PermissionError(f'Read-only file system: `{directory}`')
