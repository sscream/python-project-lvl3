import argparse

from page_loader import download


def main():
    parser = argparse.ArgumentParser(description='Download web page')
    parser.add_argument('url', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()

    download(args.url, args.output)
