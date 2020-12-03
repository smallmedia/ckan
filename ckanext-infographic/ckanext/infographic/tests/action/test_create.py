from nose import tools as nosetools

from ckan.model.package import Package
import ckan.model as model
import ckan.plugins.toolkit as toolkit

try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers


from ckanext.infographic.model import InfographicPackageAssociation, InfographicAdmin
from ckanext.infographic.tests import InfographicFunctionalTestBase


class TestCreateInfographic(InfographicFunctionalTestBase):

    def test_infographic_create_no_args(self):
        '''
        Calling infographic create without args raises ValidationError.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}

        # no infographics exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 0)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_create',
                                context=context)

        # no infographics (dataset of type 'infographic') created.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 0)

    def test_infographic_create_with_name_arg(self):
        '''
        Calling infographic create with a name arg creates a infographic package.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}

        # no infographics exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 0)

        helpers.call_action('ckanext_infographic_create',
                            context=context, name='my-infographic')

        # a infographics (dataset of type 'infographic') created.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 1)

    def test_infographic_create_with_existing_name(self):
        '''
        Calling infographic create with an existing name raises ValidationError.
        '''
        sysadmin = factories.Sysadmin()
        context = {'user': sysadmin['name']}
        factories.Dataset(type='infographic', name='my-infographic')

        # a single infographics exist.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 1)

        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_create',
                                context=context, name='my-infographic')

        # still only one infographic exists.
        nosetools.assert_equal(model.Session.query(Package)
                               .filter(Package.type == 'infographic').count(), 1)


class TestCreateInfographicPackageAssociation(InfographicFunctionalTestBase):

    def test_association_create_no_args(self):
        '''
        Calling sc/pkg association create with no args raises
        ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_package_association_create',
                                context=context)

        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 0)

    def test_association_create_missing_arg(self):
        '''
        Calling sc/pkg association create with a missing arg raises
        ValidationError.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']

        context = {'user': sysadmin['name']}
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_package_association_create',
                                context=context, package_id=package_id)

        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 0)

    def test_association_create_by_id(self):
        '''
        Calling sc/pkg association create with correct args (package ids)
        creates an association.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        infographic_id = factories.Dataset(type='infographic')['id']

        context = {'user': sysadmin['name']}
        association_dict = helpers.call_action('ckanext_infographic_package_association_create',
                                               context=context, package_id=package_id,
                                               infographic_id=infographic_id)

        # One association object created
        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 1)
        # Association properties are correct
        nosetools.assert_equal(association_dict.get('infographic_id'), infographic_id)
        nosetools.assert_equal(association_dict.get('package_id'), package_id)

    def test_association_create_by_name(self):
        '''
        Calling sc/pkg association create with correct args (package names)
        creates an association.
        '''
        sysadmin = factories.User(sysadmin=True)
        package = factories.Dataset()
        package_name = package['name']
        infographic = factories.Dataset(type='infographic')
        infographic_name = infographic['name']

        context = {'user': sysadmin['name']}
        association_dict = helpers.call_action('ckanext_infographic_package_association_create',
                                               context=context, package_id=package_name,
                                               infographic_id=infographic_name)

        nosetools.assert_equal(model.Session.query(InfographicPackageAssociation).count(), 1)
        nosetools.assert_equal(association_dict.get('infographic_id'), infographic['id'])
        nosetools.assert_equal(association_dict.get('package_id'), package['id'])

    def test_association_create_existing(self):
        '''
        Attempt to create association with existing details returns Validation
        Error.
        '''
        sysadmin = factories.User(sysadmin=True)
        package_id = factories.Dataset()['id']
        infographic_id = factories.Dataset(type='infographic')['id']

        context = {'user': sysadmin['name']}
        # Create association
        helpers.call_action('ckanext_infographic_package_association_create',
                            context=context, package_id=package_id,
                            infographic_id=infographic_id)
        # Attempted duplicate creation results in ValidationError
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_package_association_create',
                                context=context, package_id=package_id,
                                infographic_id=infographic_id)


class TestCreateInfographicAdmin(InfographicFunctionalTestBase):

    def test_infographic_admin_add_creates_infographic_admin_user(self):
        '''
        Calling ckanext_infographic_admin_add adds user to infographic admin list.
        '''
        user_to_add = factories.User()

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 0)

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_to_add['name'])

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 1)
        nosetools.assert_true(user_to_add['id'] in InfographicAdmin.get_infographic_admin_ids())

    def test_infographic_admin_add_multiple_users(self):
        '''
        Calling ckanext_infographic_admin_add for multiple users correctly adds
        them to infographic admin list.
        '''
        user_to_add = factories.User()
        second_user_to_add = factories.User()

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 0)

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_to_add['name'])

        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=second_user_to_add['name'])

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 2)
        nosetools.assert_true(user_to_add['id'] in InfographicAdmin.get_infographic_admin_ids())
        nosetools.assert_true(second_user_to_add['id'] in InfographicAdmin.get_infographic_admin_ids())

    def test_infographic_admin_add_existing_user(self):
        '''
        Calling ckanext_infographic_admin_add twice for same user raises a
        ValidationError.
        '''
        user_to_add = factories.User()

        # Add once
        helpers.call_action('ckanext_infographic_admin_add', context={},
                            username=user_to_add['name'])

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 1)

        # Attempt second add
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_admin_add', context={},
                                username=user_to_add['name'])

        # Still only one InfographicAdmin object.
        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 1)

    def test_infographic_admin_add_username_doesnot_exist(self):
        '''
        Calling ckanext_infographic_admin_add with non-existent username raises
        ValidationError and no InfographicAdmin object is created.
        '''
        nosetools.assert_raises(toolkit.ObjectNotFound, helpers.call_action,
                                'ckanext_infographic_admin_add', context={},
                                username='missing')

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 0)
        nosetools.assert_equal(InfographicAdmin.get_infographic_admin_ids(), [])

    def test_infographic_admin_add_no_args(self):
        '''
        Calling ckanext_infographic_admin_add with no args raises ValidationError
        and no InfographicAdmin object is created.
        '''
        nosetools.assert_raises(toolkit.ValidationError, helpers.call_action,
                                'ckanext_infographic_admin_add', context={})

        nosetools.assert_equal(model.Session.query(InfographicAdmin).count(), 0)
        nosetools.assert_equal(InfographicAdmin.get_infographic_admin_ids(), [])
