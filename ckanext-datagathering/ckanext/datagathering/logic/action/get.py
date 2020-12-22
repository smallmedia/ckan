import sqlalchemy

import ckan.plugins.toolkit as toolkit
import ckan.lib.dictization.model_dictize as model_dictize
from ckan.lib.navl.dictization_functions import validate
from ckan.logic import NotAuthorized

from ckanext.datagathering.logic.schema import (datagathering_package_list_schema,
                                           package_datagathering_list_schema)
from ckanext.datagathering.model import DatagatheringPackageAssociation, DatagatheringAdmin

import logging
log = logging.getLogger(__name__)

_select = sqlalchemy.sql.select
_and_ = sqlalchemy.and_


@toolkit.side_effect_free
def datagathering_show(context, data_dict):
    '''Return the pkg_dict for a datagathering (package).

    :param id: the id or name of the datagathering
    :type id: string
    '''

    toolkit.check_access('ckanext_datagathering_show', context, data_dict)

    pkg_dict = toolkit.get_action('package_show')(context, data_dict)

    return pkg_dict


@toolkit.side_effect_free
def datagathering_list(context, data_dict):
    '''Return a list of all datagatherings in the site.'''

    toolkit.check_access('ckanext_datagathering_list', context, data_dict)

    model = context["model"]

    q = model.Session.query(model.Package) \
        .filter(model.Package.type == 'datagathering') \
        .filter(model.Package.state == 'active')

    datagathering_list = []
    for pkg in q.all():
        datagathering_list.append(model_dictize.package_dictize(pkg, context))

    return datagathering_list


@toolkit.side_effect_free
def datagathering_package_list(context, data_dict):
    '''List packages associated with a datagathering.

    :param datagathering_id: id or name of the datagathering
    :type datagathering_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_datagathering_package_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           datagathering_package_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of package ids associated with datagathering id
    pkg_id_list = DatagatheringPackageAssociation.get_package_ids_for_datagathering(
        validated_data_dict['datagathering_id'])

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
def package_datagathering_list(context, data_dict):
    '''List datagatherings associated with a package.

    :param package_id: id or name of the package
    :type package_id: string

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_package_datagathering_list', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           package_datagathering_list_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    # get a list of datagathering ids associated with the package id
    datagathering_id_list = DatagatheringPackageAssociation.get_datagathering_ids_for_package(
        validated_data_dict['package_id'])
    datagathering_list = []

    q = ''
    fq = ''
    if datagathering_id_list:
        id_list = []
        for datagathering_id in datagathering_id_list:
            id_list.append(datagathering_id[0])
        fq = 'dataset_type:datagathering'
        q = ' OR '.join(['id:{0}'.format(x) for x in id_list])
        _datagathering_list = toolkit.get_action('package_search')(
            context,
            {'q': q, 'fq': fq, 'rows': 100})
        datagathering_list = _datagathering_list['results']

    return datagathering_list


@toolkit.side_effect_free
def datagathering_admin_list(context, data_dict):
    '''
    Return a list of dicts containing the id and name of all active datagathering
    admin users.

    :rtype: list of dictionaries
    '''

    toolkit.check_access('ckanext_datagathering_admin_list', context, data_dict)

    model = context["model"]

    user_ids = DatagatheringAdmin.get_datagathering_admin_ids()

    if user_ids:
        q = model.Session.query(model.User) \
            .filter(model.User.state == 'active') \
            .filter(model.User.id.in_(user_ids))

        datagathering_admin_list = []
        for user in q.all():
            datagathering_admin_list.append({'name': user.name, 'id': user.id})
        return datagathering_admin_list

    return []
