import logging
from datetime import datetime, timezone
import os

from flask import Blueprint, make_response
import ckan.model as model
from ckan.common import c

import ckan.plugins.toolkit as tk
from lxml import etree

sitemap = Blueprint("sitemap", __name__)

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

XHTML_NS = "http://www.w3.org/1999/xhtml"

log = logging.getLogger(__file__)


def sitemap_controller():
    root = etree.Element("urlset", nsmap={None: SITEMAP_NS, "xhtml": XHTML_NS})

    current_dir = os.path.dirname(__file__)
    format_string = "%Y-%m-%dT%H:%M:%S.%f%z"

    def _generate_filename():
        return "sitemap-" + datetime.now(tz=timezone.utc).isoformat() + ".xml"

    def _remove_file(file):
        log.info("Removing sitemap.xml file: %s", file)
        os.remove(os.path.join(current_dir, file))

    def _create_file(filename, root):
        log.info("Creating new sitemap.xml file: %s", filename)
        
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        data_dict = {
            'q': '*:*',
            'start': 0,
            'rows': 500  # Adjust as needed
        }

        # Use the package_search action to query datasets
        search_action = tk.get_action('package_search')
        search_results = search_action(context, data_dict)
        datasets = search_results['results']

        all_ckan_urls = [
            tk.url_for(controller="home", action="index", _external=True),
            tk.url_for(controller="dataset", action="search", _external=True),
            tk.url_for(controller="organization", action="index", _external=True),
            tk.url_for(controller="group", action="index", _external=True),
        ]

        for _url in all_ckan_urls:
            url = etree.SubElement(root, "url")
            loc = etree.SubElement(url, "loc")
            loc.text = _url

        for pkg in datasets:
            url = etree.SubElement(root, "url")
            loc = etree.SubElement(url, "loc")
            pkg_url = tk.url_for(controller="dataset", action="read", id=pkg["name"])
            loc.text = tk.config.get("ckan.site_url") + pkg_url
            lastmod = etree.SubElement(url, "lastmod")
            metadata_modifiedDate = datetime.strptime(pkg["metadata_modified"], "%Y-%m-%dT%H:%M:%S.%f")
            lastmod.text = metadata_modifiedDate.strftime("%Y-%m-%d")
            resources = list(pkg["resources"])

            for res in resources:
                url = etree.SubElement(root, "url")
                loc = etree.SubElement(url, "loc")
                loc.text = tk.config.get("ckan.site_url") + tk.url_for(
                    controller="dataset_resource",
                    action="read",
                    id=pkg["name"],
                    package_type=tk.h.default_package_type(),
                    resource_id=res["id"],
                )
                lastmod = etree.SubElement(url, "lastmod")
                lastmod.text = datetime.strptime(res["created"], "%Y-%m-%dT%H:%M:%S.%f")

        with open(os.path.join(current_dir, filename), "wb") as f:
            f.write(etree.tostring(root, pretty_print=True))

    def create_response(file):
        with open(os.path.join(current_dir, file), "rb") as f:
            response = make_response(f.read(), 200)
            response.headers["Content-Type"] = "application/xml"
            return response

    sitemap_file = [
        file for file in os.listdir(current_dir) if file.startswith("sitemap-")
    ]

    if not sitemap_file:
        _create_file(_generate_filename(), root)
    else:
        file_date = sitemap_file[0].replace("sitemap-", "").replace(".xml", "")
        now = datetime.now(timezone.utc)
        file_date = datetime.strptime(file_date, format_string).astimezone(timezone.utc)
        time_difference = now - file_date

        if time_difference.total_seconds() > 8 * 3600:
            _remove_file(sitemap_file[0])
            _create_file(_generate_filename(), root)
        else:
            response = create_response(sitemap_file[0])
            return response

    response = make_response(etree.tostring(root, pretty_print=True), 200)
    return response


sitemap.add_url_rule("/sitemap.xml", view_func=sitemap_controller, methods=["GET"])

def get_blueprints():
    return [sitemap]
