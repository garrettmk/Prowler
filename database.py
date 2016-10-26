from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, aliased
from sqlalchemy.orm.exc import *

# Session configuration
session_factory = sessionmaker()
Session = scoped_session(session_factory)

# Helper function, used in some of the repr's
def trunc(string, length=20):
    return (string[:length - 3] + '...') if len(string) > length else string


Base = declarative_base()


class AmazonCategory(Base):
    __tablename__ = 'amz_categories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    scale = Column(Integer)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)

class AmazonMerchant(Base):
    __tablename__ = 'merchants'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)


class AmazonListing(Base):
    __tablename__ = 'amz_listings'

    asin = Column(String, primary_key=True)
    title = Column(String)
    category_id = Column(Integer, ForeignKey(AmazonCategory.id))
    salesrank = Column(Integer)
    price = Column(Float)
    quantity = Column(Integer)

    offers = Column(Integer)
    hasprime = Column(Boolean)
    merchant_id = Column(Integer, ForeignKey(AmazonMerchant.id))

    brand = Column(String)
    model = Column(String)
    upc = Column(Integer)

    lastupdate = Column(DateTime)

    category = relationship(AmazonCategory)
    merchant = relationship(AmazonMerchant)
    linked_products = relationship('LinkedProducts', back_populates='amz_listing')

    def __repr__(self):
        return "<%s(asin='%s', title='%s')>" % (__class__, self.asin, trunc(self.title))


class Vendor(Base):
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    url = Column(String)

    def __repr__(self):
        return "<%s(name='%s')>" % (__class__, self.name)


class VendorListing(Base):
    __tablename__ = 'vendor_listings'

    vendor_id = Column(Integer, ForeignKey(Vendor.id), primary_key=True)
    sku = Column(String, primary_key=True)

    title = Column(String)
    brand = Column(String)
    model = Column(String)
    upc = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    url = Column(String)

    lastupdate = Column(DateTime)

    vendor = relationship(Vendor)
    linked_products = relationship('LinkedProducts', back_populates='vnd_listing')

    def __repr__(self):
        return "<%s(sku='%s', title='%s')>" % (__class__, self.sku, trunc(self.title))


class LinkedProducts(Base):
    __tablename__ = 'linkedproducts'

    amz_listing_id = Column(String, ForeignKey(AmazonListing.asin), primary_key=True)
    vnd_listing_id = Column(String, ForeignKey(VendorListing.sku), primary_key=True)
    vendor_id = Column(Integer, ForeignKey(Vendor.id), primary_key=True)

    confidence = Column(Integer)
    brand_match = Column(Integer)
    model_match = Column(Integer)
    title_match = Column(Integer)

    amz_listing = relationship(AmazonListing, back_populates='linked_products')
    vnd_listing = relationship(VendorListing, back_populates='linked_products')
    source = relationship(Vendor)

    def __repr__(self):
        return "<%s(asin='%s', sku='%s', confidence='%i')>" % (__class__, self.amz_listing_id, self.src_listing_id, self.confidence)

class ListMembership(Base):
    __tablename__ =  'listmemberships'

    list_id = Column(Integer, ForeignKey(List.id), primary_key=True)
    

# TODO: Implement multi-operation methods
class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    priority = Column(Integer, nullable=False, default=0)
    operation = Column(String, nullable=False)
    scheduled = Column(DateTime)
    complete = Column(Boolean, default=False)

    asin = Column(String, ForeignKey(AmazonListing.asin))
    vendor_id = Column(String, ForeignKey(Vendor.id))
    sku = Column(String, ForeignKey(VendorListing.sku))

    def __repr__(self):
        return "<%s(operation='%s', scheduled='%s', asin='%s', sku='%s)>" % (__class__, self.operation, self.scheduled, self.asin, self.sku)

    @property
    def api_call(self):
        """Return the name of the next Amazon API call for this operation."""
        return self.operation

    @property
    def op_name(self):
        """Return the name of the next operation to perform."""
        return self.operation


class List(Base):
    __tablename__ = 'lists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)