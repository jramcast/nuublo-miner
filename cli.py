#!/usr/bin/env python3

import click
import urllib.request as ur
from api import image
from api.miner import select_most_frequent, select_most_frequent_coocurrences, select_most_frequent_word_coocurrences

@click.group()
def cli():
    pass

@cli.command()
@click.argument('number', default=10)
@click.argument('include', default='terms')
def frequent(number, include):
    """Searches the most frequent words"""
    click.echo(select_most_frequent(number, include))

@cli.command()
@click.argument('number', default=10)
@click.argument('include', default='terms')
def coocurrences(number, include):
    """Gets the terms with more coocurrences"""
    click.echo(select_most_frequent_coocurrences(number, include))

@cli.command()
@click.argument('term')
@click.argument('number', default=10)
@click.argument('include', default='terms')
def word(term, number, include):
    """Gets the terms with more coocurrences with the given term"""
    click.echo(select_most_frequent_word_coocurrences(term, number, include))

@cli.command()
@click.argument('url')
def irecognition(url):
    """Tensorflow image recognition"""
    testfile = ur.URLopener()
    testfile.retrieve(url, "image.jpg")
    print('Image downloaded')
    image.run('image.jpg')

if __name__ == '__main__':
    cli()