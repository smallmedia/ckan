import logging

import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
import ckan.lib.navl.dictization_functions

from ckanext.infographic.logic.schema import (
    infographic_package_association_delete_schema,
    infographic_admin_remove_schema)

from ckanext.infographic.model import InfographicPackageAssociation, InfographicAdmin

validate = ckan.lib.navl.dictization_functions.validate

log = logging.getLogger(__name__)


def infographic_delete(context, data_dict):
    '''Delete a infographic. Infographic delete cascades to
    InfographicPackageAssociation objects.

    :param id: the id or name of the infographic to delete
    :type id: string
    '''

    model = context['model']
    id = toolkit.get_or_bust(data_dict, 'id')

    entity = model.Package.get(id)

    if entity is None:
        raise toolkit.ObjectNotFound

    toolkit.check_access('ckanext_infographic_delete', context, data_dict)

    entity.purge()
    model.repo.commit()


def infographic_package_association_delete(context, data_dict):
    '''Delete an association between a infographic and a package.

    :param infographic_id: id or name of the infographic in the association
    :type infographic_id: string

    :param package_id: id or name of the package in the association
    :type package_id: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_infographic_package_association_delete',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, infographic_package_association_delete_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, infographic_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'infographic_id'])

    infographic_package_association = InfographicPackageAssociation.get(
        package_id=package_id, infographic_id=infographic_id)

    if infographic_package_association is None:
        raise toolkit.ObjectNotFound("InfographicPackageAssociation with package_id '{0}' and infographic_id '{1}' doesn't exist.".format(package_id, infographic_id))

    # delete the association
    infographic_package_association.delete()
    model.repo.commit()


def infographic_admin_remove(context, data_dict):
    '''Remove a user to the list of infographic admins.

    :param username: name of the user to remove from infographic user admin list
    :type username: string
    '''

    model = context['model']

    toolkit.check_access('ckanext_infographic_admin_remove', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(data_dict,
                                           infographic_admin_remove_schema(),
                                           context)

    if errors:
        raise toolkit.ValidationError(errors)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    user_id = convert_user_name_or_id_to_id(username, context)

    infographic_admin_to_remove = InfographicAdmin.get(user_id=user_id)

    if infographic_admin_to_remove is None:
        raise toolkit.ObjectNotFound("InfographicAdmin with user_id '{0}' doesn't exist.".format(user_id))

    infographic_admin_to_remove.delete()
    model.repo.commit()
