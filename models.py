# flask_sqlalchemy/models.py
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://root:Katerina27@localhost/sample_data', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
# We will need this for querying
Base.query = db_session.query_property()

class Tenant(Base):
    __tablename__ = 'tenant'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))


class Sensor(Base):
    __tablename__ = 'sensor'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))


class Data(Base):
    __tablename__ = 'data'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, default=func.now())
    value = Column(Integer, nullable = False)
    sensor_id = Column(Integer, ForeignKey('sensor.id'))
    tenant_id = Column(Integer, ForeignKey('tenant.id'))
    sensor = relationship(
        Sensor,
        backref=backref('sensor',
                        uselist=True,
                        cascade='delete,all'))
    tenant = relationship(
    Tenant,
    backref=backref('tenant',
                    uselist=True,
                    cascade='delete,all'))

