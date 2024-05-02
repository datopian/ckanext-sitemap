[![Tests](https://github.com//ckanext-sitemap/workflows/Tests/badge.svg?branch=main)](https://github.com//ckanext-sitemap/actions)

# ckanext-sitemap
A CKAN extension that generates a sitemap XML file is designed to create a structured map of a CKAN instance's datasets and resources, making it easier for search engines to discover and index the available data. !

## Installation

**TODO:** Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-sitemap:

1. Activate your CKAN virtual environment, for example:

     . /usr/lib/ckan/default/bin/activate

2. Clone the source and install it on the virtualenv

    git clone https://github.com//ckanext-sitemap.git
    cd ckanext-sitemap
    pip install -e .
    pip install -r requirements.txt

3. Add `sitemap` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

     sudo service apache2 reload

## Configuration

You can configure this extension in the `production.ini` file of your CKAN instance. Ensure to set these environment variables according to your requirements for sitemap generation and management.

Environment Variable | Default Value | Description
-------------------- | ------------- | -----------
`ckanext.sitemap.directory` | [`./ckanext/sitemap/public`](./ckanext/sitemap/public/) | The directory path for storing generated sitemaps.
`ckanext.sitemap.max_items` | `5000` | Maximum number of items per sitemap file. If the total count of resources exceeds this limit, the sitemap is split into multiple files.
`ckanext.sitemap.ttl` | `8 * 3600` (8 hours) | Time-To-Live (TTL) for sitemaps. Sitemaps older than this value (in seconds) are regenerated when a user visits a sitemap route.
`ckanext.sitemap.include_resources` | `True` | Determines whether package resources (distributions) should be included in the sitemaps. Set to `True` to include resources, and `False` to exclude them.
`ckanext.sitemap.include_language_alternatives` | `True` | Determines whether package resources (distributions) should be included in the sitemaps. Set to `True` to include resources, and `False` to exclude them.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
