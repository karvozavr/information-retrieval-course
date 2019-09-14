#!/usr/bin/env python3

import base64
import json
from urllib.parse import urlparse

import click
import networkx as nx
import tqdm


def nodes_ranked(g):
    rank = list(nx.pagerank(g, 0.9).items())
    rank.sort(key=lambda x: x[1], reverse=True)
    return list(map(lambda x: x[0], rank))


def build_graph(file):
    g = nx.DiGraph()

    load_graph(g, file)

    print('Ready')

    nodes = nodes_ranked(g)

    print('Ranked')

    top100 = g.subgraph(nodes[:100])
    top500 = g.subgraph(nodes[:500])
    top1000 = g.subgraph(nodes[:1000])

    print(len(top100.edges))

    nx.write_gml(top100, 'top100.gml')
    nx.write_gml(top500, 'top500.gml')
    nx.write_gml(top1000, 'top1000.gml')
    nx.write_gml(g, 'graph.gml')


def load_graph(g, file):
    with open(file) as f:
        docs = json.load(f)
        for doc in tqdm.tqdm(docs):
            url = base64.b64decode(doc['url']).decode('cp1251')
            refs = doc['references']
            for ref in refs:
                if ref.startswith('http://'):
                    try:
                        g.add_edge(f'{urlparse(url).netloc}', f'{urlparse(ref).netloc}')
                    except ValueError as e:
                        pass


@click.command()
@click.option('--file', '-f', required=True)
def main(file):
    build_graph(file)


if __name__ == '__main__':
    main()
