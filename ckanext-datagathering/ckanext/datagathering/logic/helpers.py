import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Datagathering search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.datagathering.controller:DatagatheringController',
        action='search')


def get_datagathering_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of datagatherings.
    '''

    stats = {}
    stats['datagathering_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '+dataset_type:datagathering'})['count']

    return stats


def get_wysiwyg_editor():
    return tk.config.get('ckanext.datagathering.editor', '')
