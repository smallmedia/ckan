import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.infographic.model import InfographicAdmin

import logging
log = logging.getLogger(__name__)


def _is_infographic_admin(context):
    '''
    Determines whether user in context is in the infographic admin list.
    '''
    user = context.get('user', '')
    userobj = model.User.get(user)
    return InfographicAdmin.is_user_infographic_admin(userobj)


def create(context, data_dict):
    '''Create a Infographic.

       Only sysadmin or users listed as Infographic Admins can create a Infographic.
    '''
    return {'success': _is_infographic_admin(context)}


def delete(context, data_dict):
    '''Delete a Infographic.

       Only sysadmin or users listed as Infographic Admins can delete a Infographic.
    '''
    return {'success': _is_infographic_admin(context)}


def update(context, data_dict):
    '''Update a Infographic.

       Only sysadmin or users listed as Infographic Admins can update a Infographic.
    '''
    return {'success': _is_infographic_admin(context)}


@toolkit.auth_allow_anonymous_access
def show(context, data_dict):
    '''All users can access a infographic show'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def list(context, data_dict):
    '''All users can access a infographic list'''
    return {'success': True}


def package_association_create(context, data_dict):
    '''Create a package infographic association.

       Only sysadmins or user listed as Infographic Admins can create a
       package/infographic association.
    '''
    return {'success': _is_infographic_admin(context)}


def package_association_delete(context, data_dict):
    '''Delete a package infographic association.

       Only sysadmins or user listed as Infographic Admins can delete a
       package/infographic association.
    '''
    return {'success': _is_infographic_admin(context)}


@toolkit.auth_allow_anonymous_access
def infographic_package_list(context, data_dict):
    '''All users can access a infographic's package list'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def package_infographic_list(context, data_dict):
    '''All users can access a packages's infographic list'''
    return {'success': True}


def add_infographic_admin(context, data_dict):
    '''Only sysadmins can add users to infographic admin list.'''
    return {'success': False}


def remove_infographic_admin(context, data_dict):
    '''Only sysadmins can remove users from infographic admin list.'''
    return {'success': False}


def infographic_admin_list(context, data_dict):
    '''Only sysadmins can list infographic admin users.'''
    return {'success': False}

def infographic_upload(context, data_dict):
    '''Only sysadmins can upload images.'''
    return {'success': _is_infographic_admin(context)}
