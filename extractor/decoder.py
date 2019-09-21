#!/usr/bin/env python3
import base64
import json
import os
import re
import xml.etree.ElementTree as ET
from pymystem3 import Mystem
import gc
import click
from bs4 import BeautifulSoup
from tqdm import tqdm

from subprocess import check_output

stop_words = {'г', '©'}

mystem = Mystem()


def get_stop_words(files):
    for file in files:
        with open(file) as f:
            for word in f:
                stop_words.add(word.split()[0])


get_stop_words(['stopwords/english', 'stopwords/russian'])


def is_not_stop_word(d):
    return not getLexOrText(d) in stop_words


def getText(d):
    return d['text'].lower()


def getLexOrText(d):
    if not d['analysis']:
        return getText(d)

    analysis = d['analysis'][0]
    return analysis['lex'] if 'lex' in analysis else getText(d)


def filter_text(text):
    # words_results = check_output([
    #     '/home/karvozavr/Downloads/mystem/mystem', '-n', '--format', 'json', '-'
    # ], universal_newlines=True, input=text).split('\n')

    words_results = mystem.analyze(text)

    words_results = filter(bool, words_results)
    words_results = list(filter(lambda x: 'analysis' in x, words_results))

    json_results = list(filter(is_not_stop_word, words_results))

    raw_content = " ".join(list(map(getText, json_results)))
    lexed_content = " ".join(list(map(getLexOrText, json_results)))

    return raw_content, lexed_content


class Document:

    def __init__(self, content: str, url: str, id: str, bytes_size: int):
        self.html = content
        self.url = base64.b64decode(url).decode('cp1251')
        self.id = id
        self.bytes_size = bytes_size
        soup = BeautifulSoup(content, 'lxml')
        title = soup.title
        self.title = title.string if title is not None else ''
        self.references = list(filter(lambda x: x is not None, map(lambda link: link.get('href'), soup.find_all('a'))))
        excludes = [soup.find_all('script'), soup.find_all('style'), soup.find_all('meta')]
        for exclude in excludes:
            for tag in exclude:
                tag.extract()
        raw_text = soup.get_text(separator=' ')
        self.text = re.sub(r'\s+', ' ', raw_text)

    def save_html(self, path):
        with open(path, 'w', encoding='cp1251') as file:
            file.write(self.html)

    def save_text(self, path):
        with open(path, 'w') as file:
            file.write(self.text)

    def save(self, out):

        raw_content, stem_content = filter_text(self.text)

        info = {
            "content": raw_content,
            "stem_content": stem_content,
            "title": self.title,
            "url": self.url,
            "id": self.id,
            "bytes_size": self.bytes_size,
            "references": self.references
        }

        s = json.dumps(info, ensure_ascii=False)
        out.write(s + ', ')


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
@click.option('--dataset', '-f', required=True)
@click.option('--output', '-o', required=True)
def main(dataset, output):
    # os.makedirs(os.path.join(output, 'html'), exist_ok=True)
    # os.makedirs(os.path.join(output, 'info'), exist_ok=True)
    # os.makedirs(os.path.join(output, 'text'), exist_ok=True)

    json_path = os.path.join(output, 'all_info.json')

    i = 0
    for file in os.listdir(dataset):
        gc.collect()
        print(file)
        documents = process_file(os.path.join(dataset, file))
        f = open(json_path, 'w')
        for doc in tqdm(documents):
            if i % 1000 == 0:
                f.write(']')
                f.close()
                f = open(os.path.join(output, f'all_info{i // 1000}.json'), 'w')
                f.write('[')
            save_processed_document(doc, f)
            i += 1


if __name__ == '__main__':
    main()
