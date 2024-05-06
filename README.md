[![Tests](https://github.com//ckanext-sitemap/workflows/Tests/badge.svg?branch=main)](https://github.com//ckanext-sitemap/actions)

# ckanext-sitemap

A CKAN extension that generates a sitemap XML file is designed to create a structured map of a CKAN instance's datasets and resources, making it easier for search engines to discover and index the available data.

## Table of Contents

- [Getting Started](#getting-started)
- [Contributing](#contributing)
- [Versioning](#versioning)
- [License](#license)

## Getting Started

### Installation

To install ckanext-sitemap:

1. Activate your CKAN virtual environment, for example:

    ```bash
    . /usr/lib/ckan/default/bin/activate
    ```

2. Clone the source and install it in the virtual environment

    ```bash
    git clone https://github.com//ckanext-sitemap.git
    cd ckanext-sitemap
    pip install -e .
    pip install -r requirements.txt
    ```

3. Add `sitemap` to the `ckan.plugins` setting in your CKAN
   config file (by default the config file is located at
   `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu:

    ```bash
    sudo service apache2 reload
    ```

### Configuration

You can configure this extension in the `ckan.ini` file of your CKAN instance. Ensure to set these environment variables according to your requirements for sitemap generation and management.

Environment Variable | Default Value | Description
-------------------- | ------------- | -----------
`ckanext.sitemap.directory` | [`./ckanext/sitemap/public`](./ckanext/sitemap/public/) | The directory path for storing generated sitemaps.
`ckanext.sitemap.max_items` | `5000` | Maximum number of items per sitemap file. If the total count of resources exceeds this limit, the sitemap is split into multiple files.
`ckanext.sitemap.autorenew` | `True` | If this option is enabled, the sitemaps will be automatically renewed whenever a user requests a sitemap and the existing sitemap is older than the Time-To-Live (TTL) value specified. Set this to False if you prefer a cron job to handle sitemap generation.
`ckanext.sitemap.ttl` | `8 * 3600` (8 hours) | Time-To-Live (TTL) for sitemaps. Sitemaps older than this value (in seconds) are regenerated when a user visits a sitemap route.
`ckanext.sitemap.resources` | `True` | Determines whether package resources (distributions) should be included in the sitemaps.
`ckanext.sitemap.language_alternatives` | `True` | Determines whether language alternatives should be included in the sitemaps.
`ckanext.sitemap.custom_uris` | `Undefined` | A list of additional sitemap URIs separated by whitespace or newlines. These URIs will be included in the sitemap generation process alongside the default CKAN URIs.

### Using Cron for Regular Sitemap Generation

Using cron to generate sitemaps regularly can be advantageous, especially if the sitemap generation process is time-consuming.

Ensure that the sitemap generation occurs within the time frame specified by `ckanext.sitemap.ttl`, or alternatively, set `ckanext.sitemap.autorenew` to `False` to prevent accidental triggering of sitemap generation by users.

**Example Cron Job:**

To schedule the command to run at 2 AM, 10 AM, and 6 PM:

```bash
0 2,10,18 * * * /usr/lib/ckan/default/bin/ckan -c /etc/ckan/default/production.ini ckanext-sitemap generate > /dev/null 2>&1
```

## Available Commands

- `generate`

    This command triggers the generation of the sitemap.

    Usage:

    ```bash
    ckanext-sitemap generate
    ```

## Contributing

To contribute to this documentation, create a branch or fork this repository, make
your changes and create a merge request.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see
the tags on this repository.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
