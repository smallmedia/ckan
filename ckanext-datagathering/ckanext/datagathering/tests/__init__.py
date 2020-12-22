from ckanext.datagathering.model import setup as datagathering_setup


try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers


class DatagatheringFunctionalTestBase(helpers.FunctionalTestBase):

    def setup(self):
        '''Reset the database and clear the search indexes.'''
        super(DatagatheringFunctionalTestBase, self).setup()
        # set up datagathering tables
        datagathering_setup()
