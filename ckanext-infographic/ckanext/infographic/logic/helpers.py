import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Infographic search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.infographic.controller:InfographicController',
        action='search')


def get_infographic_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of infographics.
    '''

    stats = {}
    stats['infographic_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '+dataset_type:infographic'})['count']

    return stats


def get_wysiwyg_editor():
    return tk.config.get('ckanext.infographic.editor', '')
