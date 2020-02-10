# encoding: utf-8


def upgrade(migrate_engine):
    migrate_engine.execute('''
        ALTER TABLE package_revision
            ADD COLUMN lang text NOT NULL DEFAULT 'fa_IR';

        UPDATE package SET lang = 'fa_IR' WHERE lang IS NULL;
    ''')
