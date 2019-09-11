#!/usr/bin/env python3
import base64
import csv
import functools
import os
import urllib
from urllib.parse import urlparse

import click
import json

from tqdm import tqdm


def build_graph(directory):
    with open("g.csv", "w") as csv_file:
        csv_file.write('Source,Target\n')
        # writer = csv.writer(csv_file, delimiter=',')
        for f in tqdm(os.listdir(directory)):
            with open(os.path.join(directory, f)) as file:
                o = json.load(file)
                url = base64.b64decode(o['url']).decode('cp1251')
                neighbours = o['references']
                for link in neighbours:
                    if not (link.startswith('http://')):
                        link = urllib.parse.urljoin(url, link)
                    csv_file.write('"' + url + '","' + link + '"\n')


@click.command()
@click.option('--directory', '-d', required=True)
def main(directory):
    build_graph(directory)


if __name__ == '__main__':
    main()
