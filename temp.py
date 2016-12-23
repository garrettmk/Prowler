from database import *
from sqlalchemy.event import listen
from itertools import chain

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

amazon = Vendor(name='Amazon', id=0)
acme = Vendor(name='ACME', tax_rate=.09, ship_rate=.3)
acorp = Vendor(name='ACorp', tax_rate=0, ship_rate=.8)


session.add_all([amazon, acme, acorp])
session.commit()

vnd1 = VendorListing(vendor_id=acme.id, sku='ACME001', price=24.99, quantity=10)
vnd2 = VendorListing(vendor_id=acme.id, sku='ACME002', price=18.99, quantity=10)
vnd3 = VendorListing(vendor_id=acorp.id, sku='ACORP1', price=10.00, quantity=15)
amz1 = AmazonListing(vendor_id=amazon.id, sku='A12345', price=24.99, quantity=1)
amz2 = AmazonListing(vendor_id=amazon.id, sku='B12345', price=29.99, quantity=1)
link1 = LinkedProducts(amz_listing=amz1, vnd_listing=vnd1)
link2 = LinkedProducts(amz_listing=amz1, vnd_listing=vnd2)
link3 = LinkedProducts(amz_listing=amz1, vnd_listing=vnd3)

price1 = AmzPriceAndFees(amz_listing=amz1, price=24.99)
price2 = AmzPriceAndFees(amz_listing=amz1, price=31.99)

cat1 = AmazonCategory(name='Kitchen Stuff')
amz1.category = cat1

session.add_all([vnd1, vnd2, vnd3, amz1, link1, link2, price1, price2])
session.commit()


def listener(session):
    for item in chain(session.new, session.dirty, session.deleted):
        if isinstance(item, Operation):
            break
    else:
        return

    print('Change in Operation table detected.')

listen(session, 'before_commit', listener)



import amazonmws as mws
import mwskeys, pakeys
import requests

mwsapi = mws.Products(mwskeys.accesskey, mwskeys.secretkey, mwskeys.sellerid)
mwsapi.make_request = requests.request

paapi = mws.ProductAdvertising(pakeys.accesskey, pakeys.secretkey, pakeys.associatetag)
paapi.make_request = requests.request


from database import *
from dbhelpers import *

from sqlalchemy.sql import alias

engine = create_engine('sqlite:///prowler.db')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

prod = session.query(AmazonListing).filter_by(sku='B00XLMX4KC').one()
hist = ProductHistoryStats(session, prod.id)


def slope(one, two):
    scale = 1 - (min(one, two) / max(one, two))
    return scale, scale * (two - one) / 3600

for one, two in [(103000, 14000), (18000, 8000), (3200, 2800), (100000, 90000)]:
    print(slope(one, two))
