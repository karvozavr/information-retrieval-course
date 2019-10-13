#!/usr/bin/env python3

import click


def process_files(file1, file2):
	with open(file1) as f1, open(file2) as f2:
		lines1 = f1.readlines()
		lines2 = f2.readlines()

		for line1, line2 in zip(lines1, lines2):
			l1 = line1.split(' ')
			l2 = line2.split(' ')
			l1[0] = l2[2]
			print(' '.join(l1), end='')


@click.command()
@click.argument('file1', nargs=1)
@click.argument('file2', nargs=1)
def main(file1, file2):
	process_files(file1, file2)


if __name__ == '__main__':
	main()
