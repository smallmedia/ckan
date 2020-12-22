from nose import tools as nosetools
from nose import SkipTest

from ckan.plugins import toolkit as tk
try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers

import ckanext.datagathering.logic.helpers as datagathering_helpers
from ckanext.datagathering.tests import DatagatheringFunctionalTestBase


class TestGetSiteStatistics(DatagatheringFunctionalTestBase):

    def test_dataset_count_no_datasets(self):
        '''
        Dataset and datagathering count is 0 when no datasets, and no datagatherings.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        stats = datagathering_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 0)
        nosetools.assert_equal(stats['datagathering_count'], 0)

    def test_dataset_count_no_datasets_some_datagatherings(self):
        '''
        Dataset and datagathering count is 0 when no datasets, but some datagatherings.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset(type='datagathering')

        stats = datagathering_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 0)
        nosetools.assert_equal(stats['datagathering_count'], 10)

    def test_dataset_count_some_datasets_no_datagatherings(self):
        '''
        Dataset and datagathering count is correct when there are datasets, but no
        datagatherings.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset()

        stats = datagathering_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 10)
        nosetools.assert_equal(stats['datagathering_count'], 0)

    def test_dataset_count_some_datasets_some_datagatherings(self):
        '''
        Dataset and datagathering count is correct when there are datasets and some
        datagatherings.
        '''
        if not tk.check_ckan_version(min_version='2.5'):
            raise SkipTest('get_site_statistics without user broken in CKAN 2.4')
        for i in xrange(0, 10):
            factories.Dataset()

        for i in xrange(0, 5):
            factories.Dataset(type='datagathering')

        stats = datagathering_helpers.get_site_statistics()
        nosetools.assert_equal(stats['dataset_count'], 10)
        nosetools.assert_equal(stats['datagathering_count'], 5)


@helpers.change_config('ckanext.datagathering.editor', 'custom-editor')
def test_get_wysiwyg_editor():
    nosetools.assert_equals(datagathering_helpers.get_wysiwyg_editor(), 'custom-editor')
