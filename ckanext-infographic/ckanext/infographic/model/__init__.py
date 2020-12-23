from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import types

from ckan.model.domain_object import DomainObject
from ckan.model.meta import metadata, mapper, Session
from ckan import model

import logging
log = logging.getLogger(__name__)


infographic_package_assocation_table = None
infographic_admin_table = None


def setup():
    # setup infographic_package_assocation_table
    if infographic_package_assocation_table is None:
        define_infographic_package_association_table()
        log.debug('InfographicPackageAssociation table defined in memory')

    if model.package_table.exists():
        if not infographic_package_assocation_table.exists():
            infographic_package_assocation_table.create()
            log.debug('InfographicPackageAssociation table create')
        else:
            log.debug('InfographicPackageAssociation table already exists')
    else:
        log.debug('InfographicPackageAssociation table creation deferred')

    # setup infographic_admin_table
    if infographic_admin_table is None:
        define_infographic_admin_table()
        log.debug('InfographicAdmin table defined in memory')

    if model.user_table.exists():
        if not infographic_admin_table.exists():
            infographic_admin_table.create()
            log.debug('InfographicAdmin table create')
        else:
            log.debug('InfographicAdmin table already exists')
    else:
        log.debug('InfographicAdmin table creation deferred')


class InfographicBaseModel(DomainObject):
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


class InfographicPackageAssociation(InfographicBaseModel):

    @classmethod
    def get_package_ids_for_infographic(cls, infographic_id):
        '''
        Return a list of package ids associated with the passed infographic_id.
        '''
        infographic_package_association_list = \
            Session.query(cls.package_id).filter_by(
                infographic_id=infographic_id).all()
        return infographic_package_association_list

    @classmethod
    def get_infographic_ids_for_package(cls, package_id):
        '''
        Return a list of infographic ids associated with the passed package_id.
        '''
        infographic_package_association_list = \
            Session.query(cls.infographic_id).filter_by(
                package_id=package_id).all()
        return infographic_package_association_list


def define_infographic_package_association_table():
    global infographic_package_assocation_table

    infographic_package_assocation_table = Table(
        'infographic_package_association', metadata,
        Column('package_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False),
        Column('infographic_id', types.UnicodeText,
               ForeignKey('package.id',
                          ondelete='CASCADE',
                          onupdate='CASCADE'),
               primary_key=True, nullable=False)
    )

    mapper(InfographicPackageAssociation, infographic_package_assocation_table)


class InfographicAdmin(InfographicBaseModel):

    @classmethod
    def get_infographic_admin_ids(cls):
        '''
        Return a list of infographic admin user ids.
        '''
        id_list = [i for (i, ) in Session.query(cls.user_id).all()]
        return id_list

    @classmethod
    def is_user_infographic_admin(cls, user):
        '''
        Determine whether passed user is in the infographic admin list.
        '''
        return (user.id in cls.get_infographic_admin_ids())


def define_infographic_admin_table():
    global infographic_admin_table

    infographic_admin_table = Table('infographic_admin', metadata,
                                 Column('user_id', types.UnicodeText,
                                        ForeignKey('user.id',
                                                   ondelete='CASCADE',
                                                   onupdate='CASCADE'),
                                        primary_key=True, nullable=False))

    mapper(InfographicAdmin, infographic_admin_table)
