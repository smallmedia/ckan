import logging

import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
import ckan.lib.navl.dictization_functions

from ckanext.datagathering.logic.schema import (
    datagathering_package_association_delete_schema,
    datagathering_admin_remove_schema)

from ckanext.datagathering.model import DatagatheringPackageAssociation, DatagatheringAdmin

validate = ckan.lib.navl.dictization_functions.validate

log = logging.getLogger(__name__)


def datagathering_delete(context, data_dict):
    '''Delete a datagathering. Datagathering delete cascades to
    DatagatheringPackageAssociation objects.

    :param id: the id or name of the datagathering to delete
    :type id: string
    '''

    model = context['model']
    id = toolkit.get_or_bust(data_dict, 'id')

    entity = model.Package.get(id)

    if entity is None:
        raise toolkit.ObjectNotFound

    toolkit.check_access('ckanext_datagathering_delete', context, data_dict)

    entity.purge()
    model.repo.commit()


def datagathering_package_association_delete(context, data_dict):
    '''Delete an association between a datagathering and a package.

    :param datagathering_id: id or name of the datagathering in the association
    :type datagathering_id: string

    :param package_id: id or name of the package in the association
    :type package_id: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_datagathering_package_association_delete',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, datagathering_package_association_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, datagathering_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'datagathering_id'])

    datagathering_package_association = DatagatheringPackageAssociation.get(
        package_id=package_id, datagathering_id=datagathering_id)

    if datagathering_package_association is None:
        raise toolkit.ObjectNotFound("DatagatheringPackageAssociation with package_id '{0}' and datagathering_id '{1}' doesn't exist.".format(package_id, datagathering_id))

    # delete the association
    datagathering_package_association.delete()
    model.repo.commit()


def datagathering_admin_remove(context, data_dict):
    '''Remove a user to the list of datagathering admins.

    :param username: name of the user to remove from datagathering user admin list
    :type username: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_datagathering_admin_remove', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           datagathering_admin_remove_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    user_id = convert_user_name_or_id_to_id(username, context)

    datagathering_admin_to_remove = DatagatheringAdmin.get(user_id=user_id)

    if datagathering_admin_to_remove is None:
        raise toolkit.ObjectNotFound("DatagatheringAdmin with user_id '{0}' doesn't exist.".format(user_id))

    datagathering_admin_to_remove.delete()
    model.repo.commit()
