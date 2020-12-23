from nose import tools as nosetools
from nose import SkipTest

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


class TestInfographicShow(InfographicFunctionalTestBase):

    def test_infographic_show_no_args(self):
        '''
        Calling infographic show with no args raises a ValidationError.
        '''
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_show')

    def test_infographic_show_with_id(self):
        '''
        Calling infographic show with id arg returns infographic dict.
        '''
        my_infographic = factories.Dataset(type='infographic', name='my-infographic')

        infographic_shown = helpers.call_action('ckanext_infographic_show', id=my_infographic['id'])

        nosetools.assert_equal(my_infographic['name'], infographic_shown['name'])

    def test_infographic_show_with_name(self):
        '''
        Calling infographic show with name arg returns infographic dict.
        '''
        my_infographic = factories.Dataset(type='infographic', name='my-infographic')

        infographic_shown = helpers.call_action('ckanext_infographic_show', id=my_infographic['name'])

        nosetools.assert_equal(my_infographic['id'], infographic_shown['id'])

    def test_infographic_show_with_nonexisting_name(self):
        '''
        Calling infographic show with bad name arg returns ObjectNotFound.
        '''
        factories.Dataset(type='infographic', name='my-infographic')

        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                                'ckanext_infographic_show', id='my-bad-name')

    def test_infographic_show_num_datasets_added(self):
        '''
        num_datasets property returned with infographic dict.
        '''
        my_infographic = factories.Dataset(type='infographic', name='my-infographic')

        infographic_shown = helpers.call_action('ckanext_infographic_show', id=my_infographic['name'])

        nosetools.assert_true('num_datasets' in infographic_shown)
        nosetools.assert_equal(infographic_shown['num_datasets'], 0)

    def test_infographic_show_num_datasets_correct_value(self):
        '''
        num_datasets property has correct value.
        '''

        sysadmin = factories.User(sysadmin=True)

        my_infographic = factories.Dataset(type='infographic', name='my-infographic')
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_one['id'],
                            infographic_id=my_infographic['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_two['id'],
                            infographic_id=my_infographic['id'])

        infographic_shown = helpers.call_action('ckanext_infographic_show', id=my_infographic['name'])

        nosetools.assert_equal(infographic_shown['num_datasets'], 2)

    def test_infographic_show_num_datasets_correct_only_count_active_datasets(self):
        '''
        num_datasets property has correct value when some previously
        associated datasets have been datasets.
        '''
        sysadmin = factories.User(sysadmin=True)

        my_infographic = factories.Dataset(type='infographic', name='my-infographic')
        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()

        context = {'user': sysadmin['name']}
        # create the associations
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_one['id'],
                            infographic_id=my_infographic['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_two['id'],
                            infographic_id=my_infographic['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_three['id'],
                            infographic_id=my_infographic['id'])

        # delete the first package
        helpers.call_action('package_delete', context=context, id=package_one['id'])

        infographic_shown = helpers.call_action('ckanext_infographic_show', id=my_infographic['name'])

        # the num_datasets should only include active datasets
        nosetools.assert_equal(infographic_shown['num_datasets'], 2)

    def test_infographic_anon_user_can_see_package_list_when_infographic_association_was_deleted(self):
        '''
        When a infographic is deleted, the remaining associations with formerly associated
        packages or infographics can still be displayed.
        '''
        app = self._get_test_app()

        sysadmin = factories.User(sysadmin=True)

        infographic_one = factories.Dataset(type='infographic', name='infographic-one')
        infographic_two = factories.Dataset(type='infographic', name='infographic-two')
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        admin_context = {'user': sysadmin['name']}

        # create the associations
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=admin_context, package_id=package_one['id'],
                            infographic_id=infographic_one['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=admin_context, package_id=package_one['id'],
                            infographic_id=infographic_two['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=admin_context, package_id=package_two['id'],
                            infographic_id=infographic_one['id'])
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=admin_context, package_id=package_two['id'],
                            infographic_id=infographic_two['id'])

        # delete one of the associated infographics
        helpers.call_action('package_delete', context=admin_context,
                            id=infographic_two['id'])

        # the anon user can still see the associated packages of remaining infographic
        associated_packages = helpers.call_action(
            'ckanext_infographic_package_list',
            infographic_id=infographic_one['id'])

        nosetools.assert_equal(len(associated_packages), 2)

        # overview of packages can still be seen
        app.get("/dataset", status=200)


class TestInfographicList(InfographicFunctionalTestBase):

    def test_infographic_list(self):
        '''Infographic list action returns names of infographics in site.'''

        infographic_one = factories.Dataset(type='infographic')
        infographic_two = factories.Dataset(type='infographic')
        infographic_three = factories.Dataset(type='infographic')

        infographic_list = helpers.call_action('ckanext_infographic_list')

        infographic_list_name_id = [(sc['name'], sc['id']) for sc in infographic_list]

        nosetools.assert_equal(len(infographic_list), 3)
        nosetools.assert_true(sorted(infographic_list_name_id) ==
                              sorted([(infographic['name'], infographic['id'])
                                     for infographic in [infographic_one,
                                                      infographic_two,
                                                      infographic_three]]))

    def test_infographic_list_no_datasets(self):
        '''
        Infographic list action doesn't return normal datasets (of type
        'dataset').
        '''
        infographic_one = factories.Dataset(type='infographic')
        dataset_one = factories.Dataset()
        dataset_two = factories.Dataset()

        infographic_list = helpers.call_action('ckanext_infographic_list')

        infographic_list_name_id = [(sc['name'], sc['id']) for sc in infographic_list]

        nosetools.assert_equal(len(infographic_list), 1)
        nosetools.assert_true((infographic_one['name'], infographic_one['id']) in infographic_list_name_id)
        nosetools.assert_true((dataset_one['name'], dataset_one['id']) not in infographic_list_name_id)
        nosetools.assert_true((dataset_two['name'], dataset_two['id']) not in infographic_list_name_id)


class TestInfographicPackageList(InfographicFunctionalTestBase):

    '''Tests for ckanext_infographic_package_list'''

    def test_infographic_package_list_no_packages(self):
        '''
        Calling ckanext_infographic_package_list with a infographic that has no
        packages returns an empty list.
        '''
        infographic_id = factories.Dataset(type='infographic')['id']

        pkg_list = helpers.call_action('ckanext_infographic_package_list',
                                       infographic_id=infographic_id)

        nosetools.assert_equal(pkg_list, [])

    def test_infographic_package_list_works_with_name(self):
        '''
        Calling ckanext_infographic_package_list with a infographic name doesn't
        raise a ValidationError.
        '''
        infographic_name = factories.Dataset(type='infographic')['name']

        pkg_list = helpers.call_action('ckanext_infographic_package_list',
                                       infographic_id=infographic_name)

        nosetools.assert_equal(pkg_list, [])

    def test_infographic_package_list_wrong_infographic_id(self):
        '''
        Calling ckanext_infographic_package_list with a bad infographic id raises a
        ValidationError.
        '''
        factories.Dataset(type='infographic')['id']

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_package_list',
                                infographic_id='a-bad-id')

    def test_infographic_package_list_infographic_has_package(self):
        '''
        Calling ckanext_infographic_package_list with a infographic that has a
        package should return that package.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        infographic_id = factories.Dataset(type='infographic')['id']
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic_id)

        pkg_list = helpers.call_action('ckanext_infographic_package_list',
                                       infographic_id=infographic_id)

        # We've got an item in the pkg_list
        nosetools.assert_equal(len(pkg_list), 1)
        # The list item should have the correct name property
        nosetools.assert_equal(pkg_list[0]['name'], package['name'])

    def test_infographic_package_list_infographic_has_two_packages(self):
        '''
        Calling ckanext_infographic_package_list with a infographic that has two
        packages should return the packages.
        '''
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        infographic_id = factories.Dataset(type='infographic')['id']
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_one['id'],
                            infographic_id=infographic_id)
        # create second association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_two['id'],
                            infographic_id=infographic_id)

        pkg_list = helpers.call_action('ckanext_infographic_package_list',
                                       infographic_id=infographic_id)

        # We've got two items in the pkg_list
        nosetools.assert_equal(len(pkg_list), 2)

    def test_infographic_package_list_infographic_only_contains_active_datasets(self):
        '''
        Calling ckanext_infographic_package_list will only return active datasets
        (not deleted ones).
        '''
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()
        infographic_id = factories.Dataset(type='infographic')['id']
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_one['id'],
                            infographic_id=infographic_id)
        # create second association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_two['id'],
                            infographic_id=infographic_id)
        # create third association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_three['id'],
                            infographic_id=infographic_id)

        # delete the first package
        helpers.call_action('package_delete', context=context, id=package_one['id'])

        pkg_list = helpers.call_action('ckanext_infographic_package_list',
                                       infographic_id=infographic_id)

        # We've got two items in the pkg_list
        nosetools.assert_equal(len(pkg_list), 2)

        pkg_list_ids = [pkg['id'] for pkg in pkg_list]
        nosetools.assert_true(package_two['id'] in pkg_list_ids)
        nosetools.assert_true(package_three['id'] in pkg_list_ids)
        nosetools.assert_false(package_one['id'] in pkg_list_ids)

    def test_infographic_package_list_package_isnot_a_infographic(self):
        '''
        Calling ckanext_infographic_package_list with a package id should raise a
        ValidationError.

        Since Infographics are Packages under the hood, make sure we treat them
        differently.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        infographic_id = factories.Dataset(type='infographic')['id']
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic_id)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_package_list',
                                infographic_id=package['id'])


class TestPackageInfographicList(InfographicFunctionalTestBase):

    '''Tests for ckanext_package_infographic_list'''

    def test_package_infographic_list_no_infographics(self):
        '''
        Calling ckanext_package_infographic_list with a package that has no
        infographics returns an empty list.
        '''
        package_id = factories.Dataset()['id']

        infographic_list = helpers.call_action('ckanext_package_infographic_list',
                                            package_id=package_id)

        nosetools.assert_equal(infographic_list, [])

    def test_package_infographic_list_works_with_name(self):
        '''
        Calling ckanext_package_infographic_list with a package name doesn't
        raise a ValidationError.
        '''
        package_name = factories.Dataset()['name']

        infographic_list = helpers.call_action('ckanext_package_infographic_list',
                                            package_id=package_name)

        nosetools.assert_equal(infographic_list, [])

    def test_package_infographic_list_wrong_infographic_id(self):
        '''
        Calling ckanext_package_infographic_list with a bad package id raises a
        ValidationError.
        '''
        factories.Dataset()['id']

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_package_infographic_list',
                                infographic_id='a-bad-id')

    def test_package_infographic_list_infographic_has_package(self):
        '''
        Calling ckanext_package_infographic_list with a package that has a
        infographic should return that infographic.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        infographic = factories.Dataset(type='infographic')
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic['id'])

        infographic_list = helpers.call_action('ckanext_package_infographic_list',
                                            package_id=package['id'])

        # We've got an item in the infographic_list
        nosetools.assert_equal(len(infographic_list), 1)
        # The list item should have the correct name property
        nosetools.assert_equal(infographic_list[0]['name'], infographic['name'])

    def test_package_infographic_list_infographic_has_two_packages(self):
        '''
        Calling ckanext_package_infographic_list with a package that has two
        infographics should return the infographics.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        infographic_one = factories.Dataset(type='infographic')
        infographic_two = factories.Dataset(type='infographic')
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic_one['id'])
        # create second association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic_two['id'])

        infographic_list = helpers.call_action('ckanext_package_infographic_list',
                                            package_id=package['id'])

        # We've got two items in the infographic_list
        nosetools.assert_equal(len(infographic_list), 2)

    def test_package_infographic_list_package_isnot_a_infographic(self):
        '''
        Calling ckanext_package_infographic_list with a infographic id should raise a
        ValidationError.

        Since Infographics are Packages under the hood, make sure we treat them
        differently.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        infographic = factories.Dataset(type='infographic')
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package['id'],
                            infographic_id=infographic['id'])

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_package_infographic_list',
                                package_id=infographic['id'])


class TestInfographicAdminList(InfographicFunctionalTestBase):

    '''Tests for ckanext_infographic_admin_list'''

    def test_infographic_admin_list_no_infographic_admins(self):
        '''
        Calling ckanext_infographic_admin_list on a site that has no infographics
        admins returns an empty list.
        '''

        infographic_admin_list = helpers.call_action('ckanext_infographic_admin_list')

        nosetools.assert_equal(infographic_admin_list, [])

    def test_infographic_admin_list_users(self):
        '''
        Calling ckanext_infographic_admin_list will return users who are infographic
        admins.
        '''
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_two['name'])
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_three['name'])

        infographic_admin_list = helpers.call_action('ckanext_infographic_admin_list', context={})

        nosetools.assert_equal(len(infographic_admin_list), 3)
        for user in [user_one, user_two, user_three]:
            nosetools.assert_true({'name': user['name'], 'id': user['id']} in infographic_admin_list)

    def test_infographic_admin_only_lists_admin_users(self):
        '''
        Calling ckanext_infographic_admin_list will only return users who are
        infographic admins.
        '''
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_two['name'])

        infographic_admin_list = helpers.call_action('ckanext_infographic_admin_list', context={})

        nosetools.assert_equal(len(infographic_admin_list), 2)
        # user three isn't in list
        nosetools.assert_true({'name': user_three['name'], 'id': user_three['id']} not in infographic_admin_list)


class TestPackageSearchBeforeSearch(InfographicFunctionalTestBase):

    '''
    Extension uses the `before_search` method to alter search parameters.
    '''

    def test_package_search_no_additional_filters(self):
        '''
        Perform package_search with no additional filters should not include
        infographics.
        '''
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type='infographic')
        factories.Dataset(type='custom')

        search_results = helpers.call_action('package_search', context={})['results']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 3)
        nosetools.assert_true('infographic' not in types)
        nosetools.assert_true('custom' in types)

    def test_package_search_filter_include_infographic(self):
        '''
        package_search filtered to include datasets of type infographic should
        only include infographics.
        '''
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type='infographic')
        factories.Dataset(type='custom')

        search_results = helpers.call_action('package_search', context={},
                                             fq='dataset_type:infographic')['results']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 1)
        nosetools.assert_true('infographic' in types)
        nosetools.assert_true('custom' not in types)
        nosetools.assert_true('dataset' not in types)


class TestUserShowBeforeSearch(InfographicFunctionalTestBase):

    '''
    Extension uses the `before_search` method to alter results of user_show
    (via package_search).
    '''

    def test_user_show_no_additional_filters(self):
        '''
        Perform package_search with no additional filters should not include
        infographics.
        '''
        if not toolkit.check_ckan_version(min_version='2.4'):
            raise SkipTest('Filtering out infographics requires CKAN 2.4+ (ckan/ckan/issues/2380)')

        user = factories.User()
        factories.Dataset(user=user)
        factories.Dataset(user=user)
        factories.Dataset(user=user, type='infographic')
        factories.Dataset(user=user, type='custom')

        search_results = helpers.call_action('user_show', context={},
                                             include_datasets=True,
                                             id=user['name'])['datasets']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 3)
        nosetools.assert_true('infographic' not in types)
        nosetools.assert_true('custom' in types)
