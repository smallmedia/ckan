import sqlalchemy

import ckan.plugins.toolkit as toolkit
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.lib.navl.dictization_functions import validate
from ckan.logic import NotAuthorized

from ckanext.infographic.logic.schema import (infographic_package_list_schema,
                                           package_infographic_list_schema)
from ckanext.infographic.model import InfographicPackageAssociation, InfographicAdmin

import logging
log = logging.getLogger(__name__)

_select = sqlalchemy.sql.select
_and_ = sqlalchemy.and_


@toolkit.side_effect_free
def infographic_show(context, data_dict):
    '''Return the pkg_dict for a infographic (package).

    :param id: the id or name of the infographic
    :type id: string
    '''

    toolkit.check_access('ckanext_infographic_show', context, data_dict)

    pkg_dict = toolkit.get_action('package_show')(context, data_dict)

    return pkg_dict


@toolkit.side_effect_free
def infographic_list(context, data_dict):
    '''Return a list of all infographics in the site.'''

    toolkit.check_access('ckanext_infographic_list', context, data_dict)

    model = context["model"]

    q = model.Session.query(model.Package) \
        .filter(model.Package.type == 'infographic') \
        .filter(model.Package.state == 'active')

    infographic_list = []
    for pkg in q.all():
        infographic_list.append(model_dictize.package_dictize(pkg, context))

    return infographic_list


@toolkit.side_effect_free
def infographic_package_list(context, data_dict):
    '''List packages associated with a infographic.

    :param infographic_id: id or name of the infographic
    :type infographic_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_infographic_package_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           infographic_package_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of package ids associated with infographic id
    pkg_id_list = InfographicPackageAssociation.get_package_ids_for_infographic(
        validated_data_dict['infographic_id'])

    pkg_list = []
    if pkg_id_list:
        # for each package id, get the package dict and append to list if
        # active
        id_list = []
        for pkg_id in pkg_id_list:
            id_list.append(pkg_id[0])
        q = ' OR '.join(['id:{0}'.format(x) for x in id_list])
        _pkg_list = toolkit.get_action('package_search')(
            context,
            {'q': q, 'rows': 100})
        pkg_list = _pkg_list['results']
    return pkg_list


@toolkit.side_effect_free
def package_infographic_list(context, data_dict):
    '''List infographics associated with a package.

    :param package_id: id or name of the package
    :type package_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_package_infographic_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           package_infographic_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of infographic ids associated with the package id
    infographic_id_list = InfographicPackageAssociation.get_infographic_ids_for_package(
        validated_data_dict['package_id'])
    infographic_list = []

    q = ''
    fq = ''
    if infographic_id_list:
        id_list = []
        for infographic_id in infographic_id_list:
            id_list.append(infographic_id[0])
        fq = 'dataset_type:infographic'
        q = ' OR '.join(['id:{0}'.format(x) for x in id_list])
        _infographic_list = toolkit.get_action('package_search')(
            context,
            {'q': q, 'fq': fq, 'rows': 100})
        infographic_list = _infographic_list['results']

    return infographic_list


@toolkit.side_effect_free
def infographic_admin_list(context, data_dict):
    '''
    Return a list of dicts containing the id and name of all active infographic
    admin users.

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_infographic_admin_list', context, data_dict)

    model = context["model"]

    user_ids = InfographicAdmin.get_infographic_admin_ids()

    if user_ids:
        q = model.Session.query(model.User) \
            .filter(model.User.state == 'active') \
            .filter(model.User.id.in_(user_ids))

        infographic_admin_list = []
        for user in q.all():
            infographic_admin_list.append({'name': user.name, 'id': user.id})
        return infographic_admin_list

    return []
