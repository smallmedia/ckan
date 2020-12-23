import os
import sys
import logging

import ckan.plugins as plugins
import ckan.lib.plugins as lib_plugins
import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk
from ckan.common import OrderedDict
from ckan import model as ckan_model

from routes.mapper import SubMapper

import ckanext.datagathering.logic.auth
import ckanext.datagathering.logic.action.create
import ckanext.datagathering.logic.action.delete
import ckanext.datagathering.logic.action.update
import ckanext.datagathering.logic.action.get
import ckanext.datagathering.logic.schema as datagathering_schema
import ckanext.datagathering.logic.helpers as datagathering_helpers
from ckanext.datagathering.model import setup as model_setup

c = tk.c
_ = tk._

log = logging.getLogger(__name__)

DATASET_TYPE_NAME = 'datagathering'


class DatagatheringPlugin(plugins.SingletonPlugin, lib_plugins.DefaultDatasetForm):
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IFacets, inherit=True)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # ITranslation only available in 2.5+
    try:
        plugins.implements(plugins.ITranslation)
    except AttributeError:
        pass

    # IConfigurer

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')
        tk.add_public_directory(config, 'public')
        tk.add_resource('fanstatic', 'datagathering')
        if tk.check_ckan_version(min_version='2.4'):
            tk.add_ckan_admin_tab(config, 'ckanext_datagathering_admins',
                                  'Datagathering Config')

    # IConfigurable

    def configure(self, config):
        model_setup()

    # IDatasetForm

    def package_types(self):
        return [DATASET_TYPE_NAME]

    def is_fallback(self):
        return False

    def search_template(self):
        return 'datagathering/search.html'

    def new_template(self):
        return 'datagathering/new.html'

    def read_template(self):
        return 'datagathering/read.html'

    def edit_template(self):
        return 'datagathering/edit.html'

    def package_form(self):
        return 'datagathering/new_package_form.html'

    def create_package_schema(self):
        return datagathering_schema.datagathering_create_schema()

    def update_package_schema(self):
        return datagathering_schema.datagathering_update_schema()

    def show_package_schema(self):
        return datagathering_schema.datagathering_show_schema()

    # ITemplateHelpers

    def get_helpers(self):
        return {
            'facet_remove_field': datagathering_helpers.facet_remove_field,
            'get_datagathering_statistics': datagathering_helpers.get_datagathering_statistics,
            'get_wysiwyg_editor': datagathering_helpers.get_wysiwyg_editor,
        }

    # IFacets

    def dataset_facets(self, facets_dict, package_type):
        '''Only show tags for Datagathering search list.'''
        if package_type != DATASET_TYPE_NAME:
            return facets_dict
        return OrderedDict({'tags': _('Tags')})

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'ckanext_datagathering_create': ckanext.datagathering.logic.auth.create,
            'ckanext_datagathering_update': ckanext.datagathering.logic.auth.update,
            'ckanext_datagathering_delete': ckanext.datagathering.logic.auth.delete,
            'ckanext_datagathering_show': ckanext.datagathering.logic.auth.show,
            'ckanext_datagathering_list': ckanext.datagathering.logic.auth.list,
            'ckanext_datagathering_package_association_create':
                ckanext.datagathering.logic.auth.package_association_create,
            'ckanext_datagathering_package_association_delete':
                ckanext.datagathering.logic.auth.package_association_delete,
            'ckanext_datagathering_package_list':
                ckanext.datagathering.logic.auth.datagathering_package_list,
            'ckanext_package_datagathering_list':
                ckanext.datagathering.logic.auth.package_datagathering_list,
            'ckanext_datagathering_admin_add':
                ckanext.datagathering.logic.auth.add_datagathering_admin,
            'ckanext_datagathering_admin_remove':
                ckanext.datagathering.logic.auth.remove_datagathering_admin,
            'ckanext_datagathering_admin_list':
                ckanext.datagathering.logic.auth.datagathering_admin_list,
            'ckanext_datagathering_upload':
                ckanext.datagathering.logic.auth.datagathering_upload
        }

    # IRoutes

    def before_map(self, map):
        # These named routes are used for custom dataset forms which will use
        # the names below based on the dataset.type ('dataset' is the default
        # type)
        with SubMapper(map, controller='ckanext.datagathering.controller:DatagatheringController') as m:
            m.connect('ckanext_datagathering_index', '/datagathering', action='search',
                      highlight_actions='index search')
            m.connect('ckanext_datagathering_new', '/datagathering/new', action='new')
            m.connect('ckanext_datagathering_delete', '/datagathering/delete/{id}',
                      action='delete')
            m.connect('ckanext_datagathering_read', '/datagathering/{id}', action='read',
                      ckan_icon='picture')
            m.connect('ckanext_datagathering_edit', '/datagathering/edit/{id}',
                      action='edit', ckan_icon='edit')
            m.connect('ckanext_datagathering_manage_datasets',
                      '/datagathering/manage_datasets/{id}',
                      action="manage_datasets", ckan_icon="sitemap")
            m.connect('dataset_datagathering_list', '/dataset/datagatherings/{id}',
                      action='dataset_datagathering_list', ckan_icon='picture')
            m.connect('ckanext_datagathering_admins', '/ckan-admin/datagathering_admins',
                      action='manage_datagathering_admins', ckan_icon='picture'),
            m.connect('ckanext_datagathering_admin_remove',
                      '/ckan-admin/datagathering_admin_remove',
                      action='remove_datagathering_admin'),
            m.connect('datagathering_upload', '/datagathering_upload',
                    action='datagathering_upload')
        map.redirect('/datagatherings', '/datagathering')
        map.redirect('/datagatherings/{url:.*}', '/datagathering/{url}')
        return map

    # IActions

    def get_actions(self):
        action_functions = {
            'ckanext_datagathering_create':
                ckanext.datagathering.logic.action.create.datagathering_create,
            'ckanext_datagathering_update':
                ckanext.datagathering.logic.action.update.datagathering_update,
            'ckanext_datagathering_delete':
                ckanext.datagathering.logic.action.delete.datagathering_delete,
            'ckanext_datagathering_show':
                ckanext.datagathering.logic.action.get.datagathering_show,
            'ckanext_datagathering_list':
                ckanext.datagathering.logic.action.get.datagathering_list,
            'ckanext_datagathering_package_association_create':
                ckanext.datagathering.logic.action.create.datagathering_package_association_create,
            'ckanext_datagathering_package_association_delete':
                ckanext.datagathering.logic.action.delete.datagathering_package_association_delete,
            'ckanext_datagathering_package_list':
                ckanext.datagathering.logic.action.get.datagathering_package_list,
            'ckanext_package_datagathering_list':
                ckanext.datagathering.logic.action.get.package_datagathering_list,
            'ckanext_datagathering_admin_add':
                ckanext.datagathering.logic.action.create.datagathering_admin_add,
            'ckanext_datagathering_admin_remove':
                ckanext.datagathering.logic.action.delete.datagathering_admin_remove,
            'ckanext_datagathering_admin_list':
                ckanext.datagathering.logic.action.get.datagathering_admin_list,
            'ckanext_datagathering_upload':
                ckanext.datagathering.logic.action.create.datagathering_upload,
        }
        return action_functions

    # IPackageController

    def _add_to_pkg_dict(self, context, pkg_dict):
        '''
        Add key/values to pkg_dict and return it.
        '''

        if pkg_dict['type'] != 'datagathering':
            return pkg_dict

        # Add a display url for the Datagathering image to the pkg dict so template
        # has access to it.
        image_url = pkg_dict.get('image_url')
        pkg_dict[u'image_display_url'] = image_url
        if image_url and not image_url.startswith('http'):
            pkg_dict[u'image_url'] = image_url
            pkg_dict[u'image_display_url'] = \
                h.url_for_static('uploads/{0}/{1}'
                                 .format(DATASET_TYPE_NAME,
                                         pkg_dict.get('image_url')),
                                 qualified=True)

        # Add dataset count
        pkg_dict[u'num_datasets'] = len(
            tk.get_action('ckanext_datagathering_package_list')(
                context, {'datagathering_id': pkg_dict['id']}))

        # Rendered notes
        if datagathering_helpers.get_wysiwyg_editor() == 'ckeditor':
            pkg_dict[u'datagathering_notes_formatted'] = pkg_dict['notes']
        else:
            pkg_dict[u'datagathering_notes_formatted'] = \
                h.render_markdown(pkg_dict['notes'])

        return pkg_dict

    def after_show(self, context, pkg_dict):
        '''
        Modify package_show pkg_dict.
        '''
        pkg_dict = self._add_to_pkg_dict(context, pkg_dict)

    def before_view(self, pkg_dict):
        '''
        Modify pkg_dict that is sent to templates.
        '''

        context = {'model': ckan_model, 'session': ckan_model.Session,
                   'user': c.user or c.author}

        return self._add_to_pkg_dict(context, pkg_dict)

    def before_search(self, search_params):
        '''
        Unless the query is already being filtered by this dataset_type
        (either positively, or negatively), exclude datasets of type
        `datagathering`.
        '''
        fq = search_params.get('fq', '')
        filter = 'dataset_type:{0}'.format(DATASET_TYPE_NAME)
        if filter not in fq:
            search_params.update({'fq': fq + " -" + filter})
        else:
            lanfilter = 'lang:{0}'.format(h.lang())
            if lanfilter not in fq:
                search_params.update({'fq': fq + " +" + lanfilter})
        if not search_params.get('sort'):
            search_params['sort'] = 'metadata_modified desc'
        return search_params

    # ITranslation

    # The following methods copied from ckan.lib.plugins.DefaultTranslation so
    # we don't have to mix it into the class. This means we can use Datagathering
    # even if ITranslation isn't available (less than 2.5).

    def i18n_directory(self):
        '''Change the directory of the *.mo translation files

        The default implementation assumes the plugin is
        ckanext/myplugin/plugin.py and the translations are stored in
        i18n/
        '''
        # assume plugin is called ckanext.<myplugin>.<...>.PluginClass
        extension_module_name = '.'.join(self.__module__.split('.')[0:2])
        module = sys.modules[extension_module_name]
        return os.path.join(os.path.dirname(module.__file__), 'i18n')

    def i18n_locales(self):
        '''Change the list of locales that this plugin handles

        By default the will assume any directory in subdirectory in the
        directory defined by self.directory() is a locale handled by this
        plugin
        '''
        directory = self.i18n_directory()
        return [d for
                d in os.listdir(directory)
                if os.path.isdir(os.path.join(directory, d))]

    def i18n_domain(self):
        '''Change the gettext domain handled by this plugin

        This implementation assumes the gettext domain is
        ckanext-{extension name}, hence your pot, po and mo files should be
        named ckanext-{extension name}.mo'''
        return 'ckanext-{name}'.format(name=self.name)
