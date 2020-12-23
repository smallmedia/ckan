import logging

import ckan.lib.uploader as uploader
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
from ckan.logic.converters import convert_user_name_or_id_to_id
from ckan.lib.navl.dictization_functions import validate

import ckanext.infographic.logic.converters as infographic_converters
import ckanext.infographic.logic.schema as infographic_schema
from ckanext.infographic.model import InfographicPackageAssociation, InfographicAdmin

convert_package_name_or_id_to_title_or_name = \
    infographic_converters.convert_package_name_or_id_to_title_or_name
infographic_package_association_create_schema = \
    infographic_schema.infographic_package_association_create_schema
infographic_admin_add_schema = infographic_schema.infographic_admin_add_schema

log = logging.getLogger(__name__)


def infographic_create(context, data_dict):
    '''Upload the image and continue with package creation.'''

    # force type to 'infographic'
    data_dict['type'] = 'infographic'

    # If get_uploader is available (introduced for IUploader in CKAN 2.5), use
    # it, otherwise use the default uploader.
    # https://github.com/ckan/ckan/pull/2510
    try:
        upload = uploader.get_uploader('infographic')
    except AttributeError:
        upload = uploader.Upload('infographic')

    upload.update_data_dict(data_dict, 'image_url',
                            'image_upload', 'clear_upload')

    upload.upload(uploader.get_max_image_size())

    pkg = toolkit.get_action('package_create')(context, data_dict)

    return pkg


def infographic_package_association_create(context, data_dict):
    '''Create an association between a infographic and a package.

    :param infographic_id: id or name of the infographic to associate
    :type infographic_id: string

    :param package_id: id or name of the package to associate
    :type package_id: string
    '''

    toolkit.check_access('ckanext_infographic_package_association_create',
                         context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, infographic_package_association_create_schema(), context)

    if errors:
        raise toolkit.ValidationError(errors)

    package_id, infographic_id = toolkit.get_or_bust(validated_data_dict,
                                                  ['package_id',
                                                   'infographic_id'])

    if InfographicPackageAssociation.exists(package_id=package_id,
                                         infographic_id=infographic_id):
        raise toolkit.ValidationError("InfographicPackageAssociation with package_id '{0}' and infographic_id '{1}' already exists.".format(package_id, infographic_id),
                                      error_summary=u"The dataset, {0}, is already in the infographic".format(convert_package_name_or_id_to_title_or_name(package_id, context)))

    # create the association
    return InfographicPackageAssociation.create(package_id=package_id,
                                             infographic_id=infographic_id)


def infographic_admin_add(context, data_dict):
    '''Add a user to the list of infographic admins.

    :param username: name of the user to add to infographic user admin list
    :type username: string
    '''

    toolkit.check_access('ckanext_infographic_admin_add', context, data_dict)

    # validate the incoming data_dict
    validated_data_dict, errors = validate(
        data_dict, infographic_admin_add_schema(), context)

    username = toolkit.get_or_bust(validated_data_dict, 'username')
    try:
        user_id = convert_user_name_or_id_to_id(username, context)
    except toolkit.Invalid:
        raise toolkit.ObjectNotFound

    if errors:
        raise toolkit.ValidationError(errors)

    if InfographicAdmin.exists(user_id=user_id):
        raise toolkit.ValidationError("InfographicAdmin with user_id '{0}' already exists.".format(user_id),
                                      error_summary=u"User '{0}' is already a Infographic Admin.".format(username))

    # create infographic admin entry
    return InfographicAdmin.create(user_id=user_id)


def infographic_upload(context, data_dict):
    ''' Uploads images to be used in infographic content.

    '''
    toolkit.check_access('ckanext_infographic_upload', context, data_dict)

    try:
        upload = uploader.get_uploader('infographic_image')
    except AttributeError:
        upload = uploader.Upload('infographic_image')

    upload.update_data_dict(data_dict, 'image_url', 'upload', 'clear_upload')
    upload.upload(uploader.get_max_image_size())

    image_url = data_dict.get('image_url')
    if image_url:
        image_url = h.url_for_static(
           'uploads/infographic_image/{}'.format(image_url),
            qualified = True
        )
    return {'url': image_url}
