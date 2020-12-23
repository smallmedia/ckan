from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper, Session
from ckan import model

import logging
log = logging.getLogger(__name__)


datagathering_package_assocation_table = None
datagathering_admin_table = None


def setup():
    # setup datagathering_package_assocation_table
    if datagathering_package_assocation_table is None:
        define_datagathering_package_association_table()
        log.debug('DatagatheringPackageAssociation table defined in memory')

    if model.package_table.exists():
        if not datagathering_package_assocation_table.exists():
            datagathering_package_assocation_table.create()
            log.debug('DatagatheringPackageAssociation table create')
        else:
            log.debug('DatagatheringPackageAssociation table already exists')
    else:
        log.debug('DatagatheringPackageAssociation table creation deferred')

    # setup datagathering_admin_table
    if datagathering_admin_table is None:
        define_datagathering_admin_table()
        log.debug('DatagatheringAdmin table defined in memory')

    if model.user_table.exists():
        if not datagathering_admin_table.exists():
            datagathering_admin_table.create()
            log.debug('DatagatheringAdmin table create')
        else:
            log.debug('DatagatheringAdmin table already exists')
    else:
        log.debug('DatagatheringAdmin table creation deferred')


class DatagatheringBaseModel(DomainObject):
    @classmethod
    def filter(cls, **kwargs):
        return Session.query(cls).filter_by(**kwargs)

    @classmethod
    def exists(cls, **kwargs):
        if cls.filter(**kwargs).first():
            return True
        else:
            return False

    @classmethod
    def get(cls, **kwargs):
        instance = cls.filter(**kwargs).first()
        return instance

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        Session.add(instance)
        Session.commit()
        return instance.as_dict()


class DatagatheringPackageAssociation(DatagatheringBaseModel):

    @classmethod
    def get_package_ids_for_datagathering(cls, datagathering_id):
        '''
        Return a list of package ids associated with the passed datagathering_id.
        '''
        datagathering_package_association_list = \
            Session.query(cls.package_id).filter_by(
                datagathering_id=datagathering_id).all()
        return datagathering_package_association_list

    @classmethod
    def get_datagathering_ids_for_package(cls, package_id):
        '''
        Return a list of datagathering ids associated with the passed package_id.
        '''
        datagathering_package_association_list = \
            Session.query(cls.datagathering_id).filter_by(
                package_id=package_id).all()
        return datagathering_package_association_list


def define_datagathering_package_association_table():
    global datagathering_package_assocation_table

    datagathering_package_assocation_table = Table(
        'datagathering_package_association', metadata,
        Column('package_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('datagathering_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False)
    )

    mapper(DatagatheringPackageAssociation, datagathering_package_assocation_table)


class DatagatheringAdmin(DatagatheringBaseModel):

    @classmethod
    def get_datagathering_admin_ids(cls):
        '''
        Return a list of datagathering admin user ids.
        '''
        id_list = [i for (i, ) in Session.query(cls.user_id).all()]
        return id_list

    @classmethod
    def is_user_datagathering_admin(cls, user):
        '''
        Determine whether passed user is in the datagathering admin list.
        '''
        return (user.id in cls.get_datagathering_admin_ids())


def define_datagathering_admin_table():
    global datagathering_admin_table

    datagathering_admin_table = Table('datagathering_admin', metadata,
                                 Column('user_id', types.UnicodeText,
                                        ForeignKey('user.id',
                                                   ondelete='CASCADE',
                                                   onupdate='CASCADE'),
                                        primary_key=True, nullable=False))

    mapper(DatagatheringAdmin, datagathering_admin_table)
