from .request import perform_request


def save_html_page(page_data, destination):
    with open(destination, 'w') as html_file:
        html_file.write(page_data)


def download_resource(resource_url, resource_destination):
    response = perform_request(resource_url)

    if response.encoding is not None:
        resource_data = response.text
        write_mode = 'w'
    else:
        resource_data = response.content
        write_mode = 'wb'

    with open(resource_destination, write_mode) as file:
        file.write(resource_data)
