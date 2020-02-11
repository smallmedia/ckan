import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation

from ckanext.mailchimp.logic.action.create import mailchimp_user_create
from ckanext.mailchimp.logic.action.update import mailchimp_user_update


class MailchimpPlugin(plugins.SingletonPlugin,  DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'mailchimp')

    # IActions
    def get_actions(self):
        return {
            'user_create': mailchimp_user_create,
            'user_update': mailchimp_user_update
        }

    # IRoutes

    def before_map(self, m):
        m.connect('/newsletter/subscribe',
                     controller='ckanext.mailchimp.controller:NewsletterController',
                     action='subscribe')
        return m
