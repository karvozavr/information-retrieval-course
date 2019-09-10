#!/usr/bin/env python3
import base64
import functools
import json
import multiprocessing
import os
import re
import xml.etree.ElementTree as ET

import click
from bs4 import BeautifulSoup
from tqdm import tqdm


class Document:

    def __init__(self, content: str, url: str, id: str, bytes_size: int):
        self.html = content
        self.url = url
        self.id = id
        self.bytes_size = bytes_size
        soup = BeautifulSoup(content, 'html.parser')
        self.references = list(filter(lambda x: x is not None, map(lambda link: link.get('href'), soup.find_all('a'))))
        excludes = [soup.find_all('script'), soup.find_all('style'), soup.find_all('meta')]
        for exclude in excludes:
            for tag in exclude:
                tag.extract()
        raw_text = soup.get_text(separator='\n')
        self.text = re.sub(r'\s+', '\n', raw_text)

    def save_html(self, path):
        with open(path, 'w', encoding='cp1251') as file:
            file.write(self.html)

    def save_text(self, path):
        with open(path, 'w') as file:
            file.write(self.text)

    def save(self, out_dir):
        html_path = os.path.join(out_dir, self.id + '.html')
        text_path = os.path.join(out_dir, self.id + '.txt')
        json_path = os.path.join(out_dir, self.id + '.json')

        self.save_html(html_path)
        self.save_text(text_path)

        info = {
            "html": html_path,
            "text": text_path,
            "url": self.url,
            "id": self.id,
            "bytes_size": self.bytes_size,
            "references": self.references
        }

        with open(json_path, 'w') as file:
            json.dump(info, file)


def process_file(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root.findall('./document')


def handle_document(document: ET.Element):
    content_encoded = document.find('./content').text
    binary_content = base64.b64decode(content_encoded)
    content = binary_content.decode('cp1251')
    url = document.find('./docURL').text
    doc_id = document.find('./docID').text
    return Document(content=content, url=url, id=doc_id, bytes_size=len(binary_content))


def save_processed_document(doc, output):
    handle_document(doc).save(output)


@click.command()
@click.option('--file', '-f', required=True)
@click.option('--output', '-o', required=True)
def main(file, output):
    os.makedirs(os.path.join(output, 'html'), exist_ok=True)
    os.makedirs(os.path.join(output, 'info'), exist_ok=True)
    os.makedirs(os.path.join(output, 'text'), exist_ok=True)

    pool = multiprocessing.Pool(4)
    mapper = functools.partial(save_processed_document, output=output)
    documents = process_file(file)
    for _ in tqdm(pool.imap_unordered(mapper, documents), total=len(documents)):
        pass


if __name__ == '__main__':
    main()
