import logging

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
from ckan.lib.navl.dictization_functions import validate

import ckanext.datagathering.logic.converters as datagathering_converters
import ckanext.datagathering.logic.schema as datagathering_schema
from ckanext.datagathering.model import DatagatheringPackageAssociation, DatagatheringAdmin

convert_package_name_or_id_to_title_or_name = \
    datagathering_converters.convert_package_name_or_id_to_title_or_name
datagathering_package_association_create_schema = \
    datagathering_schema.datagathering_package_association_create_schema
datagathering_admin_add_schema = datagathering_schema.datagathering_admin_add_schema

log = logging.getLogger(__name__)


def datagathering_create(context, data_dict):
    '''Upload the image and continue with package creation.'''

    # force type to 'datagathering'
    data_dict['type'] = 'datagathering'

    # If get_uploader is available (introduced for IUploader in CKAN 2.5), use
    # it, otherwise use the default uploader.
    # https://github.com/ckan/ckan/pull/2510
    try:
        upload = uploader.get_uploader('datagathering')
    except AttributeError:
        upload = uploader.Upload('datagathering')

    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    upload.upload(uploader.get_max_image_size())

    pkg = toolkit.get_action('package_create')(context, data_dict)

    return pkg


def datagathering_package_association_create(context, data_dict):
    '''Create an association between a datagathering and a package.

    :param datagathering_id: id or name of the datagathering to associate
    :type datagathering_id: string

    :param package_id: id or name of the package to associate
    :type package_id: string
    '''

    toolkit.check_access('ckanext_datagathering_package_association_create',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, datagathering_package_association_create_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, datagathering_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'datagathering_id'])

    if DatagatheringPackageAssociation.exists(package_id=package_id,
                                         datagathering_id=datagathering_id):
        raise toolkit.ValidationError("DatagatheringPackageAssociation with package_id '{0}' and datagathering_id '{1}' already exists.".format(package_id, datagathering_id),
                                      error_summary=u"The dataset, {0}, is already in the datagathering".format(convert_package_name_or_id_to_title_or_name(package_id, context)))

    # create the association
    return DatagatheringPackageAssociation.create(package_id=package_id,
                                             datagathering_id=datagathering_id)


def datagathering_admin_add(context, data_dict):
    '''Add a user to the list of datagathering admins.

    :param username: name of the user to add to datagathering user admin list
    :type username: string
    '''

    toolkit.check_access('ckanext_datagathering_admin_add', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, datagathering_admin_add_schema(), context)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    try:
        user_id = convert_user_name_or_id_to_id(username, context)
    except toolkit.Invalid:
        raise toolkit.ObjectNotFound

    if errors:
        raise toolkit.ValidationError(errors)

    if DatagatheringAdmin.exists(user_id=user_id):
        raise toolkit.ValidationError("DatagatheringAdmin with user_id '{0}' already exists.".format(user_id),
                                      error_summary=u"User '{0}' is already a Datagathering Admin.".format(username))

    # create datagathering admin entry
    return DatagatheringAdmin.create(user_id=user_id)


def datagathering_upload(context, data_dict):
    ''' Uploads images to be used in datagathering content.

    '''
    toolkit.check_access('ckanext_datagathering_upload', context, data_dict)

    try:
        upload = uploader.get_uploader('datagathering_image')
    except AttributeError:
        upload = uploader.Upload('datagathering_image')

    upload.update_data_dict(data_dict, 'image_url', 'upload', 'clear_upload')
    upload.upload(uploader.get_max_image_size())

    image_url = data_dict.get('image_url')
    if image_url:
        image_url = h.url_for_static(
           'uploads/datagathering_image/{}'.format(image_url),
            qualified = True
        )
    return {'url': image_url}
