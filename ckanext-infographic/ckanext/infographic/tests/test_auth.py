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

from ckanext.infographic.tests import InfographicFunctionalTestBase


class TestInfographicAuthIndex(InfographicFunctionalTestBase):

    def test_auth_anon_user_can_view_infographic_index(self):
        '''An anon (not logged in) user can view the Infographics index.'''
        app = self._get_test_app()

        app.get("/infographic", status=200)

    def test_auth_logged_in_user_can_view_infographic_index(self):
        '''
        A logged in user can view the Infographic index.
        '''
        app = self._get_test_app()

        user = factories.User()

        app.get("/infographic", status=200,
                extra_environ={'REMOTE_USER': str(user["name"])})

    def test_auth_anon_user_cant_see_add_infographic_button(self):
        '''
        An anon (not logged in) user can't see the Add Infographic button on the
        infographic index page.
        '''
        app = self._get_test_app()

        response = app.get("/infographic", status=200)

        # test for new infographic link in response
        response.mustcontain(no="/infographic/new")

    def test_auth_logged_in_user_cant_see_add_infographic_button(self):
        '''
        A logged in user can't see the Add Infographic button on the infographic
        index page.
        '''
        app = self._get_test_app()
        user = factories.User()

        response = app.get("/infographic", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new infographic link in response
        response.mustcontain(no="/infographic/new")

    def test_auth_sysadmin_can_see_add_infographic_button(self):
        '''
        A sysadmin can see the Add Infographic button on the infographic index
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        response = app.get("/infographic", status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for new infographic link in response
        response.mustcontain("/infographic/new")


class TestInfographicAuthDetails(InfographicFunctionalTestBase):
    def test_auth_anon_user_can_view_infographic_details(self):
        '''
        An anon (not logged in) user can view an individual Infographic details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/my-infographic', status=200)

    def test_auth_logged_in_user_can_view_infographic_details(self):
        '''
        A logged in user can view an individual Infographic details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_see_manage_button(self):
        '''
        An anon (not logged in) user can't see the Manage button on an individual
        infographic details page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/infographic/my-infographic', status=200)

        # test for url to edit page
        response.mustcontain(no="/infographic/edit/my-infographic")

    def test_auth_logged_in_user_can_see_manage_button(self):
        '''
        A logged in user can't see the Manage button on an individual infographic
        details page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/infographic/my-infographic', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain(no="/infographic/edit/my-infographic")

    def test_auth_sysadmin_can_see_manage_button(self):
        '''
        A sysadmin can see the Manage button on an individual infographic details
        page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/infographic/my-infographic', status=200,
                           extra_environ={'REMOTE_USER': str(user['name'])})

        # test for url to edit page
        response.mustcontain("/infographic/edit/my-infographic")

    def test_auth_infographic_show_anon_can_access(self):
        '''
        Anon user can request infographic show.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_show?id=my-infographic',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_infographic_show_normal_user_can_access(self):
        '''
        Normal logged in user can request infographic show.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_show?id=my-infographic',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_infographic_show_sysadmin_can_access(self):
        '''
        Normal logged in user can request infographic show.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_show?id=my-infographic',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestInfographicAuthCreate(InfographicFunctionalTestBase):

    def test_auth_anon_user_cant_view_create_infographic(self):
        '''
        An anon (not logged in) user can't access the create infographic page.
        '''
        app = self._get_test_app()
        app.get("/infographic/new", status=302)

    def test_auth_logged_in_user_cant_view_create_infographic_page(self):
        '''
        A logged in user can't access the create infographic page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/infographic/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_create_infographic_page(self):
        '''
        A sysadmin can access the create infographic page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/infographic/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})


class TestInfographicAuthList(InfographicFunctionalTestBase):

    def test_auth_infographic_list_anon_can_access(self):
        '''
        Anon user can request infographic list.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_list',
                           status=200)

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_infographic_list_normal_user_can_access(self):
        '''
        Normal logged in user can request infographic list.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])

    def test_auth_infographic_list_sysadmin_can_access(self):
        '''
        Normal logged in user can request infographic list.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/api/3/action/ckanext_infographic_list',
                           status=200, extra_environ={'REMOTE_USER': str(user['name'])})

        json_response = json.loads(response.body)

        nosetools.assert_true(json_response['success'])


class TestInfographicAuthEdit(InfographicFunctionalTestBase):

    def test_auth_anon_user_cant_view_edit_infographic_page(self):
        '''
        An anon (not logged in) user can't access the infographic edit page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/edit/my-infographic', status=302)

    def test_auth_logged_in_user_cant_view_edit_infographic_page(self):
        '''
        A logged in user can't access the infographic edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/edit/my-infographic', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_edit_infographic_page(self):
        '''
        A sysadmin can access the infographic edit page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/edit/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_infographic_admin_can_view_edit_infographic_page(self):
        '''
        A infographic admin can access the infographic edit page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/edit/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_manage_datasets(self):
        '''
        An anon (not logged in) user can't access the infographic manage datasets page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/manage_datasets/my-infographic', status=302)

    def test_auth_logged_in_user_cant_view_manage_datasets(self):
        '''
        A logged in user (not sysadmin) can't access the infographic manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/manage_datasets/my-infographic', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_manage_datasets(self):
        '''
        A sysadmin can access the infographic manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/manage_datasets/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_infographic_admin_can_view_manage_datasets(self):
        '''
        A infographic admin can access the infographic manage datasets page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/manage_datasets/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_delete_infographic_page(self):
        '''
        An anon (not logged in) user can't access the infographic delete page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/delete/my-infographic', status=302)

    def test_auth_logged_in_user_cant_view_delete_infographic_page(self):
        '''
        A logged in user can't access the infographic delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/delete/my-infographic', status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_delete_infographic_page(self):
        '''
        A sysadmin can access the infographic delete page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/delete/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_infographic_admin_can_view_delete_infographic_page(self):
        '''
        A infographic admin can access the infographic delete page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user['name'])

        factories.Dataset(type='infographic', name='my-infographic')

        app.get('/infographic/delete/my-infographic', status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_anon_user_cant_view_addtoinfographic_dropdown_dataset_infographic_list(self):
        '''
        An anonymous user can't view the 'Add to infographic' dropdown selector
        from a datasets infographic list page.
        '''
        app = self._get_test_app()

        factories.Dataset(name='my-infographic', type='infographic')
        factories.Dataset(name='my-dataset')

        infographic_list_response = app.get('/dataset/infographics/my-dataset', status=200)

        nosetools.assert_false('infographic-add' in infographic_list_response.forms)

    def test_auth_normal_user_cant_view_addtoinfographic_dropdown_dataset_infographic_list(self):
        '''
        A normal (logged in) user can't view the 'Add to infographic' dropdown
        selector from a datasets infographic list page.
        '''
        user = factories.User()
        app = self._get_test_app()

        factories.Dataset(name='my-infographic', type='infographic')
        factories.Dataset(name='my-dataset')

        infographic_list_response = app.get('/dataset/infographics/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_false('infographic-add' in infographic_list_response.forms)

    def test_auth_sysadmin_can_view_addtoinfographic_dropdown_dataset_infographic_list(self):
        '''
        A sysadmin can view the 'Add to infographic' dropdown selector from a
        datasets infographic list page.
        '''
        user = factories.Sysadmin()
        app = self._get_test_app()

        factories.Dataset(name='my-infographic', type='infographic')
        factories.Dataset(name='my-dataset')

        infographic_list_response = app.get('/dataset/infographics/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('infographic-add' in infographic_list_response.forms)

    def test_auth_infographic_admin_can_view_addtoinfographic_dropdown_dataset_infographic_list(self):
        '''
        A infographic admin can view the 'Add to infographic' dropdown selector from
        a datasets infographic list page.
        '''
        app = self._get_test_app()
        user = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user['name'])

        factories.Dataset(name='my-infographic', type='infographic')
        factories.Dataset(name='my-dataset')

        infographic_list_response = app.get('/dataset/infographics/my-dataset', status=200,
                                         extra_environ={'REMOTE_USER': str(user['name'])})

        nosetools.assert_true('infographic-add' in infographic_list_response.forms)


class TestInfographicPackageAssociationCreate(InfographicFunctionalTestBase):

    def test_infographic_package_association_create_no_user(self):
        '''
        Calling infographic package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_package_association_create',
                                context=context)

    def test_infographic_package_association_create_sysadmin(self):
        '''
        Calling infographic package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_package_association_create',
                          context=context)

    def test_infographic_package_association_create_infographic_admin(self):
        '''
        Calling infographic package association create by a infographic admin
        doesn't raise NotAuthorized.
        '''
        infographic_admin = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=infographic_admin['name'])

        context = {'user': infographic_admin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_package_association_create',
                          context=context)

    def test_infographic_package_association_create_unauthorized_creds(self):
        '''
        Calling infographic package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_package_association_create',
                                context=context)


class TestInfographicPackageAssociationDelete(InfographicFunctionalTestBase):

    def test_infographic_package_association_delete_no_user(self):
        '''
        Calling infographic package association create with no user raises
        NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_package_association_delete',
                                context=context)

    def test_infographic_package_association_delete_sysadmin(self):
        '''
        Calling infographic package association create by a sysadmin doesn't
        raise NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_package_association_delete',
                          context=context)

    def test_infographic_package_association_delete_infographic_admin(self):
        '''
        Calling infographic package association create by a infographic admin
        doesn't raise NotAuthorized.
        '''
        infographic_admin = factories.User()

        # Make user a infographic admin
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=infographic_admin['name'])

        context = {'user': infographic_admin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_package_association_delete',
                          context=context)

    def test_infographic_package_association_delete_unauthorized_creds(self):
        '''
        Calling infographic package association create with unauthorized user
        raises NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_package_association_delete',
                                context=context)


class TestInfographicAdminAddAuth(InfographicFunctionalTestBase):

    def test_infographic_admin_add_no_user(self):
        '''
        Calling infographic admin add with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_add', context=context)

    def test_infographic_admin_add_correct_creds(self):
        '''
        Calling infographic admin add by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_admin_add', context=context)

    def test_infographic_admin_add_unauthorized_creds(self):
        '''
        Calling infographic admin add with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_add', context=context)


class TestInfographicAdminRemoveAuth(InfographicFunctionalTestBase):

    def test_infographic_admin_remove_no_user(self):
        '''
        Calling infographic admin remove with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_remove', context=context)

    def test_infographic_admin_remove_correct_creds(self):
        '''
        Calling infographic admin remove by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_admin_remove', context=context)

    def test_infographic_admin_remove_unauthorized_creds(self):
        '''
        Calling infographic admin remove with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_remove', context=context)


class TestInfographicAdminListAuth(InfographicFunctionalTestBase):

    def test_infographic_admin_list_no_user(self):
        '''
        Calling infographic admin list with no user raises NotAuthorized.
        '''

        context = {'user': None, 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_list', context=context)

    def test_infographic_admin_list_correct_creds(self):
        '''
        Calling infographic admin list by a sysadmin doesn't raise
        NotAuthorized.
        '''
        a_sysadmin = factories.Sysadmin()
        context = {'user': a_sysadmin['name'], 'model': None}
        helpers.call_auth('ckanext_infographic_admin_list', context=context)

    def test_infographic_admin_list_unauthorized_creds(self):
        '''
        Calling infographic admin list with unauthorized user raises
        NotAuthorized.
        '''
        not_a_sysadmin = factories.User()
        context = {'user': not_a_sysadmin['name'], 'model': None}
        nosetools.assert_raises(toolkit.NotAuthorized, helpers.call_auth,
                                'ckanext_infographic_admin_list', context=context)


class TestInfographicAuthManageInfographicAdmins(InfographicFunctionalTestBase):

    def test_auth_anon_user_cant_view_infographic_admin_manage_page(self):
        '''
        An anon (not logged in) user can't access the manage infographic admin
        page.
        '''
        app = self._get_test_app()
        app.get("/infographic/new", status=302)

    def test_auth_logged_in_user_cant_view_infographic_admin_manage_page(self):
        '''
        A logged in user can't access the manage infographic admin page.
        '''
        app = self._get_test_app()
        user = factories.User()
        app.get("/infographic/new", status=401,
                extra_environ={'REMOTE_USER': str(user['name'])})

    def test_auth_sysadmin_can_view_infographic_admin_manage_page(self):
        '''
        A sysadmin can access the manage infographic admin page.
        '''
        app = self._get_test_app()
        user = factories.Sysadmin()
        app.get("/infographic/new", status=200,
                extra_environ={'REMOTE_USER': str(user['name'])})
