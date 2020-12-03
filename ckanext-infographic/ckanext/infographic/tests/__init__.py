from ckanext.infographic.model import setup as infographic_setup


try:
    import ckan.tests.helpers as helpers
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.helpers as helpers


class InfographicFunctionalTestBase(helpers.FunctionalTestBase):

    def setup(self):
        '''Reset the database and clear the search indexes.'''
        super(InfographicFunctionalTestBase, self).setup()
        # set up infographic tables
        infographic_setup()
