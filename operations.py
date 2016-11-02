import arrow
import requests
import amazonmws as mws
import mwskeys, pakeys

from fuzzywuzzy import fuzz
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from responseparser import ListMatchingProductsParser, ErrorResponseParser, GetLowestOfferListingsForAsinParser
from responseparser import GetMyFeesEstimateParser, GetCompetitivePricingForASINParser
from responseparser import ParseError
from database import *


def remove_symbols(string, repl=''):
    return re.sub(r'[^a-zA-Z0-9\s]', repl, string)


def brand_match(listing1, listing2):
    fits = list()
    brand1 = remove_symbols(listing1.brand or '').lower()
    brand2 = remove_symbols(listing2.brand or '').lower()
    title1 = remove_symbols(listing1.title or '').lower()
    title2 = remove_symbols(listing2.title or '').lower()

    fits.append(fuzz.partial_ratio(brand1, brand2))
    fits.append(fuzz.partial_ratio(brand1, title2))
    fits.append(fuzz.partial_ratio(brand2, title1))
    return max(fits)


def model_match(listing1, listing2):
    fits = list()
    model1 = remove_symbols(listing1.model or '').lower()
    model2 = remove_symbols(listing2.model or '').lower()
    title1 = remove_symbols(listing1.title or '').lower()
    title2 = remove_symbols(listing2.title or '').lower()

    if model1.isdigit() and model2.isdigit():
        fits.append(100 * (model1 in model2 or model2 in model1))
    else:
        fits.append(fuzz.token_set_ratio(model1, model2))

    fits.append(fuzz.token_set_ratio(model1, title2))
    fits.append(fuzz.token_set_ratio(model2, title1))
    return max(fits)


def title_match(listing1, listing2):
    title1 = str(listing1.title or '').lower()
    title2 = str(listing2.title or '').lower()
    return fuzz.token_set_ratio(title1, title2)


class OperationsManager(QObject):

    __instance__ = None
    @classmethod
    def get_instance(cls, parent=None):
        if cls.__instance__ is None:
            cls.__instance__ = OperationsManager(parent=parent)
        return cls.__instance__

    supported_mws = ['ListMatchingProducts', 'GetLowestOfferListingsForASIN', 'GetCompetitivePricingForASIN',
                     'GetMyFeesEstimate']
    supported_pa = ['ItemLookup']
    supported_ops = supported_mws + supported_pa + ['AddToProductHistory']

    operation_complete = pyqtSignal(int)
    status_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super(OperationsManager, self).__init__(parent=parent)
        self.dbsession = Session()
        self.scheduled = {}

        # Set up the Amazon api's and throttling managers
        self.mwsapi = mws.Throttler(mws.Products(mwskeys.accesskey, mwskeys.secretkey, mwskeys.sellerid), blocking=True)
        self.mwsapi.api.make_request = self.make_request

        self.paapi = mws.Throttler(mws.ProductAdvertising(pakeys.accesskey, pakeys.secretkey, pakeys.associatetag), blocking=True)
        self.paapi.api.make_request = self.make_request

        for operation in self.supported_mws:
            self.mwsapi.set_priority_quota(operation, priority=0, quota=mws.LIMITS[operation].quota_max - 2)
            self.mwsapi.set_priority_quota(operation, priority=10, quota=2)

    def start(self):
        """Starts processing operations in the database."""
        self.status_message.emit('Begin processing operations...')
        self.load_next()

    def stop(self):
        """Remove all pending operations from the queue."""
        self.status_message.emit('Stopping all operations.')
        for t_id in self.scheduled:
            self.killTimer(t_id)

        self.scheduled.clear()

    def load_next(self):
        """Load and schedule the next operation of each type listed in self.supported_ops."""
        for op_name in self.supported_ops:
            # Sort first by priority, then by scheduled time, then by id
            next_op = self.dbsession.query(Operation). \
                                     filter(Operation.complete == False). \
                                     filter(Operation.error == False). \
                                     filter(Operation.current_operation.like('{}%'.format(op_name))). \
                                     order_by(Operation.priority.desc()). \
                                     order_by(Operation.scheduled). \
                                     order_by(Operation.id). \
                                     first()

            if next_op is None:
                continue

            # We only want one operation of a given type scheduled at a time, so bump the currently scheduled op
            # if it's priority is lower. If there is already a scheduled operation of this type, return
            already_sched = None
            for t_id, s_op in self.scheduled.items():
                if s_op.operation_name == op_name:
                    already_sched = s_op
                    break

            if already_sched and already_sched.priority < next_op.priority:
                self.killTimer(t_id)
                self.scheduled.pop(t_id)
                self.schedule_op(next_op)
            elif already_sched:
                continue
            else:
                self.schedule_op(next_op)

    def get_wait(self, api_call, priority):
        return max(self.mwsapi.request_wait(api_call, priority), self.paapi.request_wait(api_call, priority))

    def schedule_op(self, op, wait=None):
        # Get next available time from the throttler
        if wait is None:
            wait = self.get_wait(op.operation_name, op.priority)

        # Schedule the timer
        timer_id = self.startTimer(wait * 1000 * 1.1)
        self.scheduled[timer_id] = op

    def timerEvent(self, event):
        """Do the operation scheduled by the given timer."""
        # Kill the timer and get the associated operation
        timer_id = event.timerId()
        self.killTimer(timer_id)
        op = self.scheduled.pop(timer_id)

        # If the op was deleted just load the next one
        try:
            op.id
        except ObjectDeletedError:
            self.load_next()
            return

        # Reschedule the op if necessary
        wait = self.get_wait(op.operation_name, op.priority)
        if wait:
            self.schedule_op(op, wait)
            return

        # Handle the operation
        status_message = 'Processing: \'%s\', priority=%s' % (op.operation_name, op.priority)
        handler = getattr(self, op.operation_name, None)
        if handler is None:
            op.error = True
            op.message = 'No handler found.'
            self.dbsession.commit()

            status_message += ', error: No handler found.'
            self.status_message.emit(status_message)
            return

        handler(op)
        op.advance()

        if op.complete:
            status_message += ': complete.'
            self.operation_complete.emit(op.id)
        elif op.error:
            status_message += ', error: %s' % op.message
        else:
            status_message += ': %s' % op.message

        self.status_message.emit(status_message)

        # Load the next operations
        self.load_next()

    def is_error_response(self, response, op):
        """Test if the response is an error, and take appropriate action."""
        if response.ok:
            return False

        # Try to parse the error response, if there is one
        msg = 'Status code %i, ' % response.status_code
        try:
            parser = ErrorResponseParser(response.content.decode())
            msg += '%s - %s' % (parser.code, parser.message)
        except ParseError:
            msg += 'no parsable response.'

        op.error = True
        op.message = msg

        # 400 usually means an invalid parameter
        if response.status_code in [400]:
            pass
        # 401, 403, 404 means there was a problem with the keys, signature, or address used
        elif response.status_code in [401, 403, 404]:
            self.stop()
        # 500 or 503 usually means internal service error or throttling
        elif response.status_code in [500, 503]:
            self.schedule_op(op, wait=60)

        return True

    # TODO: Use QNetworkAccessManager and ProcessEvents() to make network requests
    def make_request(self, *args, **kwargs):
        """Make the actual network request."""
        return requests.request(*args, **kwargs)

    def ListMatchingProducts(self, op):
        """Query Amazon for products matching a given listing.

        Parameters:     linkif: create a link only if the conditions are met
                            conf: match confidence greater than or equal to the given value.

                        priceif: create followup operations to get pricing for matched products
                            salesrank: sales rank less than or equal to the given value

                        feesif: on pricing operations, request fees if the conditions are met
                            priceratio: the price ratio of the matched product to the listing
            """
        vnd_listing = self.dbsession.query(VendorListing).filter_by(id=op.listing_id).first()
        params = op.params

        title = str(vnd_listing.title).replace(vnd_listing.brand, '').replace(vnd_listing.model, '').strip()
        query = ' '.join([vnd_listing.brand, vnd_listing.model, title])

        r = self.mwsapi.ListMatchingProducts(priority=op.priority, MarketplaceId=self.mwsapi.api.market_id(), Query=query)
        if self.is_error_response(r, op):
            return

        parser = ListMatchingProductsParser(r.content.decode())

        for product in parser.get_products():
            previous_id = self.dbsession.query(AmazonListing.id).filter_by(sku=product['asin']).scalar()
            amz_listing = self.dbsession.merge(AmazonListing(id=previous_id, vendor_id=0, sku=product['asin']))

            amz_listing.title = product['title']
            amz_listing.brand = product['brand']
            amz_listing.model = product['model']
            amz_listing.upc = product['upc']
            amz_listing.quantity = product['quantity']
            amz_listing.salesrank = product['salesrank']
            amz_listing.updated = arrow.utcnow().datetime

            # Create a new category if necessary
            pcid = product['productcategoryid']
            if pcid is not None:
                category = self.dbsession.query(AmazonCategory).filter_by(product_category_id=pcid).first()
                if category is None:
                    category = AmazonCategory(name=pcid, product_category_id=pcid)
                    self.dbsession.add(category)
                amz_listing.category = category

            # Create a link between the two listings
            link = LinkedProducts()
            link.brand_match = brand_match(amz_listing, vnd_listing)
            link.model_match = model_match(amz_listing, vnd_listing)
            link.title_match = title_match(amz_listing, vnd_listing)
            link.confidence = sum([link.brand_match * 2, link.model_match * 2, link.title_match]) / 5

            # Add the link if it meets the criteria, or if no criteria were provided
            add_cond_1 = 'linkif' in params \
                            and 'conf' in params['linkif'] \
                            and link.confidence >= float(params['linkif']['conf'])
            add_cond_2 = 'linkif' not in params

            if add_cond_1 or add_cond_2:
                self.dbsession.flush()
                link.amz_listing_id = amz_listing.id
                link.vnd_listing_id = vnd_listing.id
                self.dbsession.merge(link)

                # Schedule a price lookup if conditions are met
                if 'priceif' in params \
                        and 'salesrank' in params['priceif'] \
                        and amz_listing.salesrank \
                        and amz_listing.salesrank <= int(params['priceif']['salesrank']):
                    # Build the query string to pass on to GetMyFeesEstimate
                    fee_params = params.get('feesif')

                    price_op = Operation(priority=op.priority, listing_id=amz_listing.id)
                    price_op.append('GetCompetitivePricingForASIN', {'fallback': True, 'feesif': fee_params})
                    self.dbsession.add(price_op)

        op.message = '%s links found.' % len(vnd_listing.amz_links)
        self.dbsession.commit()

    def GetCompetitivePricingForASIN(self, op):
        """Get the buy box pricing for an Amazon product. Also updates the sales rank.

        Parameters:     fallback=   If no pricing is returned, generate a call to GetLowestOfferListingsForASIN

                        feesif: Get FBA fees if the conditions are met.
                            priceratio=     The ratio of the listing price to any vendor price is at least priceratio

        """
        amz_listing = self.dbsession.query(AmazonListing).filter_by(id=op.listing_id).first()
        params = op.params

        r = self.mwsapi.GetCompetitivePricingForASIN(priority=op.priority, MarketplaceId=self.mwsapi.api.market_id(),
                                                     ASINList=[amz_listing.sku])
        if self.is_error_response(r, op):
            return

        parser = GetCompetitivePricingForASINParser(r.content.decode())

        info = next(parser.get_product_info())
        if info is None:
            op.message = 'No valid response.'
            op.error = True
            self.dbsession.commit()
            return

        amz_listing.salesrank = info['salesrank']
        amz_listing.offers = info.get('newlistings', 0)

        if info['price'] is not None:
            amz_listing.price = info['price']

            if 'feesif' in params and 'priceratio' in params['feesif']:
                maxratio = 0
                for link in self.dbsession.query(LinkedProducts).filter_by(amz_listing_id=amz_listing.id):
                    maxratio = max(amz_listing.unit_price / link.vnd_listing.unit_price, maxratio)

                if maxratio >= float(params['feesif']['priceratio']):
                    op.insert(op.current_index + 1,
                              'GetMyFeesEstimate',
                              {'price': '%.2f' % info['price']})
        else:
            if 'fallback' in params and params['fallback'] == True:
                fee_params = params.get('feesif')
                op.insert(op.current_index + 1, 'GetLowestOfferListingsForASIN', {'feesif': fee_params})
                op.message = 'Falling back to GetLowestOfferListingsForASIN...'

        self.dbsession.commit()

    def GetLowestOfferListingsForASIN(self, op):
        """Get lowest available pricing from Amazon.

        Parameters:     feesif: Get FBA fees if the conditions are met.
                            priceratio=     The ratio of the listing price to any vendor price is at least priceratio
        """

        amz_listing = self.dbsession.query(AmazonListing).filter_by(id=op.listing_id).first()
        params = op.params

        r = self.mwsapi.GetLowestOfferListingsForASIN(priority=op.priority, MarketplaceId=self.mwsapi.api.market_id(),
                                                      ASINList=[amz_listing.sku], ItemCondition='New')
        if self.is_error_response(r, op):
            return

        parser = GetLowestOfferListingsForAsinParser(r.content.decode())

        price = next(parser.get_prices())
        if price is None:
            op.error = True
            op.message = 'No prices returned.'
            self.dbsession.commit()
            return

        amz_listing.price = price['price']

        if amz_listing.price is not None:
            if 'feesif' in params and 'priceratio' in params['feesif']:
                maxratio = 0
                for link in self.dbsession.query(LinkedProducts).filter_by(amz_listing_id=amz_listing.id):
                    maxratio = max(amz_listing.unit_price / link.vnd_listing.unit_price, maxratio)

                if maxratio >= float(params['feesif']['priceratio']):
                    op.insert(op.current_index + 1,
                              'GetMyFeesEstimate',
                              {'price': '%.2f' % price['price']})
                    op.message = 'Getting FBA fees...'

        self.dbsession.commit()

    def GetMyFeesEstimate(self, op):
        """Get an FBA fees estimate for the given listing.

        Parameters:     price=  Update all price points at the given price. If not provided, update all price points
                                at the current listing price. Create a new price point if none exist.

                        fees=   Set the fees to the given value. If not provided, request fees from Amazon."""

        amz_listing = self.dbsession.query(AmazonListing).filter_by(id=op.listing_id).first()
        params = op.params

        if 'price' in params:
            price = float(params['price'])
        else:
            price = amz_listing.price

        if 'fees' in params:
            fba_fees = float(params['fees'])
        else:
            feerequest = {'MarketplaceId': self.mwsapi.api.market_id(),
                          'IdType': 'ASIN',
                          'IdValue': amz_listing.sku,
                          'Identifier': 'prwlr',
                          'IsAmazonFulfilled': 'true',
                          'PriceToEstimateFees.ListingPrice.CurrencyCode': 'USD',
                          'PriceToEstimateFees.ListingPrice.Amount': price}

            r = self.mwsapi.GetMyFeesEstimate(FeesEstimateRequestList=[feerequest])
            if self.is_error_response(r, op):
                return

            parser = GetMyFeesEstimateParser(r.content.decode())
            fees = next(parser.get_fees())
            if fees is None or fees['status'] != 'Success':
                op.error = True
                op.message = fees['errormessage']
                self.dbsession.commit()
                return
            else:
                fba_fees = fees['amount']

        # Get all the price points this fee request applies to
        price_point = None
        for price_point in self.dbsession.query(AmzPriceAndFees).filter_by(amz_listing_id=amz_listing.id, price=price):
            price_point.fba = fba_fees
        if price_point is None:
            price_point = AmzPriceAndFees(amz_listing=amz_listing, price=price, fba=fba_fees)
            self.dbsession.add(price_point)

        self.dbsession.commit()


    def AddToProductHistory(self, op):
        """Push the current state of an Amazon product onto the AmzProductHistory table.

        Parameters:     repeat=min      Schedule an update of all product information and another AddToProductHistory
                                        operation for a set number of minutes after this one completes."""

        amz_listing = self.dbsession.query(AmazonListing).filter_by(id=op.listing_id).first()
        params = op.params

        history = AmzProductHistory(amz_listing_id=amz_listing.id,
                                    price=amz_listing.price,
                                    salesrank=amz_listing.salesrank,
                                    hasprime=amz_listing.hasprime,
                                    merchant_id=amz_listing.merchant_id,
                                    offers=amz_listing.offers,
                                    timestamp=amz_listing.updated)

        self.dbsession.add(history)
