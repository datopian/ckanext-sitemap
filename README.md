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

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
