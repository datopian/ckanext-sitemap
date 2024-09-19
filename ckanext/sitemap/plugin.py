import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.sitemap.view as view
from ckanext.sitemap import cli


class SitemapPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IClick)

    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "sitemap")

    # IBlueprint
    def get_blueprint(self):
        return view.get_blueprints()

    # IClick
    def get_commands(self):
        return cli.get_commands()
