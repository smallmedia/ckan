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

from ckanext.datagathering.model import DatagatheringPackageAssociation
from ckanext.datagathering.tests import DatagatheringFunctionalTestBase

import logging
log = logging.getLogger(__name__)

submit_and_follow = helpers.submit_and_follow


class TestDatagatheringIndex(DatagatheringFunctionalTestBase):

    def test_datagatherings_redirects_to_datagathering(self):
        '''/datagatherings redirects to /datagathering.'''
        app = self._get_test_app()
        response = app.get('/datagatherings', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/datagathering')

    def test_datagatherings_redirects_to_datagathering_for_item(self):
        '''/datagatherings/ redirects to /datagathering.'''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get('/datagatherings/my-datagathering', status=302)
        nosetools.assert_equal(response.location, 'http://localhost/datagathering/my-datagathering')

    def test_datagathering_listed_on_index(self):
        '''
        An added Datagathering will appear on the Datagathering index page.
        '''
        app = self._get_test_app()

        factories.Dataset(type='datagathering', name='my-datagathering')

        response = app.get("/datagathering", status=200)
        response.mustcontain("1 datagathering found")
        response.mustcontain("my-datagathering")


class TestDatagatheringNewView(DatagatheringFunctionalTestBase):

    def test_datagathering_create_form_renders(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController', action='new'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_datagathering_new_redirects_to_manage_datasets(self):
        '''Creating a new datagathering redirects to the manage datasets form.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        # need a dataset for the 'bulk_action.datagathering_add' button to show
        factories.Dataset()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController', action='new'),
            extra_environ=env,
        )

        # create datagathering
        form = response.forms['dataset-edit']
        form['name'] = u'my-datagathering'
        create_response = submit_and_follow(app, form, env, 'save')

        # Unique to manage_datasets page
        nosetools.assert_true('bulk_action.datagathering_add' in create_response)
        # Requested page is the manage_datasets url.
        nosetools.assert_equal(url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                                       action='manage_datasets', id='my-datagathering'), create_response.request.path)


class TestDatagatheringEditView(DatagatheringFunctionalTestBase):

    def test_datagathering_edit_form_renders(self):
        '''
        Edit form renders in response for DatagatheringController edit action.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-datagathering', type='datagathering')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='edit',
                        id='my-datagathering'),
            extra_environ=env,
        )
        nosetools.assert_true('dataset-edit' in response.forms)

    def test_datagathering_edit_redirects_to_datagathering_details(self):
        '''Editing a datagathering redirects to the datagathering details page.'''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-datagathering', type='datagathering')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='edit', id='my-datagathering'),
            extra_environ=env,
        )

        # edit datagathering
        form = response.forms['dataset-edit']
        form['name'] = u'my-changed-datagathering'
        edit_response = submit_and_follow(app, form, env, 'save')

        # Requested page is the datagathering read url.
        nosetools.assert_equal(url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                                       action='read', id='my-changed-datagathering'), edit_response.request.path)


class TestDatasetView(DatagatheringFunctionalTestBase):

    '''Plugin adds a new datagatherings view for datasets.'''

    def test_dataset_read_has_datagatherings_tab(self):
        '''
        Dataset view page has a new Datagatherings tab linked to the correct place.
        '''
        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='package', action='read', id=dataset['id'])
        )
        # response contains link to dataset's datagathering list
        nosetools.assert_true('/dataset/datagatherings/{0}'.format(dataset['name']) in response)

    def test_dataset_datagathering_page_lists_datagatherings_no_associations(self):
        '''
        No datagatherings are listed if dataset has no datagathering associations.
        '''

        app = self._get_test_app()
        dataset = factories.Dataset(name='my-dataset')

        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='dataset_datagathering_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('ul.media-grid li.media-item')), 0)

    def test_dataset_datagathering_page_lists_datagatherings_two_associations(self):
        '''
        Two datagatherings are listed for dataset with two datagathering associations.
        '''

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        datagathering_one = factories.Dataset(name='my-first-datagathering', type='datagathering')
        datagathering_two = factories.Dataset(name='my-second-datagathering', type='datagathering')
        factories.Dataset(name='my-third-datagathering', type='datagathering')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=dataset['id'],
                            datagathering_id=datagathering_one['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=dataset['id'],
                            datagathering_id=datagathering_two['id'])

        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='dataset_datagathering_list', id=dataset['id'])
        )

        nosetools.assert_equal(len(response.html.select('li.media-item')), 2)
        nosetools.assert_true('my-first-datagathering' in response)
        nosetools.assert_true('my-second-datagathering' in response)
        nosetools.assert_true('my-third-datagathering' not in response)

    def test_dataset_datagathering_page_add_to_datagathering_dropdown_list(self):
        '''
        Add to datagathering dropdown only lists datagatherings that aren't already
        associated with dataset.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        datagathering_one = factories.Dataset(name='my-first-datagathering', type='datagathering')
        datagathering_two = factories.Dataset(name='my-second-datagathering', type='datagathering')
        datagathering_three = factories.Dataset(name='my-third-datagathering', type='datagathering')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=dataset['id'],
                            datagathering_id=datagathering_one['id'])

        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='dataset_datagathering_list', id=dataset['id']),
            extra_environ={'REMOTE_USER': str(sysadmin['name'])}
        )

        datagathering_add_form = response.forms['datagathering-add']
        datagathering_added_options = [value for (value, _) in datagathering_add_form['datagathering_added'].options]
        nosetools.assert_true(datagathering_one['id'] not in datagathering_added_options)
        nosetools.assert_true(datagathering_two['id'] in datagathering_added_options)
        nosetools.assert_true(datagathering_three['id'] in datagathering_added_options)

    def test_dataset_datagathering_page_add_to_datagathering_dropdown_submit(self):
        '''
        Submitting 'Add to datagathering' form with selected datagathering value creates
        a sc/pkg association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        datagathering_one = factories.Dataset(name='my-first-datagathering', type='datagathering')
        factories.Dataset(name='my-second-datagathering', type='datagathering')
        factories.Dataset(name='my-third-datagathering', type='datagathering')

        nosetools.assert_equal(model.Session.query(DatagatheringPackageAssociation).count(), 0)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}

        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='dataset_datagathering_list', id=dataset['id']),
            extra_environ=env
        )

        form = response.forms['datagathering-add']
        form['datagathering_added'] = datagathering_one['id']
        datagathering_add_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(datagathering_add_response.request.path, "/dataset/datagatherings/my-dataset")
        # an association is created
        nosetools.assert_equal(model.Session.query(DatagatheringPackageAssociation).count(), 1)

    def test_dataset_datagathering_page_remove_datagathering_button_submit(self):
        '''
        Submitting 'Remove' form with selected datagathering value deletes a sc/pkg
        association.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        dataset = factories.Dataset(name='my-dataset')
        datagathering_one = factories.Dataset(name='my-first-datagathering', type='datagathering')

        context = {'user': sysadmin['name']}
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=dataset['id'],
                            datagathering_id=datagathering_one['id'])

        nosetools.assert_equal(model.Session.query(DatagatheringPackageAssociation).count(), 1)

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='dataset_datagathering_list', id=dataset['id']),
            extra_environ=env
        )

        # Submit the remove form.
        form = response.forms[1]
        nosetools.assert_equal(form['remove_datagathering_id'].value, datagathering_one['id'])
        datagathering_remove_response = submit_and_follow(app, form, env)

        # returns to the correct page
        nosetools.assert_equal(datagathering_remove_response.request.path, "/dataset/datagatherings/my-dataset")
        # the association is deleted
        nosetools.assert_equal(model.Session.query(DatagatheringPackageAssociation).count(), 0)


class TestDatagatheringAdminManageView(DatagatheringFunctionalTestBase):

    '''Plugin adds a datagathering admin management page to ckan-admin section.'''

    def test_ckan_admin_has_datagathering_config_tab(self):
        '''
        ckan-admin index page has a datagathering config tab.
        '''
        if not tk.check_ckan_version(min_version='2.4'):
            raise SkipTest('Datagathering config tab only available for CKAN 2.4+')

        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='admin', action='index'),
            extra_environ=env
        )
        # response contains link to dataset's datagathering list
        nosetools.assert_true('/ckan-admin/datagathering_admins' in response)

    def test_datagathering_admin_manage_page_returns_correct_status(self):
        '''
        /ckan-admin/datagathering_admins can be successfully accessed.
        '''
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        app.get(url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                            action='manage_datagathering_admins'),
                status=200, extra_environ=env)

    def test_datagathering_admin_manage_page_lists_datagathering_admins(self):
        '''
        Datagathering admins are listed on the datagathering admin page.
        '''
        app = self._get_test_app()
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_two['name'])

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                                       action='manage_datagathering_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('/user/{0}'.format(user_one['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_two['name']) in response)
        nosetools.assert_true('/user/{0}'.format(user_three['name']) not in response)

    def test_datagathering_admin_manage_page_no_admins_message(self):
        '''
        Datagathering admins page displays message if no datagathering admins present.
        '''
        app = self._get_test_app()

        sysadmin = factories.Sysadmin()

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                                       action='manage_datagathering_admins'),
                           status=200, extra_environ=env)

        nosetools.assert_true('There are currently no Datagathering Admins' in response)


class TestSearch(helpers.FunctionalTestBase):

    def test_search_with_nonascii_filter_query(self):
        '''
        Searching with non-ASCII filter queries works.

        See https://github.com/ckan/ckanext-datagathering/issues/34.
        '''
        app = self._get_test_app()
        tag = u'\xe4\xf6\xfc'
        dataset = factories.Dataset(tags=[{'name': tag, 'state': 'active'}])
        result = helpers.call_action('package_search', fq='tags:' + tag)
        nosetools.assert_equals(result['count'], 1)


class TestCKEditor(helpers.FunctionalTestBase):

    @helpers.change_config('ckanext.datagathering.editor', 'ckeditor')
    def test_rich_text_editor_is_shown_when_configured(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-datagathering', type='datagathering')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='edit',
                        id='my-datagathering'),
            extra_environ=env,
        )
        nosetools.assert_in('<textarea id="editor"', response.ubody)


    def test_rich_text_editor_is_not_shown_when_not_configured(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-datagathering', type='datagathering')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='edit',
                        id='my-datagathering'),
            extra_environ=env,
        )
        nosetools.assert_not_in('<textarea id="editor"', response.ubody)

    @helpers.change_config('ckanext.datagathering.editor', 'ckeditor')
    def test_custom_div_content_is_used_with_ckeditor(self):
        app = self._get_test_app()
        sysadmin = factories.Sysadmin()
        factories.Dataset(name='my-datagathering', type='datagathering')

        env = {'REMOTE_USER': sysadmin['name'].encode('ascii')}
        response = app.get(
            url=url_for(controller='ckanext.datagathering.controller:DatagatheringController',
                        action='read',
                        id='my-datagathering'),
            extra_environ=env,
        )
        nosetools.assert_in('<div class="ck-content">', response.ubody)