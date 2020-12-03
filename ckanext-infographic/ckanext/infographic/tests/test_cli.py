import ckan.tests.helpers as helpers

try:
    import ckan.tests.factories as factories
except ImportError:  # for ckan <= 2.3
    import ckan.new_tests.factories as factories

from ckan.lib.helpers import render_markdown
from ckanext.infographic.commands.migrate import MigrationCommand


class TestMigrationCommand(object):
    '''Tests for MigrationCommand.markdown_to_html'''

    @classmethod
    def setup_class(cls):
        cls.migration_cmd = MigrationCommand('migration-command')

    def setup(self):
        helpers.reset_db()

    def test_notes_are_migrated_from_markdown_to_html(self):
        infographic1 = factories.Dataset(
            type='infographic',
            name='my-infographic',
            notes='# Title')

        infographic2 = factories.Dataset(
            type='infographic',
            name='my-infographic-2',
            notes='# Title 2')

        self.migration_cmd.args = ['markdown_to_html']
        self.migration_cmd.markdown_to_html()

        migrated_infographic1 = helpers.call_action(
            'package_show',
            context={'ignore_auth': True},
            id=infographic1['id']
        )
        assert(
            migrated_infographic1['notes'] == render_markdown(infographic1['notes'])
            )

        migrated_infographic2 = helpers.call_action(
            'package_show',
            context={'ignore_auth': True},
            id=infographic2['id']
        )
        assert(
            migrated_infographic2['notes'] == render_markdown(infographic2['notes'])
            )
