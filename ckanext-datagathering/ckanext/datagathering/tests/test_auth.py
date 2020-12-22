import json
from nose import tools as nosetools

import ckan.plugins.toolkit as toolkit
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.datagathering.tests import DatagatheringFunctionalTestBase


class TestDatagatheringAuthIndex(DatagatheringFunctionalTestBase):

    def test_auth_anon_user_can_view_datagathering_index(self):
        '''An anon (not logged in) user can view the Datagatherings index.'''
        app = self._get_test_app()

        app.get("/datagathering", status=200)

    def test_auth_logged_in_user_can_view_datagathering_index(self):
        '''
        A logged in user can view the Datagathering index.
        '''
        app = self._get_test_app()

        user = factories.User()

        app.get("/datagathering", status=200,
                extra_environ={'REMOTE_USER': str(user["name"])})

    def test_auth_anon_user_cant_see_add_datagathering_button(self):
        '''
        An anon (not logged in) user can't see the Add Datagathering button on the
        datagathering index page.
        '''
        app = self._get_test_app()

        response = app.get("/datagathering", status=200)

        # test for new datagathering link in response
        response.mustcontain(no="/datagathering/new")

    def test_auth_logged_in_user_cant_see_add_datagathering_button(self):
        '''
        A logged in user can't see the Add Datagathering button on the datagathering
        index page.
        '''
        app = self._get_test_app()
        user = factories.User()

        response = app.get("/datagathering", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new datagathering link in response
        response.mustcontain(no="/datagathering/new")

    def test_auth_sysadmin_can_see_add_datagathering_button(self):
        '''
        A sysadmin can see the Add Datagathering button on the datagathering index
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        response = app.get("/datagathering", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new datagathering link in response
        response.mustcontain("/datagathering/new")


class TestDatagatheringAuthDetails(DatagatheringFunctionalTestBase):
    def test_auth_anon_user_can_view_datagathering_details(self):
        '''
        An anon (not logged in) user can view an individual Datagathering details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/my-datagathering', status=200)

    def test_auth_logged_in_user_can_view_datagathering_details(self):
        '''
        A logged in user can view an individual Datagathering details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_see_manage_button(self):
        '''
        An anon (not logged in) user can't see the Manage button on an individual
        datagathering details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/datagathering/my-datagathering', status=200)

        # test for url to edit page
        response.mustcontain(no="/datagathering/edit/my-datagathering")

    def test_auth_logged_in_user_can_see_manage_button(self):
        '''
        A logged in user can't see the Manage button on an individual datagathering
        details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/datagathering/my-datagathering', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain(no="/datagathering/edit/my-datagathering")

    def test_auth_sysadmin_can_see_manage_button(self):
        '''
        A sysadmin can see the Manage button on an individual datagathering details
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/datagathering/my-datagathering', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain("/datagathering/edit/my-datagathering")

    def test_auth_datagathering_show_anon_can_access(self):
        '''
        Anon user can request datagathering show.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_show?id=my-datagathering',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_datagathering_show_normal_user_can_access(self):
        '''
        Normal logged in user can request datagathering show.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_show?id=my-datagathering',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_datagathering_show_sysadmin_can_access(self):
        '''
        Normal logged in user can request datagathering show.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_show?id=my-datagathering',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestDatagatheringAuthCreate(DatagatheringFunctionalTestBase):

    def test_auth_anon_user_cant_view_create_datagathering(self):
        '''
        An anon (not logged in) user can't access the create datagathering page.
        '''
        app = self._get_test_app()
        app.get("/datagathering/new", status=302)

    def test_auth_logged_in_user_cant_view_create_datagathering_page(self):
        '''
        A logged in user can't access the create datagathering page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/datagathering/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_create_datagathering_page(self):
        '''
        A sysadmin can access the create datagathering page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/datagathering/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})


class TestDatagatheringAuthList(DatagatheringFunctionalTestBase):

    def test_auth_datagathering_list_anon_can_access(self):
        '''
        Anon user can request datagathering list.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_list',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_datagathering_list_normal_user_can_access(self):
        '''
        Normal logged in user can request datagathering list.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_datagathering_list_sysadmin_can_access(self):
        '''
        Normal logged in user can request datagathering list.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/api/3/action/ckanext_datagathering_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestDatagatheringAuthEdit(DatagatheringFunctionalTestBase):

    def test_auth_anon_user_cant_view_edit_datagathering_page(self):
        '''
        An anon (not logged in) user can't access the datagathering edit page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/edit/my-datagathering', status=302)

    def test_auth_logged_in_user_cant_view_edit_datagathering_page(self):
        '''
        A logged in user can't access the datagathering edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/edit/my-datagathering', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_edit_datagathering_page(self):
        '''
        A sysadmin can access the datagathering edit page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/edit/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_datagathering_admin_can_view_edit_datagathering_page(self):
        '''
        A datagathering admin can access the datagathering edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/edit/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_manage_datasets(self):
        '''
        An anon (not logged in) user can't access the datagathering manage datasets page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/manage_datasets/my-datagathering', status=302)

    def test_auth_logged_in_user_cant_view_manage_datasets(self):
        '''
        A logged in user (not sysadmin) can't access the datagathering manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/manage_datasets/my-datagathering', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_manage_datasets(self):
        '''
        A sysadmin can access the datagathering manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/manage_datasets/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_datagathering_admin_can_view_manage_datasets(self):
        '''
        A datagathering admin can access the datagathering manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/manage_datasets/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_delete_datagathering_page(self):
        '''
        An anon (not logged in) user can't access the datagathering delete page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/delete/my-datagathering', status=302)

    def test_auth_logged_in_user_cant_view_delete_datagathering_page(self):
        '''
        A logged in user can't access the datagathering delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/delete/my-datagathering', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_delete_datagathering_page(self):
        '''
        A sysadmin can access the datagathering delete page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/delete/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_datagathering_admin_can_view_delete_datagathering_page(self):
        '''
        A datagathering admin can access the datagathering delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='datagathering', name='my-datagathering')

        app.get('/datagathering/delete/my-datagathering', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_addtodatagathering_dropdown_dataset_datagathering_list(self):
        '''
        An anonymous user can't view the 'Add to datagathering' dropdown selector
        from a datasets datagathering list page.
        '''
        app = self._get_test_app()

        factories.Dataset(name='my-datagathering', type='datagathering')
        factories.Dataset(name='my-dataset')

        datagathering_list_response = app.get('/dataset/datagatherings/my-dataset', status=200)

        nosetools.assert_false('datagathering-add' in datagathering_list_response.forms)

    def test_auth_normal_user_cant_view_addtodatagathering_dropdown_dataset_datagathering_list(self):
        '''
        A normal (logged in) user can't view the 'Add to datagathering' dropdown
        selector from a datasets datagathering list page.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(name='my-datagathering', type='datagathering')
        factories.Dataset(name='my-dataset')

        datagathering_list_response = app.get('/dataset/datagatherings/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_false('datagathering-add' in datagathering_list_response.forms)

    def test_auth_sysadmin_can_view_addtodatagathering_dropdown_dataset_datagathering_list(self):
        '''
        A sysadmin can view the 'Add to datagathering' dropdown selector from a
        datasets datagathering list page.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(name='my-datagathering', type='datagathering')
        factories.Dataset(name='my-dataset')

        datagathering_list_response = app.get('/dataset/datagatherings/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('datagathering-add' in datagathering_list_response.forms)

    def test_auth_datagathering_admin_can_view_addtodatagathering_dropdown_dataset_datagathering_list(self):
        '''
        A datagathering admin can view the 'Add to datagathering' dropdown selector from
        a datasets datagathering list page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user['name'])

        factories.Dataset(name='my-datagathering', type='datagathering')
        factories.Dataset(name='my-dataset')

        datagathering_list_response = app.get('/dataset/datagatherings/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('datagathering-add' in datagathering_list_response.forms)


class TestDatagatheringPackageAssociationCreate(DatagatheringFunctionalTestBase):

    def test_datagathering_package_association_create_no_user(self):
        '''
        Calling datagathering package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_package_association_create',
                                context=context)

    def test_datagathering_package_association_create_sysadmin(self):
        '''
        Calling datagathering package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_package_association_create',
                          context=context)

    def test_datagathering_package_association_create_datagathering_admin(self):
        '''
        Calling datagathering package association create by a datagathering admin
        doesn't raise NotAuthorized.
        '''
        datagathering_admin = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=datagathering_admin['name'])

        context = {'user': datagathering_admin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_package_association_create',
                          context=context)

    def test_datagathering_package_association_create_unauthorized_creds(self):
        '''
        Calling datagathering package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_package_association_create',
                                context=context)


class TestDatagatheringPackageAssociationDelete(DatagatheringFunctionalTestBase):

    def test_datagathering_package_association_delete_no_user(self):
        '''
        Calling datagathering package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_package_association_delete',
                                context=context)

    def test_datagathering_package_association_delete_sysadmin(self):
        '''
        Calling datagathering package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_package_association_delete',
                          context=context)

    def test_datagathering_package_association_delete_datagathering_admin(self):
        '''
        Calling datagathering package association create by a datagathering admin
        doesn't raise NotAuthorized.
        '''
        datagathering_admin = factories.User()

        # Make user a datagathering admin
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=datagathering_admin['name'])

        context = {'user': datagathering_admin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_package_association_delete',
                          context=context)

    def test_datagathering_package_association_delete_unauthorized_creds(self):
        '''
        Calling datagathering package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_package_association_delete',
                                context=context)


class TestDatagatheringAdminAddAuth(DatagatheringFunctionalTestBase):

    def test_datagathering_admin_add_no_user(self):
        '''
        Calling datagathering admin add with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_add', context=context)

    def test_datagathering_admin_add_correct_creds(self):
        '''
        Calling datagathering admin add by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_admin_add', context=context)

    def test_datagathering_admin_add_unauthorized_creds(self):
        '''
        Calling datagathering admin add with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_add', context=context)


class TestDatagatheringAdminRemoveAuth(DatagatheringFunctionalTestBase):

    def test_datagathering_admin_remove_no_user(self):
        '''
        Calling datagathering admin remove with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_remove', context=context)

    def test_datagathering_admin_remove_correct_creds(self):
        '''
        Calling datagathering admin remove by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_admin_remove', context=context)

    def test_datagathering_admin_remove_unauthorized_creds(self):
        '''
        Calling datagathering admin remove with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_remove', context=context)


class TestDatagatheringAdminListAuth(DatagatheringFunctionalTestBase):

    def test_datagathering_admin_list_no_user(self):
        '''
        Calling datagathering admin list with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_list', context=context)

    def test_datagathering_admin_list_correct_creds(self):
        '''
        Calling datagathering admin list by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_datagathering_admin_list', context=context)

    def test_datagathering_admin_list_unauthorized_creds(self):
        '''
        Calling datagathering admin list with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_datagathering_admin_list', context=context)


class TestDatagatheringAuthManageDatagatheringAdmins(DatagatheringFunctionalTestBase):

    def test_auth_anon_user_cant_view_datagathering_admin_manage_page(self):
        '''
        An anon (not logged in) user can't access the manage datagathering admin
        page.
        '''
        app = self._get_test_app()
        app.get("/datagathering/new", status=302)

    def test_auth_logged_in_user_cant_view_datagathering_admin_manage_page(self):
        '''
        A logged in user can't access the manage datagathering admin page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/datagathering/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_datagathering_admin_manage_page(self):
        '''
        A sysadmin can access the manage datagathering admin page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/datagathering/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})
