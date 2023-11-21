import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.sitemap.view as view


class SitemapPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)

    # IBlueprint
    def get_blueprint(self):
        return view.get_blueprints()
        

    
