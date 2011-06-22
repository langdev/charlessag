
# -*- coding: utf-8 -*-
import time
import collections

import sqlalchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy import TIMESTAMP
from sqlalchemy import asc, desc
from sqlalchemy.types import *
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker, object_session
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import column_property, composite, deferred
from sqlalchemy.orm import synonym
from sqlalchemy.sql import select, and_, or_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import synonym_for

from database_private import CHARLES_DATABASE

engine = sqlalchemy.create_engine(CHARLES_DATABASE, echo=False)

Session = sessionmaker(autoflush=True, autocommit=True, bind=engine)
session = Session()
 
Base = declarative_base(bind=engine)

class Project(Base):
    """Project는 찰지거나 찰지게 될 예정인 단위이다."""
    __tablename__ = 'projects'
   
    project_id = Column(Integer, primary_key=True)
    id = synonym('project_id')
    parent_id = Column(Integer) # null이면 최상위를, 아니면 project_id 참조
    name = Column(Unicode(256), nullable=False)
    
    jobs = relationship('Job', backref='project',
        primaryjoin='Job.project_id == Project.project_id')
    members = relationship('Member', backref='project',
        primaryjoin='Member.project_id == Project.project_id')

    @property
    def parent(self):
        return Project.by(project_id=self.parent_id)

    @property
    def children(self):
        return Project.filter(Project.parent_id == self.project_id)

    def __init__(self, name, parent_id=None):
        self.name = name
        self.parent_id = parent_id

    def __repr__(self):
        return "<Project(%d<%d,'%s')>" % (self.id, self.parent_id, self.name)

class Job(Base):
    """Job은 Project를 찰지게 만들기 위해 찰싹거릴 수 있는 대상이다."""
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True)
    id = synonym('job_id')
    project_id = Column(Integer, ForeignKey(Project.project_id), nullable=False)
    name = Column(Unicode(256), nullable=False)

    votes = relationship('Vote', backref='job',
                         primaryjoin='Vote.job_id == Job.job_id')

    def __init__(self, project_id, name):
        self.project_id = project_id
        self.name = name

    def __repr__(self):
        return "<Job(%d,'%s')>" % (self.project_id, self.name)

class User(Base):
    """User는 어떤 Project의 Member로 참여하여 Project를 찰지게 하거나
    다른 Project를 찰지게 만들도록 어떤 Job을 찰싹거릴 수 있는 단위이다.
    찰싹에 한번 이상 로그인 해야 등록된다.
    한 Member에 대해 여러 표현형을 지원하면 내맘대로 추가할 수 있겠으나 물론
    귀찮다...
    """
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    id = synonym('user_id')
    name = Column(Unicode(64), nullable=False) # langdev username
    
    members = relationship('Member', backref='user',
        primaryjoin='Member.user_id == User.user_id')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<User(%d,'%s')>" % (self.user_id, self.name)

class Member(Base):
    """Member는 어떤 Project를 찰지게 만드는 또는 만들 User이다."""
    __tablename__ = 'project_members'
   
    project_id = Column(Integer, ForeignKey(Project.project_id),
                        primary_key=True)
    user_id = Column(Integer, ForeignKey(User.user_id),
                     primary_key=True)
    name = Column(Unicode(128))
    

    def __init__(self, project_id, user_id, name=None):
        self.project_id = project_id
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return "<Member(%d,%d,'%s')>" % (self.project_id, self.user_id, name)

class Vote(Base):
    """Vote는 User가 어떤 Project를 찰지게 하기 위해 찰싹거리는 단위이다."""
    __tablename__ = 'votes'

    job_id = Column(Integer, ForeignKey(Job.job_id), primary_key=True)
    user_id = Column(Integer, ForeignKey(User.user_id), primary_key=True)
    comment = Column(UnicodeText, nullable=False)


"""Add shortcut methods filter_by, filter, by to each declarative class.
# filter_by: shortcut of filter_by query from global session
# filter: shortcut of filter query from global session
# by: shortcut of filter query from glabal session, and take one() from it
"""
import sys
import inspect
import types
for name, cls in inspect.getmembers(sys.modules[__name__]):
    if inspect.isclass(cls) and issubclass(cls, Base) and cls != Base:
        def filter_by(cls, **kwargs):
            return session.query(cls).filter_by(**kwargs)
        def filter(cls, criterion):
            return session.query(cls).filter(criterion)
        def filter_one_by(cls, **kwargs):
            return cls.filter_by(**kwargs).one()
        def all(cls):
            return session.query(cls)
        setattr(cls, 'filter_by', types.MethodType(filter_by, cls, cls))
        setattr(cls, 'filter', types.MethodType(filter, cls, cls))
        setattr(cls, 'by', types.MethodType(filter_one_by, cls, cls))
        setattr(cls, 'all', types.MethodType(all, cls, cls))

