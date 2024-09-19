import logging
import os

from flask import Blueprint, make_response

import ckan.plugins.toolkit as tk
import ckanext.sitemap.sitemap as sm

sitemap = Blueprint("sitemap", __name__)

SITEMAP_DIR = tk.config.get('ckanext.sitemap.directory', os.path.join(
    os.path.dirname(__file__), 'public'))
SITEMAP_AUTORENEW = tk.asbool(tk.config.get(
    'ckanext.sitemap.autorenew', True))

log = logging.getLogger(__name__)


def view(index=None):
    try:
        return sm.generate_sitemap_response(index)

    except Exception as e:
        log.exception(
            "Error occurred during sitemap response generation: %s", e)
        return make_response("Internal Server Error", 500)


def redirect_to_sitemap_index():
    return tk.redirect_to("/sitemap_index.xml")


# Don't add url rules if autorenew is set to false and sitemaps stored in public dir
if SITEMAP_AUTORENEW or SITEMAP_DIR != os.path.join(os.path.dirname(__file__), 'public'):
    sitemap.add_url_rule("/sitemap_index.xml",
                         view_func=view, methods=["GET"])
    sitemap.add_url_rule("/sitemap-<int:index>.xml",
                         view_func=view, methods=["GET"])

sitemap.add_url_rule("/sitemap.xml",
                     view_func=redirect_to_sitemap_index, methods=["GET"])


def get_blueprints():
    return [sitemap]
