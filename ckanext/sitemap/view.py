import logging
from datetime import datetime, timezone
import os

from flask import Blueprint, make_response
from ckan.model import Session, Package

import ckan.plugins.toolkit as tk
from lxml import etree

sitemap = Blueprint("sitemap", __name__)

# cache = Cache(current_app, config={'CACHE_TYPE': 'simple'})

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"

XHTML_NS = "http://www.w3.org/1999/xhtml"

log = logging.getLogger(__file__)

defualt_locals = tk.config.get("ckan.locale_default", "en")

if isinstance(defualt_locals, str):
    defualt_locals = [defualt_locals]


def _create_language_alternatives(link, url):
    """
    Create links (elements) for every language in locales_offered in .ini file
    :param link: string containing the link, eg. /dataset/xyz
    :param url: root node
    """
    for lang in defualt_locals:
        attrib = {
            "rel": "alternate",
            "hreflang": lang,
            "href": tk.config.get("ckan.site_url") + "/" + lang + link,
        }
        etree.SubElement(url, "{http://www.w3.org/1999/xhtml}link", attrib)


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
        pkgs = (
            Session.query(Package)
            .filter(Package.type == "dataset")
            .filter(Package.private != True)
            .filter(Package.state == "active")
            .all()
        )

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
            _create_language_alternatives(_url, url)

        for pkg in pkgs:
            url = etree.SubElement(root, "url")
            loc = etree.SubElement(url, "loc")
            pkg_url = tk.url_for(controller="dataset", action="read", id=pkg.name)
            loc.text = tk.config.get("ckan.site_url") + pkg_url
            lastmod = etree.SubElement(url, "lastmod")
            lastmod.text = pkg.metadata_modified.strftime("%Y-%m-%d")
            _create_language_alternatives(pkg_url, url)
            for res in pkg.resources:
                url = etree.SubElement(root, "url")
                loc = etree.SubElement(url, "loc")
                loc.text = tk.config.get("ckan.site_url") + tk.url_for(
                    controller="dataset_resource",
                    action="read",
                    id=pkg.name,
                    package_type=tk.h.default_package_type(),
                    resource_id=res.id,
                )
                lastmod = etree.SubElement(url, "lastmod")
                _create_language_alternatives(
                    tk.url_for(
                        controller="dataset_resource",
                        action="read",
                        id=pkg.name,
                        package_type=tk.h.default_package_type(),
                        resource_id=res.id,
                    ),
                    url,
                )
                lastmod.text = res.created.strftime("%Y-%m-%d")

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
