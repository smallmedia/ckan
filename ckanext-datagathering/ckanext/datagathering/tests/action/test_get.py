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

from ckanext.datagathering.tests import DatagatheringFunctionalTestBase


class TestDatagatheringShow(DatagatheringFunctionalTestBase):

    def test_datagathering_show_no_args(self):
        '''
        Calling datagathering show with no args raises a ValidationError.
        '''
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_datagathering_show')

    def test_datagathering_show_with_id(self):
        '''
        Calling datagathering show with id arg returns datagathering dict.
        '''
        my_datagathering = factories.Dataset(type='datagathering', name='my-datagathering')

        datagathering_shown = helpers.call_action('ckanext_datagathering_show', id=my_datagathering['id'])

        nosetools.assert_equal(my_datagathering['name'], datagathering_shown['name'])

    def test_datagathering_show_with_name(self):
        '''
        Calling datagathering show with name arg returns datagathering dict.
        '''
        my_datagathering = factories.Dataset(type='datagathering', name='my-datagathering')

        datagathering_shown = helpers.call_action('ckanext_datagathering_show', id=my_datagathering['name'])

        nosetools.assert_equal(my_datagathering['id'], datagathering_shown['id'])

    def test_datagathering_show_with_nonexisting_name(self):
        '''
        Calling datagathering show with bad name arg returns ObjectNotFound.
        '''
        factories.Dataset(type='datagathering', name='my-datagathering')

        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                                'ckanext_datagathering_show', id='my-bad-name')

    def test_datagathering_show_num_datasets_added(self):
        '''
        num_datasets property returned with datagathering dict.
        '''
        my_datagathering = factories.Dataset(type='datagathering', name='my-datagathering')

        datagathering_shown = helpers.call_action('ckanext_datagathering_show', id=my_datagathering['name'])

        nosetools.assert_true('num_datasets' in datagathering_shown)
        nosetools.assert_equal(datagathering_shown['num_datasets'], 0)

    def test_datagathering_show_num_datasets_correct_value(self):
        '''
        num_datasets property has correct value.
        '''

        sysadmin = factories.User(sysadmin=True)

        my_datagathering = factories.Dataset(type='datagathering', name='my-datagathering')
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_one['id'],
                            datagathering_id=my_datagathering['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_two['id'],
                            datagathering_id=my_datagathering['id'])

        datagathering_shown = helpers.call_action('ckanext_datagathering_show', id=my_datagathering['name'])

        nosetools.assert_equal(datagathering_shown['num_datasets'], 2)

    def test_datagathering_show_num_datasets_correct_only_count_active_datasets(self):
        '''
        num_datasets property has correct value when some previously
        associated datasets have been datasets.
        '''
        sysadmin = factories.User(sysadmin=True)

        my_datagathering = factories.Dataset(type='datagathering', name='my-datagathering')
        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()

        context = {'user': sysadmin['name']}
        # create the associations
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_one['id'],
                            datagathering_id=my_datagathering['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_two['id'],
                            datagathering_id=my_datagathering['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_three['id'],
                            datagathering_id=my_datagathering['id'])

        # delete the first package
        helpers.call_action('package_delete', context=context, id=package_one['id'])

        datagathering_shown = helpers.call_action('ckanext_datagathering_show', id=my_datagathering['name'])

        # the num_datasets should only include active datasets
        nosetools.assert_equal(datagathering_shown['num_datasets'], 2)

    def test_datagathering_anon_user_can_see_package_list_when_datagathering_association_was_deleted(self):
        '''
        When a datagathering is deleted, the remaining associations with formerly associated
        packages or datagatherings can still be displayed.
        '''
        app = self._get_test_app()

        sysadmin = factories.User(sysadmin=True)

        datagathering_one = factories.Dataset(type='datagathering', name='datagathering-one')
        datagathering_two = factories.Dataset(type='datagathering', name='datagathering-two')
        package_one = factories.Dataset()
        package_two = factories.Dataset()

        admin_context = {'user': sysadmin['name']}

        # create the associations
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=admin_context, package_id=package_one['id'],
                            datagathering_id=datagathering_one['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=admin_context, package_id=package_one['id'],
                            datagathering_id=datagathering_two['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=admin_context, package_id=package_two['id'],
                            datagathering_id=datagathering_one['id'])
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=admin_context, package_id=package_two['id'],
                            datagathering_id=datagathering_two['id'])

        # delete one of the associated datagatherings
        helpers.call_action('package_delete', context=admin_context,
                            id=datagathering_two['id'])

        # the anon user can still see the associated packages of remaining datagathering
        associated_packages = helpers.call_action(
            'ckanext_datagathering_package_list',
            datagathering_id=datagathering_one['id'])

        nosetools.assert_equal(len(associated_packages), 2)

        # overview of packages can still be seen
        app.get("/dataset", status=200)


class TestDatagatheringList(DatagatheringFunctionalTestBase):

    def test_datagathering_list(self):
        '''Datagathering list action returns names of datagatherings in site.'''

        datagathering_one = factories.Dataset(type='datagathering')
        datagathering_two = factories.Dataset(type='datagathering')
        datagathering_three = factories.Dataset(type='datagathering')

        datagathering_list = helpers.call_action('ckanext_datagathering_list')

        datagathering_list_name_id = [(sc['name'], sc['id']) for sc in datagathering_list]

        nosetools.assert_equal(len(datagathering_list), 3)
        nosetools.assert_true(sorted(datagathering_list_name_id) ==
                              sorted([(datagathering['name'], datagathering['id'])
                                     for datagathering in [datagathering_one,
                                                      datagathering_two,
                                                      datagathering_three]]))

    def test_datagathering_list_no_datasets(self):
        '''
        Datagathering list action doesn't return normal datasets (of type
        'dataset').
        '''
        datagathering_one = factories.Dataset(type='datagathering')
        dataset_one = factories.Dataset()
        dataset_two = factories.Dataset()

        datagathering_list = helpers.call_action('ckanext_datagathering_list')

        datagathering_list_name_id = [(sc['name'], sc['id']) for sc in datagathering_list]

        nosetools.assert_equal(len(datagathering_list), 1)
        nosetools.assert_true((datagathering_one['name'], datagathering_one['id']) in datagathering_list_name_id)
        nosetools.assert_true((dataset_one['name'], dataset_one['id']) not in datagathering_list_name_id)
        nosetools.assert_true((dataset_two['name'], dataset_two['id']) not in datagathering_list_name_id)


class TestDatagatheringPackageList(DatagatheringFunctionalTestBase):

    '''Tests for ckanext_datagathering_package_list'''

    def test_datagathering_package_list_no_packages(self):
        '''
        Calling ckanext_datagathering_package_list with a datagathering that has no
        packages returns an empty list.
        '''
        datagathering_id = factories.Dataset(type='datagathering')['id']

        pkg_list = helpers.call_action('ckanext_datagathering_package_list',
                                       datagathering_id=datagathering_id)

        nosetools.assert_equal(pkg_list, [])

    def test_datagathering_package_list_works_with_name(self):
        '''
        Calling ckanext_datagathering_package_list with a datagathering name doesn't
        raise a ValidationError.
        '''
        datagathering_name = factories.Dataset(type='datagathering')['name']

        pkg_list = helpers.call_action('ckanext_datagathering_package_list',
                                       datagathering_id=datagathering_name)

        nosetools.assert_equal(pkg_list, [])

    def test_datagathering_package_list_wrong_datagathering_id(self):
        '''
        Calling ckanext_datagathering_package_list with a bad datagathering id raises a
        ValidationError.
        '''
        factories.Dataset(type='datagathering')['id']

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_datagathering_package_list',
                                datagathering_id='a-bad-id')

    def test_datagathering_package_list_datagathering_has_package(self):
        '''
        Calling ckanext_datagathering_package_list with a datagathering that has a
        package should return that package.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        datagathering_id = factories.Dataset(type='datagathering')['id']
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering_id)

        pkg_list = helpers.call_action('ckanext_datagathering_package_list',
                                       datagathering_id=datagathering_id)

        # We've got an item in the pkg_list
        nosetools.assert_equal(len(pkg_list), 1)
        # The list item should have the correct name property
        nosetools.assert_equal(pkg_list[0]['name'], package['name'])

    def test_datagathering_package_list_datagathering_has_two_packages(self):
        '''
        Calling ckanext_datagathering_package_list with a datagathering that has two
        packages should return the packages.
        '''
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        datagathering_id = factories.Dataset(type='datagathering')['id']
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_one['id'],
                            datagathering_id=datagathering_id)
        # create second association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_two['id'],
                            datagathering_id=datagathering_id)

        pkg_list = helpers.call_action('ckanext_datagathering_package_list',
                                       datagathering_id=datagathering_id)

        # We've got two items in the pkg_list
        nosetools.assert_equal(len(pkg_list), 2)

    def test_datagathering_package_list_datagathering_only_contains_active_datasets(self):
        '''
        Calling ckanext_datagathering_package_list will only return active datasets
        (not deleted ones).
        '''
        sysadmin = factories.User(sysadmin=True)

        package_one = factories.Dataset()
        package_two = factories.Dataset()
        package_three = factories.Dataset()
        datagathering_id = factories.Dataset(type='datagathering')['id']
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_one['id'],
                            datagathering_id=datagathering_id)
        # create second association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_two['id'],
                            datagathering_id=datagathering_id)
        # create third association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package_three['id'],
                            datagathering_id=datagathering_id)

        # delete the first package
        helpers.call_action('package_delete', context=context, id=package_one['id'])

        pkg_list = helpers.call_action('ckanext_datagathering_package_list',
                                       datagathering_id=datagathering_id)

        # We've got two items in the pkg_list
        nosetools.assert_equal(len(pkg_list), 2)

        pkg_list_ids = [pkg['id'] for pkg in pkg_list]
        nosetools.assert_true(package_two['id'] in pkg_list_ids)
        nosetools.assert_true(package_three['id'] in pkg_list_ids)
        nosetools.assert_false(package_one['id'] in pkg_list_ids)

    def test_datagathering_package_list_package_isnot_a_datagathering(self):
        '''
        Calling ckanext_datagathering_package_list with a package id should raise a
        ValidationError.

        Since Datagatherings are Packages under the hood, make sure we treat them
        differently.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        datagathering_id = factories.Dataset(type='datagathering')['id']
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering_id)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_datagathering_package_list',
                                datagathering_id=package['id'])


class TestPackageDatagatheringList(DatagatheringFunctionalTestBase):

    '''Tests for ckanext_package_datagathering_list'''

    def test_package_datagathering_list_no_datagatherings(self):
        '''
        Calling ckanext_package_datagathering_list with a package that has no
        datagatherings returns an empty list.
        '''
        package_id = factories.Dataset()['id']

        datagathering_list = helpers.call_action('ckanext_package_datagathering_list',
                                            package_id=package_id)

        nosetools.assert_equal(datagathering_list, [])

    def test_package_datagathering_list_works_with_name(self):
        '''
        Calling ckanext_package_datagathering_list with a package name doesn't
        raise a ValidationError.
        '''
        package_name = factories.Dataset()['name']

        datagathering_list = helpers.call_action('ckanext_package_datagathering_list',
                                            package_id=package_name)

        nosetools.assert_equal(datagathering_list, [])

    def test_package_datagathering_list_wrong_datagathering_id(self):
        '''
        Calling ckanext_package_datagathering_list with a bad package id raises a
        ValidationError.
        '''
        factories.Dataset()['id']

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_package_datagathering_list',
                                datagathering_id='a-bad-id')

    def test_package_datagathering_list_datagathering_has_package(self):
        '''
        Calling ckanext_package_datagathering_list with a package that has a
        datagathering should return that datagathering.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        datagathering = factories.Dataset(type='datagathering')
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering['id'])

        datagathering_list = helpers.call_action('ckanext_package_datagathering_list',
                                            package_id=package['id'])

        # We've got an item in the datagathering_list
        nosetools.assert_equal(len(datagathering_list), 1)
        # The list item should have the correct name property
        nosetools.assert_equal(datagathering_list[0]['name'], datagathering['name'])

    def test_package_datagathering_list_datagathering_has_two_packages(self):
        '''
        Calling ckanext_package_datagathering_list with a package that has two
        datagatherings should return the datagatherings.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        datagathering_one = factories.Dataset(type='datagathering')
        datagathering_two = factories.Dataset(type='datagathering')
        context = {'user': sysadmin['name']}
        # create first association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering_one['id'])
        # create second association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering_two['id'])

        datagathering_list = helpers.call_action('ckanext_package_datagathering_list',
                                            package_id=package['id'])

        # We've got two items in the datagathering_list
        nosetools.assert_equal(len(datagathering_list), 2)

    def test_package_datagathering_list_package_isnot_a_datagathering(self):
        '''
        Calling ckanext_package_datagathering_list with a datagathering id should raise a
        ValidationError.

        Since Datagatherings are Packages under the hood, make sure we treat them
        differently.
        '''
        sysadmin = factories.User(sysadmin=True)

        package = factories.Dataset()
        datagathering = factories.Dataset(type='datagathering')
        context = {'user': sysadmin['name']}
        # create an association
        helpers.call_action('ckanext_datagathering_package_association_create',
                            context=context, package_id=package['id'],
                            datagathering_id=datagathering['id'])

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_package_datagathering_list',
                                package_id=datagathering['id'])


class TestDatagatheringAdminList(DatagatheringFunctionalTestBase):

    '''Tests for ckanext_datagathering_admin_list'''

    def test_datagathering_admin_list_no_datagathering_admins(self):
        '''
        Calling ckanext_datagathering_admin_list on a site that has no datagatherings
        admins returns an empty list.
        '''

        datagathering_admin_list = helpers.call_action('ckanext_datagathering_admin_list')

        nosetools.assert_equal(datagathering_admin_list, [])

    def test_datagathering_admin_list_users(self):
        '''
        Calling ckanext_datagathering_admin_list will return users who are datagathering
        admins.
        '''
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_two['name'])
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_three['name'])

        datagathering_admin_list = helpers.call_action('ckanext_datagathering_admin_list', context={})

        nosetools.assert_equal(len(datagathering_admin_list), 3)
        for user in [user_one, user_two, user_three]:
            nosetools.assert_true({'name': user['name'], 'id': user['id']} in datagathering_admin_list)

    def test_datagathering_admin_only_lists_admin_users(self):
        '''
        Calling ckanext_datagathering_admin_list will only return users who are
        datagathering admins.
        '''
        user_one = factories.User()
        user_two = factories.User()
        user_three = factories.User()

        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_one['name'])
        helpers.call_action('ckanext_datagathering_admin_add', context={},
                            username=user_two['name'])

        datagathering_admin_list = helpers.call_action('ckanext_datagathering_admin_list', context={})

        nosetools.assert_equal(len(datagathering_admin_list), 2)
        # user three isn't in list
        nosetools.assert_true({'name': user_three['name'], 'id': user_three['id']} not in datagathering_admin_list)


class TestPackageSearchBeforeSearch(DatagatheringFunctionalTestBase):

    '''
    Extension uses the `before_search` method to alter search parameters.
    '''

    def test_package_search_no_additional_filters(self):
        '''
        Perform package_search with no additional filters should not include
        datagatherings.
        '''
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type='datagathering')
        factories.Dataset(type='custom')

        search_results = helpers.call_action('package_search', context={})['results']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 3)
        nosetools.assert_true('datagathering' not in types)
        nosetools.assert_true('custom' in types)

    def test_package_search_filter_include_datagathering(self):
        '''
        package_search filtered to include datasets of type datagathering should
        only include datagatherings.
        '''
        factories.Dataset()
        factories.Dataset()
        factories.Dataset(type='datagathering')
        factories.Dataset(type='custom')

        search_results = helpers.call_action('package_search', context={},
                                             fq='dataset_type:datagathering')['results']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 1)
        nosetools.assert_true('datagathering' in types)
        nosetools.assert_true('custom' not in types)
        nosetools.assert_true('dataset' not in types)


class TestUserShowBeforeSearch(DatagatheringFunctionalTestBase):

    '''
    Extension uses the `before_search` method to alter results of user_show
    (via package_search).
    '''

    def test_user_show_no_additional_filters(self):
        '''
        Perform package_search with no additional filters should not include
        datagatherings.
        '''
        if not toolkit.check_ckan_version(min_version='2.4'):
            raise SkipTest('Filtering out datagatherings requires CKAN 2.4+ (ckan/ckan/issues/2380)')

        user = factories.User()
        factories.Dataset(user=user)
        factories.Dataset(user=user)
        factories.Dataset(user=user, type='datagathering')
        factories.Dataset(user=user, type='custom')

        search_results = helpers.call_action('user_show', context={},
                                             include_datasets=True,
                                             id=user['name'])['datasets']

        types = [result['type'] for result in search_results]

        nosetools.assert_equal(len(search_results), 3)
        nosetools.assert_true('datagathering' not in types)
        nosetools.assert_true('custom' in types)
