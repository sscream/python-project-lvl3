import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Download web page')
    parser.add_argument('url', type=str)
    parser.add_argument('--output', type=str)
    args = parser.parse_args()

    return args.url, args.output
