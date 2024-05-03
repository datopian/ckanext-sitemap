# -*- coding: utf-8 -*-

import click
import ckanext.sitemap.sitemap as sm

def get_commands():
    return [ckanext_sitemap]


@click.group()
def ckanext_sitemap():
    """ckanext-sitemap

    Usage:

      ckanext-sitemap generate
        - (Re)generate sitemap.
    """


@ckanext_sitemap.command()
def generate():
    """
    Command to generate sitemap.
    """
    try:
        click.echo('Starting sitemap generation..')
        sm.generate_sitemap()
        click.echo('Finished sitemap generation.')

    except Exception as e:
        # Handle exceptions that may occur during cleanup
        click.echo(f'Error during sitemap generation: {str(e)}', err=True)
