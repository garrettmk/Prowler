import re
import json

from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, event
from sqlalchemy import Table, Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy import ForeignKey, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy import and_, or_

from sqlalchemy.sql import label
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method, hybrid_property
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref
from sqlalchemy.orm.exc import ObjectDeletedError, NoResultFound

from sqlalchemy.sql.functions import func

from PyQt5.QtSql import QSqlQuery


# Helper function to convert SQLAlchemy queries into QSqlQuery objects
def saquery_to_qtquery(sa_query):
    statement = sa_query.statement.compile()
    qtquery = QSqlQuery()
    qtquery.prepare(str(statement))
    for name, value in statement.params.items():
        qtquery.bindValue(':' + name, value)
    return qtquery


# Make sure foreign keys are enabled
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session configuration
session_factory = sessionmaker()
Session = scoped_session(session_factory)


# Helper function, used in some of the repr's
def trunc(string, length=30):
    if string is None:
        return ''
    return (string[:length - 3] + '...') if len(string) > length else string


# Database classes
Base = declarative_base()


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column(String(collation='NOCASE'), nullable=False, unique=True)
    url = Column(String(collation='NOCASE'))

    tax_rate = Column(Float, default=0)
    ship_rate = Column(Float, default=0)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)


class Listing(Base):
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    vendor_id = Column(Integer, ForeignKey(Vendor.id, ondelete='CASCADE'), nullable=False)
    vendor = relationship(Vendor)
    sku = Column(String(collation='NOCASE'), nullable=False)

    title = Column(String)
    brand = Column(String(collation='NOCASE'))
    model = Column(String(collation='NOCASE'))
    upc = Column(Integer)

    height = Column(Float)
    width = Column(Float)
    depth = Column(Float)
    weight = Column(Float)

    quantity = Column(Integer)
    price = Column(Float)
    url = Column(String(collation='NOCASE'))

    updated = Column(DateTime, default=func.now())

    __table_args__ = (UniqueConstraint('vendor_id', 'sku', name='vendor_sku_key'), {})
    __mapper_args__ = {'polymorphic_identity': 'listing',
                       'polymorphic_on': 'type'}

    def __repr__(self):
        return "<%s(title='%s')>" % (__class__, self.title)

    @hybrid_property
    def unit_price(self):
        return round(self.price / self.quantity, 2)

    @unit_price.expression
    def unit_price(cls):
        return func.round(cls.price / cls.quantity, 2)


class AmazonCategory(Base):
    __tablename__ = 'amz_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(collation='NOCASE'), nullable=False)
    scale = Column(Integer, default=1)
    product_category_id = Column(String)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)


class AmazonMerchant(Base):
    __tablename__ = 'merchants'

    id = Column(Integer, primary_key=True)
    name = Column(String(collation='NOCASE'), nullable=False, unique=True)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)


class AmazonListing(Listing):
    __tablename__ = 'amz_listings'

    id = Column(Integer, ForeignKey(Listing.id, ondelete='CASCADE'), primary_key=True)

    salesrank = Column(Integer)
    offers = Column(Integer)
    hasprime = Column(Boolean)

    category_id = Column(Integer, ForeignKey(AmazonCategory.id))
    category = relationship(AmazonCategory)

    merchant_id = Column(Integer, ForeignKey(AmazonMerchant.id))

    __mapper_args__ = {'polymorphic_identity': 'amz_listing'}

    def __repr__(self):
        return "<%s(sku='%s', title='%s')>" % (__class__, self.sku, trunc(self.title))


class AmzProductHistory(Base):
    __tablename__ = 'amz_history'

    id = Column(Integer, primary_key=True)
    amz_listing_id = Column(Integer, ForeignKey(AmazonListing.id, ondelete='CASCADE'))
    amz_listing = relationship(AmazonListing, backref='history')

    price = Column(Float)
    salesrank = Column(Integer)
    hasprime = Column(Boolean)
    merchant_id = Column(Integer, ForeignKey(AmazonMerchant.id))
    offers = Column(Integer)
    timestamp = Column(DateTime)

    def __repr__(self):
        return "<%s(id=%s)>" % (__class__, self.id)


class AmzPriceAndFees(Base):
    __tablename__ = 'amzpriceandfees'

    id = Column(Integer, primary_key=True)
    amz_listing_id = Column(Integer, ForeignKey(AmazonListing.id, ondelete='CASCADE'), nullable=False)
    amz_listing = relationship(AmazonListing)

    price = Column(Float)
    fba = Column(Float)
    prep = Column(Float)
    ship = Column(Float)

    def __repr__(self):
        return "<%s(id=%s, price=%s, fba=%s)>" % (__class__, self.id, self.price, self.fba)


class VendorListing(Listing):
    __tablename__ = 'vendor_listings'

    id = Column(Integer, ForeignKey(Listing.id, ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = {'polymorphic_identity': 'vendor_listing'}

    def __repr__(self):
        return "<%s(sku='%s', title='%s')>" % (__class__, self.sku, trunc(self.title))


class List(Base):
    __tablename__ = 'lists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    is_amazon = Column(Boolean, default=False)

    def __repr__(self):
        return "<%s(name=%s, is_amazon=%s)>" % (__class__, self.name, self.is_amazon)


class ListMembership(Base):
    __tablename__ = 'listmembership'

    list_id = Column(Integer, ForeignKey(List.id, ondelete='CASCADE'), primary_key=True)
    listing_id = Column(Integer, ForeignKey(Listing.id, ondelete='CASCADE'), primary_key=True)

    list = relationship(List)


class LinkedProducts(Base):
    __tablename__ = 'linkedproducts'

    amz_listing_id = Column(Integer, ForeignKey(Listing.id, ondelete='CASCADE'), primary_key=True)
    vnd_listing_id = Column(Integer, ForeignKey(Listing.id, ondelete='CASCADE'), primary_key=True)

    confidence = Column(Integer)
    brand_match = Column(Integer)
    model_match = Column(Integer)
    title_match = Column(Integer)

    amz_listing = relationship(Listing, backref=backref('vnd_links', cascade='all, delete-orphan', passive_deletes=True),
                                        primaryjoin=Listing.id==amz_listing_id)
    vnd_listing = relationship(Listing, backref=backref('amz_links', cascade='all, delete-orphan', passive_deletes=True),
                                        primaryjoin=Listing.id==vnd_listing_id)

    def __repr__(self):
        return "<%s(amz_listing_id='%s', vnd_listng_id='%s', confidence='%s')>" % \
               (__class__, self.amz_listing_id, self.vnd_listing_id, self.confidence)


class Operation(Base):
    """A sequence of instructions to be processed by the OperationManager class."""
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    priority = Column(Integer, nullable=False, default=0)

    operation = Column(String)
    param_string = Column(String)

    scheduled = Column(DateTime, default=func.now())
    complete = Column(Boolean, default=False)
    error = Column(Boolean, default=False)
    message = Column(String)

    listing_id = Column(String, ForeignKey(Listing.id, ondelete='CASCADE'))
    listing = relationship(Listing)

    def __repr__(self):
        return "<%s(operation='%s', listing_id=%s, priority=%s, scheduled=%s)>" % \
               (__class__, self.operation, self.listing_id, self.priority, self.scheduled)

    @property
    def params(self):
        if self.param_string:
            return json.loads(self.param_string)
        else:
            return {}

    @params.setter
    def params(self, values):
        self.param_string = json.dumps(values)

    @staticmethod
    def GenericOperation(operation, params=None, **kwargs):
        return Operation(operation=operation,
                         param_string=json.dumps(params) if params else '',
                         **kwargs)

    @staticmethod
    def FindAmazonMatches(params=None, **kwargs):
        return Operation.GenericOperation(operation='FindAmazonMatches',
                                          params=params,
                                          **kwargs)

    @staticmethod
    def GetMyFeesEstimate(params=None, **kwargs):
        return Operation.GenericOperation(operation='GetMyFeesEstimate',
                                          params=params,
                                          **kwargs)

    @staticmethod
    def UpdateAmazonListing(params=None, **kwargs):
        return Operation.GenericOperation(operation='UpdateAmazonListing',
                                          params=params,
                                          **kwargs)

    @staticmethod
    def SearchAmazon(params=None, **kwargs):
        return Operation.GenericOperation(operation='SearchAmazon',
                                          params=params,
                                          **kwargs)









