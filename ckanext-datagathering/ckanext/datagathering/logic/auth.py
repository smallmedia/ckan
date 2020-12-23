import ckan.plugins.toolkit as toolkit
import ckan.model as model

from ckanext.datagathering.model import DatagatheringAdmin

import logging
log = logging.getLogger(__name__)


def _is_datagathering_admin(context):
    '''
    Determines whether user in context is in the datagathering admin list.
    '''
    user = context.get('user', '')
    userobj = model.User.get(user)
    return DatagatheringAdmin.is_user_datagathering_admin(userobj)


def create(context, data_dict):
    '''Create a Datagathering.

       Only sysadmin or users listed as Datagathering Admins can create a Datagathering.
    '''
    return {'success': _is_datagathering_admin(context)}


def delete(context, data_dict):
    '''Delete a Datagathering.

       Only sysadmin or users listed as Datagathering Admins can delete a Datagathering.
    '''
    return {'success': _is_datagathering_admin(context)}


def update(context, data_dict):
    '''Update a Datagathering.

       Only sysadmin or users listed as Datagathering Admins can update a Datagathering.
    '''
    return {'success': _is_datagathering_admin(context)}


@toolkit.auth_allow_anonymous_access
def show(context, data_dict):
    '''All users can access a datagathering show'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def list(context, data_dict):
    '''All users can access a datagathering list'''
    return {'success': True}


def package_association_create(context, data_dict):
    '''Create a package datagathering association.

       Only sysadmins or user listed as Datagathering Admins can create a
       package/datagathering association.
    '''
    return {'success': _is_datagathering_admin(context)}


def package_association_delete(context, data_dict):
    '''Delete a package datagathering association.

       Only sysadmins or user listed as Datagathering Admins can delete a
       package/datagathering association.
    '''
    return {'success': _is_datagathering_admin(context)}


@toolkit.auth_allow_anonymous_access
def datagathering_package_list(context, data_dict):
    '''All users can access a datagathering's package list'''
    return {'success': True}


@toolkit.auth_allow_anonymous_access
def package_datagathering_list(context, data_dict):
    '''All users can access a packages's datagathering list'''
    return {'success': True}


def add_datagathering_admin(context, data_dict):
    '''Only sysadmins can add users to datagathering admin list.'''
    return {'success': False}


def remove_datagathering_admin(context, data_dict):
    '''Only sysadmins can remove users from datagathering admin list.'''
    return {'success': False}


def datagathering_admin_list(context, data_dict):
    '''Only sysadmins can list datagathering admin users.'''
    return {'success': False}

def datagathering_upload(context, data_dict):
    '''Only sysadmins can upload images.'''
    return {'success': _is_datagathering_admin(context)}
