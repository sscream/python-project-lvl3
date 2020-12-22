import argparse


def get_argument_parser():
    parser = argparse.ArgumentParser(description='Download web page')
    parser.add_argument('url', type=str)
    parser.add_argument('--output', type=str)
    parser.add_argument(
        '--log-level', type=str,
        default='ERROR',
        choices=['INFO', 'DEBUG', 'WARNING']
    )

    return parser
