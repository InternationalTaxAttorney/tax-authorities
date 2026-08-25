import argparse

from tax_authorities.download import download_data


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('download-data')

    args = parser.parse_args()

    if args.command == 'download-data':
        data_dirs = download_data()
        for name, path in data_dirs.items():
            print(f'{name} data downloaded to: {path}')
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
