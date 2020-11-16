import os
import pathlib
import tempfile

import requests_mock

from page_loader import download

FIXTURES_FOLDER = pathlib.Path(__file__).parent.absolute().joinpath('fixtures')


def _read_file(*path_parts, mode='r'):
    with open(os.path.join(*path_parts), mode) as file:
        return file.read()


def _assert_html_files_equal(file1_data, file2_data):
    assert ''.join(file1_data.split()) == ''.join(file2_data.split())


def test_page_loader():
    url = 'http://some.ru/site'
    img_url = 'http://some.ru/assets/img.png'

    web_page_data = _read_file(FIXTURES_FOLDER, 'web_page.html')
    img_data = _read_file(FIXTURES_FOLDER, 'assets', 'img.png', mode='rb')

    with requests_mock.Mocker() as mock:
        mock.get(url, text=web_page_data)
        mock.get(img_url, content=img_data)

        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = download(url, tmpdir)

            img_folder = os.path.join(tmpdir, 'some-ru-site_files')

            assert file_path.split('/')[-1] == 'some-ru-site.html'
            assert os.path.exists(file_path)
            assert os.path.exists(
                os.path.join(img_folder, 'some-ru-assets-img.png')
            )
            assert _read_file(
                img_folder, 'some-ru-assets-img.png', mode='rb'
            ) == img_data

            _assert_html_files_equal(
                _read_file(file_path),
                _read_file(FIXTURES_FOLDER, 'expected_web_page.html')
            )
