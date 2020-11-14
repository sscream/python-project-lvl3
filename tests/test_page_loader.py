import os

import pathlib
import tempfile

import requests_mock

from page_loader import download

FIXTURES_FOLDER = pathlib.Path(__file__).parent.absolute().joinpath('fixtures')


def _get_fixture_data(filename, folder=FIXTURES_FOLDER):
    return _read_file(pathlib.Path.joinpath(folder, filename))


def _read_file(path):
    with open(path, 'r') as file:
        return file.read()


def test_page_loader():
    url = 'http://some/site'
    fixture_data = _get_fixture_data('web_page.html')

    with requests_mock.Mocker() as mock:
        mock.get(url, text=fixture_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = download(url, tmpdir)

            assert file_path.split('/')[-1] == 'some-site.html'
            assert os.path.exists(file_path)
            assert _read_file(file_path) == fixture_data
