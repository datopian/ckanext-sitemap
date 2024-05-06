import logging
from datetime import datetime, timedelta
from typing import Set
import os

from flask import make_response
from ckan.model import Session, Package

import ckan.plugins.toolkit as tk
from lxml import etree

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NS = "http://www.w3.org/1999/xhtml"

SITEMAP_DIR = tk.config.get('ckanext.sitemap.directory', os.path.join(
    os.path.dirname(__file__), 'public'))
SITEMAP_AUTORENEW = tk.asbool(tk.config.get(
    'ckanext.sitemap.autorenew', True))
SITEMAP_TTL = int(tk.config.get('ckanext.sitemap.ttl', 8*3600))
MAX_ITEMS = tk.config.get('ckanext.sitemap.max_items', 5000)
INC_RESOURCES = tk.asbool(tk.config.get(
    'ckanext.sitemap.resources', True))
INC_LANG_ALTS = tk.asbool(tk.config.get(
    'ckanext.sitemap.language_alternatives', True))

log = logging.getLogger(__name__)


def _get_locales_from_config() -> Set:
    locales_offered = tk.config.get('ckan.locales_offered')
    filtered_out = tk.config.get('ckan.locales_filtered_out')
    locale_default = [tk.config.get('ckan.locale_default', 'en')]

    all_locales = set(locales_offered)
    all_locales -= (set(filtered_out) | set(locale_default))
    return all_locales


def _create_language_alternatives(link, url):
    for lang in _get_locales_from_config():
        attrib = {
            "rel": "alternate",
            "hreflang": lang,
            "href": tk.config.get("ckan.site_url") + "/" + lang + link,
        }
        etree.SubElement(url, "{http://www.w3.org/1999/xhtml}link", attrib)


def _generate_filename(index):
    return f"sitemap-{index}.xml"


def _generate_index_filename():
    return "sitemap_index.xml"


def _remove_file(file):
    log.info("Removing sitemap file: %s", file)
    os.remove(os.path.join(SITEMAP_DIR, file))


def _generate_sitemap_files(pkgs):
    sitemap_item_count = 0
    sitemap_index = 0
    file_root = None

    ckan_uris = [
        tk.url_for(controller="home", action="index", _external=True),
        tk.url_for(controller="dataset", action="search", _external=True),
        tk.url_for(controller="organization", action="index", _external=True),
        tk.url_for(controller="group", action="index", _external=True),
    ]

    # Get the hardcoded URIs from the CKAN configuration (if present)
    additional_uris = tk.config.get('ckanext.sitemap.additional_uris', '').split()

    # Merge CKAN URIs and hardcoded URIs from ckan config
    all_uris = ckan_uris + additional_uris

    for uri in all_uris:
        if sitemap_item_count % MAX_ITEMS == 0:
            if file_root is not None:
                with open(os.path.join(SITEMAP_DIR, _generate_filename(sitemap_index)), "wb") as f:
                    f.write(etree.tostring(
                        file_root, pretty_print=True))
                sitemap_index += 1
                file_root = None  # Reset file_root after writing
                sitemap_item_count = 0  # Reset sitemap_item_count

            file_root = etree.Element(
                "urlset", nsmap={None: SITEMAP_NS, "xhtml": XHTML_NS})

        url = etree.SubElement(file_root, "url")
        loc = etree.SubElement(url, "loc")
        loc.text = uri
        lastmod = etree.SubElement(url, "lastmod")
        lastmod.text = datetime.now().strftime("%Y-%m-%d")  # Set last modified date to current time (we don't know the real modified date)
        sitemap_item_count += 1

    for pkg in pkgs:
        if sitemap_item_count % MAX_ITEMS == 0:
            if file_root is not None:
                with open(os.path.join(SITEMAP_DIR, _generate_filename(sitemap_index)), "wb") as f:
                    f.write(etree.tostring(
                        file_root, pretty_print=True))
                sitemap_index += 1
                file_root = None  # Reset file_root after writing
                sitemap_item_count = 0  # Reset sitemap_item_count

            file_root = etree.Element(
                "urlset", nsmap={None: SITEMAP_NS, "xhtml": XHTML_NS})

        url = etree.SubElement(file_root, "url")
        loc = etree.SubElement(url, "loc")
        pkg_url = tk.url_for(controller="dataset",
                             action="read", id=pkg.name)
        loc.text = tk.config.get("ckan.site_url") + pkg_url
        lastmod = etree.SubElement(url, "lastmod")
        lastmod.text = pkg.metadata_modified.strftime("%Y-%m-%d")

        if INC_LANG_ALTS:
            _create_language_alternatives(pkg_url, url)

        sitemap_item_count += 1

        if INC_RESOURCES:
            for res in pkg.resources:
                if sitemap_item_count % MAX_ITEMS == 0:
                    if file_root is not None:
                        with open(os.path.join(SITEMAP_DIR, _generate_filename(sitemap_index)), "wb") as f:
                            f.write(etree.tostring(
                                file_root, pretty_print=True))
                        sitemap_index += 1
                        file_root = None  # Reset file_root after writing
                        sitemap_item_count = 0  # Reset sitemap_item_count

                    file_root = etree.Element(
                        "urlset", nsmap={None: SITEMAP_NS, "xhtml": XHTML_NS})

                url = etree.SubElement(file_root, "url")
                loc = etree.SubElement(url, "loc")
                loc.text = tk.config.get("ckan.site_url") + tk.url_for(
                    controller="dataset_resource",
                    action="read",
                    id=pkg.name,
                    package_type=tk.h.default_package_type(),
                    resource_id=res.id,
                )
                lastmod = etree.SubElement(url, "lastmod")

                if INC_LANG_ALTS:
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
                sitemap_item_count += 1

    # Write the last sitemap file
    if file_root is not None:
        with open(os.path.join(SITEMAP_DIR, _generate_filename(sitemap_index)), "wb") as f:
            f.write(etree.tostring(
                file_root, pretty_print=True))

    return sitemap_index + 1


def generate_sitemap():
    try:
        log.info("Generating sitemaps")
        pkgs = (
            Session.query(Package)
            .filter(Package.type == "dataset")
            .filter(Package.private != True)
            .filter(Package.state == "active")
            .all()
        )

        total_sitemaps = _generate_sitemap_files(pkgs)

        # Generate sitemap index
        index_root = etree.Element(
            "sitemapindex", nsmap={None: SITEMAP_NS})
        for i in range(total_sitemaps):  # Include all generated sitemaps
            index_url = etree.SubElement(index_root, "sitemap")
            loc = etree.SubElement(index_url, "loc")

            # Add the entry for the sitemap file
            sitemap_file_name = _generate_filename(i)
            sitemap_url = tk.config.get(
                "ckan.site_url") + "/" + sitemap_file_name

            loc.text = sitemap_url

        with open(os.path.join(SITEMAP_DIR, _generate_index_filename()), "wb") as f:
            f.write(etree.tostring(index_root, pretty_print=True))

    except Exception as e:
        log.exception("Error occurred during sitemap generation: %s", e)
        raise


def generate_sitemap_response(index=None):
    # Check modification time of sitemap index file
    index_file_path = os.path.join(
        SITEMAP_DIR, _generate_index_filename())
    if os.path.exists(index_file_path):
        index_mtime = os.path.getmtime(index_file_path)
        if datetime.fromtimestamp(index_mtime) < (datetime.now() - timedelta(seconds=SITEMAP_TTL)) and SITEMAP_AUTORENEW:
            # Regenerate sitemap index file if older than TTL
            log.info("Regenerating sitemap index file (older than TTL)")
            _remove_file(_generate_index_filename())
            generate_sitemap()
    else:
        # Generate sitemap index file if it doesn't exist
        log.info("Generating sitemap index file (not present)")
        generate_sitemap()

    if index is None:
        requested_file = _generate_index_filename()
        return create_response(requested_file)
    else:
        sitemap_files = [file for file in os.listdir(
            SITEMAP_DIR) if file.startswith("sitemap-")]

        if not sitemap_files:
            generate_sitemap()
            sitemap_files = [file for file in os.listdir(
                SITEMAP_DIR) if file.startswith("sitemap-")]

        requested_file = _generate_filename(index)
        if requested_file in sitemap_files:
            return create_response(requested_file)
        else:
            return make_response("Not Found", 404)


def create_response(file):
    with open(os.path.join(SITEMAP_DIR, file), "rb") as f:
        response = make_response(f.read(), 200)
        response.headers["Content-Type"] = "application/xml"
        return response
