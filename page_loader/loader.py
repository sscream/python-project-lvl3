import logging
import pathlib

from progress.bar import Bar

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

    with Bar('Processing', max=len(resources) + 1) as progress_bar:
        save_html_page(modified_html_page_data, html_page_file_path)
        progress_bar.next()

        if resources:
            pathlib.Path(file_folder_path).mkdir(exist_ok=True)

            for resource_url, resource_destination in resources:
                download_resource(resource_url, resource_destination)
                progress_bar.next()

                logging.info('Saving asset %s', resource_destination)

    return html_page_file_path
