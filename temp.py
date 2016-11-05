from database import *
from sqlalchemy.event import listen
from itertools import chain

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

amazon = Vendor(name='Amazon')
acme = Vendor(name='ACME')
acorp = Vendor(name='ACorp')


session.add_all([amazon, acme, acorp])
session.commit()

vnd1 = VendorListing(vendor_id=acme.id, sku='ACME001', price=24.99, quantity=10)
vnd2 = VendorListing(vendor_id=acme.id, sku='ACME002')
vnd3 = VendorListing(vendor_id=acorp.id, sku='ACORP1')
amz1 = AmazonListing(vendor_id=amazon.id, sku='A12345')
amz2 = AmazonListing(vendor_id=amazon.id, sku='B12345')
link1 = LinkedProducts(amz_listing=amz1, vnd_listing=vnd1)
link2 = LinkedProducts(amz_listing=amz1, vnd_listing=vnd2)
link3 = LinkedProducts(amz_listing=amz2, vnd_listing=vnd3)

cat1 = AmazonCategory(name='Kitchen Stuff')
amz1.category = cat1

session.add_all([vnd1, vnd2, vnd3, amz1, link1, link2])
# session.commit()

def listener(session):
    for item in chain(session.new, session.dirty, session.deleted):
        if isinstance(item, Operation):
            break
    else:
        return

    print('Change in Operation table detected.')

listen(session, 'before_commit', listener)