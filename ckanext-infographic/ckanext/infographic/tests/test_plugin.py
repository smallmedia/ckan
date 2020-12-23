from ckan.lib.helpers import url_for
from nose import tools as nosetools
from nose import SkipTest

from ckan.plugins import toolkit as tk
import ckan.model as model
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

from ckanext.infographic.model import InfographicPackageAssociation
from ckanext.infographic.tests import InfographicFunctionalTestBase

import logging
log = logging.getLogger(__name__)

submit_and_follow = helpers.submit_and_follow


class TestInfographicIndex(InfographicFunctionalTestBase):

    def test_infographics_redirects_to_infographic(self):
        '''/infographics redirects to /infographic.'''
        app = self._get_test_app()
        response = app.get('/infographics', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/infographic')

    def test_infographics_redirects_to_infographic_for_item(self):
        '''/infographics/ redirects to /infographic.'''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get('/infographics/my-infographic', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/infographic/my-infographic')

    def test_infographic_listed_on_index(self):
        '''
        An added Infographic will appear on the Infographic index page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='infographic', name='my-infographic')

        response = app.get("/infographic", status=200)
        response.mustcontain("1 infographic found")
        response.mustcontain("my-infographic")


class TestInfographicNewView(InfographicFunctionalTestBase):

    def test_infographic_create_form_renders(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController', action='new'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_infographic_new_redirects_to_manage_datasets(self):
        '''Creating a new infographic redirects to the manage datasets form.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        # need a dataset for the 'bulk_action.infographic_add' button to show
        factories.Dataset()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController', action='new'),
            extra_environ=env,
        )

        # create infographic
        form = response.forms['dataset-edit']
        form['name'] = u'my-infographic'
        create_response = submit_and_follow(app, form, env, 'save')

        # Unique to manage_datasets page
        nosetools.assert_true('bulk_action.infographic_add' in create_response)
        # Requested page is the manage_datasets url.
        nosetools.assert_equal(url_for(controller='ckanext.infographic.controller:InfographicController',
                                       action='manage_datasets', id='my-infographic'), create_response.request.path)


class TestInfographicEditView(InfographicFunctionalTestBase):

    def test_infographic_edit_form_renders(self):
        '''
        Edit form renders in response for InfographicController edit action.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-infographic', type='infographic')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='edit',
                        id='my-infographic'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_infographic_edit_redirects_to_infographic_details(self):
        '''Editing a infographic redirects to the infographic details page.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-infographic', type='infographic')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='edit', id='my-infographic'),
            extra_environ=env,
        )

        # edit infographic
        form = response.forms['dataset-edit']
        form['name'] = u'my-changed-infographic'
        edit_response = submit_and_follow(app, form, env, 'save')

        # Requested page is the infographic read url.
        nosetools.assert_equal(url_for(controller='ckanext.infographic.controller:InfographicController',
                                       action='read', id='my-changed-infographic'), edit_response.request.path)


class TestDatasetView(InfographicFunctionalTestBase):

    '''Plugin adds a new infographics view for datasets.'''

    def test_dataset_read_has_infographics_tab(self):
        '''
        Dataset view page has a new Infographics tab linked to the correct place.
        '''
        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='package', action='read', id=dataset['id'])
        )
        # response contains link to dataset's infographic list
        nosetools.assert_true('/dataset/infographics/{0}'.format(dataset['name']) in response)

    def test_dataset_infographic_page_lists_infographics_no_associations(self):
        '''
        No infographics are listed if dataset has no infographic associations.
        '''

        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='dataset_infographic_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('ul.media-grid li.media-item')), 0)

    def test_dataset_infographic_page_lists_infographics_two_associations(self):
        '''
        Two infographics are listed for dataset with two infographic associations.
        '''

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        infographic_one = factories.Dataset(name='my-first-infographic', type='infographic')
        infographic_two = factories.Dataset(name='my-second-infographic', type='infographic')
        factories.Dataset(name='my-third-infographic', type='infographic')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=dataset['id'],
                            infographic_id=infographic_one['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=dataset['id'],
                            infographic_id=infographic_two['id'])

        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='dataset_infographic_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('li.media-item')), 2)
        nosetools.assert_true('my-first-infographic' in response)
        nosetools.assert_true('my-second-infographic' in response)
        nosetools.assert_true('my-third-infographic' not in response)

    def test_dataset_infographic_page_add_to_infographic_dropdown_list(self):
        '''
        Add to infographic dropdown only lists infographics that aren't already
        associated with dataset.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        infographic_one = factories.Dataset(name='my-first-infographic', type='infographic')
        infographic_two = factories.Dataset(name='my-second-infographic', type='infographic')
        infographic_three = factories.Dataset(name='my-third-infographic', type='infographic')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=dataset['id'],
                            infographic_id=infographic_one['id'])

        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='dataset_infographic_list', id=dataset['id']),
            extra_environ={'REMOTE_USER': str(sysadmin['name'])}
        )

        infographic_add_form = response.forms['infographic-add']
        infographic_added_options = [value for (value, _) in infographic_add_form['infographic_added'].options]
        nosetools.assert_true(infographic_one['id'] not in infographic_added_options)
        nosetools.assert_true(infographic_two['id'] in infographic_added_options)
        nosetools.assert_true(infographic_three['id'] in infographic_added_options)

    def test_dataset_infographic_page_add_to_infographic_dropdown_submit(self):
        '''
        Submitting 'Add to infographic' form with selected infographic value creates
        a sc/pkg association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        infographic_one = factories.Dataset(name='my-first-infographic', type='infographic')
        factories.Dataset(name='my-second-infographic', type='infographic')
        factories.Dataset(name='my-third-infographic', type='infographic')

        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 0)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}

        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='dataset_infographic_list', id=dataset['id']),
            extra_environ=env
        )

        form = response.forms['infographic-add']
        form['infographic_added'] = infographic_one['id']
        infographic_add_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(infographic_add_response.request.path, "/dataset/infographics/my-dataset")
        # an association is created
        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 1)

    def test_dataset_infographic_page_remove_infographic_button_submit(self):
        '''
        Submitting 'Remove' form with selected infographic value deletes a sc/pkg
        association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        infographic_one = factories.Dataset(name='my-first-infographic', type='infographic')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=dataset['id'],
                            infographic_id=infographic_one['id'])

        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 1)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='dataset_infographic_list', id=dataset['id']),
            extra_environ=env
        )

        # Submit the remove form.
        form = response.forms[1]
        nosetools.assert_equal(form['remove_infographic_id'].value, infographic_one['id'])
        infographic_remove_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(infographic_remove_response.request.path, "/dataset/infographics/my-dataset")
        # the association is deleted
        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 0)


class TestInfographicAdminManageView(InfographicFunctionalTestBase):

    '''Plugin adds a infographic admin management page to ckan-admin section.'''

    def test_ckan_admin_has_infographic_config_tab(self):
        '''
        ckan-admin index page has a infographic config tab.
        '''
        if not tk.check_ckan_version(min_version='2.4'):
            raise SkipTest('Infographic config tab only available for CKAN 2.4+')

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='admin', action='index'),
            extra_environ=env
        )
        # response contains link to dataset's infographic list
        nosetools.assert_true('/ckan-admin/infographic_admins' in response)

    def test_infographic_admin_manage_page_returns_correct_status(self):
        '''
        /ckan-admin/infographic_admins can be successfully accessed.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        app.get(url=url_for(controller='ckanext.infographic.controller:InfographicController',
                            action='manage_infographic_admins'),
                status=200, extra_environ=env)

    def test_infographic_admin_manage_page_lists_infographic_admins(self):
        '''
        Infographic admins are listed on the infographic admin page.
        '''
        app = self._get_test_app()
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_two['name'])

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.infographic.controller:InfographicController',
                                       action='manage_infographic_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('/user/{0}'.format(user_one['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_two['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_three['name']) not in response)

    def test_infographic_admin_manage_page_no_admins_message(self):
        '''
        Infographic admins page displays message if no infographic admins present.
        '''
        app = self._get_test_app()

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.infographic.controller:InfographicController',
                                       action='manage_infographic_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('There are currently no Infographic Admins' in response)


class TestSearch(helpers.FunctionalTestBase):

    def test_search_with_nonascii_filter_query(self):
        '''
        Searching with non-ASCII filter queries works.

        See https://github.com/ckan/ckanext-infographic/issues/34.
        '''
        app = self._get_test_app()
        tag = u'\xe4\xf6\xfc'
        dataset = factories.Dataset(tags=[{'name': tag, 'state': 'active'}])
        result = helpers.call_action('package_search', fq='tags:' + tag)
        nosetools.assert_equals(result['count'], 1)


class TestCKEditor(helpers.FunctionalTestBase):

    @helpers.change_config('ckanext.infographic.editor', 'ckeditor')
    def test_rich_text_editor_is_shown_when_configured(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-infographic', type='infographic')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='edit',
                        id='my-infographic'),
            extra_environ=env,
        )
        nosetools.assert_in('<textarea id="editor"', response.ubody)


    def test_rich_text_editor_is_not_shown_when_not_configured(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-infographic', type='infographic')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='edit',
                        id='my-infographic'),
            extra_environ=env,
        )
        nosetools.assert_not_in('<textarea id="editor"', response.ubody)

    @helpers.change_config('ckanext.infographic.editor', 'ckeditor')
    def test_custom_div_content_is_used_with_ckeditor(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-infographic', type='infographic')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.infographic.controller:InfographicController',
                        action='read',
                        id='my-infographic'),
            extra_environ=env,
        )
        nosetools.assert_in('<div class="ck-content">', response.ubody)