from os import path
import re
import requests


def prepare_file_name(url):
    pattern = r'[^\d\w]'
    return f"{re.sub(pattern, '-', url.split('//')[1])}.html"


def download(url, destination):
    output_file_path = path.join(destination, prepare_file_name(url))

    with open(output_file_path, 'w') as file:
        data = requests.get(url)
        file.write(data.text)

    return output_file_path
