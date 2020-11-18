import os
import pathlib
import tempfile

import requests_mock
from bs4 import BeautifulSoup

from page_loader import download

FIXTURES_FOLDER = pathlib.Path(__file__).parent.absolute().joinpath('fixtures')


def _read_file(*path_parts, mode='r'):
    with open(os.path.join(*path_parts), mode) as file:
        return file.read()


def _assert_html_files_equal(file1_data, file2_data):
    assert BeautifulSoup(file1_data, 'html.parser').prettify() \
           == BeautifulSoup(file2_data, 'html.parser').prettify()


def test_page_loader():
    host = 'http://some.ru'

    url = f'{host}/site'
    img_url = f'{host}/assets/img.png'
    css_url = f'{host}/assets/application.css'
    js_url = f'{host}/assets/runtime.js'

    web_page_data = _read_file(FIXTURES_FOLDER, 'web_page.html')
    img_data = _read_file(FIXTURES_FOLDER, 'assets', 'img.png', mode='rb')
    css_data = _read_file(FIXTURES_FOLDER, 'assets', 'application.css')
    js_data = _read_file(FIXTURES_FOLDER, 'assets', 'runtime.js')

    with requests_mock.Mocker() as mock:
        mock.get(url, text=web_page_data)
        mock.get(img_url, content=img_data)
        mock.get(css_url, text=css_data)
        mock.get(js_url, text=js_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = download(url, tmpdir)

            files_folder = os.path.join(tmpdir, 'some-ru-site_files')

            assert file_path.split('/')[-1] == 'some-ru-site.html'
            assert _read_file(
                files_folder, 'some-ru-assets-img.png', mode='rb'
            ) == img_data
            assert _read_file(
                files_folder, 'some-ru-assets-application.css'
            ) == css_data
            assert _read_file(
                files_folder, 'some-ru-assets-runtime.js'
            ) == js_data

            _assert_html_files_equal(
                _read_file(file_path),
                _read_file(FIXTURES_FOLDER, 'expected_web_page.html')
            )
