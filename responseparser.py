import re
import itertools

from lxml import etree

from database import *
import dbhelpers


class QuantityGuesser:

    # Match 'container' words, abbreviations and plurals. Ex: matches 'pk', 'pks', 'pack', or 'packs'
    _re_containers = r'(?:(?<![a-z])(?:package|pack|pk|case|cs|set|st|boxe|box|bx|count|ct|carton|bag|bg|roll|rl|sleeve|quantity)s?(?![a-z]))'

    # Match 'multiplier' words, abbreviations, and plurals. Ex: matches 'dz', 'dzs', 'dozen', or 'dozens'
    _re_multipliers = r'(?:(?<![a-z])(?P<mult>ea|each|unit|pc|piece|pr|pair|dz|doz|dozen)s?(?![a-z]))'

    # Match numbers given in plain form, comma-separated, and/or enclosed in parentheses. Ex: (1,000)
    # Now recognizes fractions: 1/2, 1,000/2, (1/2), etc
    _re_numbers = r'\(?(?P<num>\d[\d,]*(?:/\d[\d,]*)?)\)?'

    _mult_lookup = {'ea': 1, 'each': 1,
                    'unit': 1,
                    'pc': 1, 'piece': 1,
                    'pr': 2, 'pair': 2,
                    'dz': 12, 'doz': 12, 'dozen': 12}

    def __init__(self, pair_value=2):
        self._mult_lookup['pr'] = pair_value
        self._mult_lookup['pair'] = pair_value

    def _type1_matches(self, string):
        """Matches the form: (container) of/consists of (number)(multiplier)
        Ex: "set of 6" "box of 2 doz" "set consists of 6 pieces"
        """
        r = re.compile(r'{container}(?:\s+consists?)?(?:\s+of)\s*{number}\s*{multiplier}?' \
                       .format(container=self._re_containers, number=self._re_numbers, multiplier=self._re_multipliers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            num = eval(match.group('num').replace(',', ''))
            mult = self._mult_lookup.get(match.group('mult'), 1)
            yield num * mult

    def _type2_matches(self, string):
        """Matches the form: (quantity) (per) (container)
        Ex: "12 per set" "1dz/case" "12-pack"
        """
        r = re.compile(r'{number}\s*{multiplier}?(?:\s*[a-z]+)?\s*(?:per|/|-| )?\s*{container}' \
                       .format(number=self._re_numbers, multiplier=self._re_multipliers, container=self._re_containers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            num = eval(match.group('num').replace(',', ''))
            mult = self._mult_lookup.get(match.group('mult'), 1)
            yield num * mult

    def _type3_matches(self, string):
        """Matches the form: (quantity)(multiplier)
        Ex: "1 dozen" "2 pair" "6 each"
        """
        r = re.compile(r'{number}\s*[-/]?\s*{multiplier}(?![a-z])' \
                       .format(number=self._re_numbers, multiplier=self._re_multipliers),
                       re.IGNORECASE)

        for match in r.finditer(string):
            num = eval(match.group('num').replace(',', ''))
            mult = self._mult_lookup.get(match.group('mult'), 1)
            yield num * mult

    def _type4_matches(self, string):






# Attempt to translate a 'human-friendly' quantity to a number
def read_quantity(string, pairs_singular=False):
    string = string.lower()

    # Match 'container' words, abbreviations and plurals. Ex: matches 'pk', 'pks', 'pack', or 'packs'
    containers = r'(?:(?<![a-z])(?:package|pack|pk|case|cs|set|st|boxe|box|bx|count|ct|carton|bag|bg|roll|rl|sleeve|quantity)s?(?![a-z]))'

    # Match 'multiplier' words, abbreviations, and plurals. Ex: matches 'dz', 'dzs', 'dozen', or 'dozens'
    multipliers = r'(?:(?<![a-z])(?P<mult>ea|each|unit|pc|piece|pr|pair|dz|doz|dozen)s?(?![a-z]))'

    # Match numbers given in plain form, comma-separated, and/or enclosed in parentheses. Ex: (1,000)
    # Now recognizes fractions: 1/2, 1,000/2, (1/2), etc
    numbers = r'\(?(?P<num>\d[\d,]*(?:/\d[\d,]*)?)\)?'

    # Sometimes it's useful to consider a 'pair' as one item. Like a pair of shoes.
    pair_value = 1 if pairs_singular else 2
    mult_lookup = {'ea': 1, 'each': 1,
                   'unit': 1,
                   'pc': 1, 'piece': 1,
                   'pr': pair_value, 'pair': pair_value,
                   'dz': 12, 'doz': 12, 'dozen': 12}

    # Match "(number)(container) of/consists of (quantity)" phrases
    r1 = re.compile(r'{container}(?:\s+consists?)?(?:\s+of)\s*{number}\s*{multiplier}?'\
                    .format(container=containers, number=numbers, multiplier=multipliers),
                    re.IGNORECASE)

    # Match "(quantity) (per) (container)" phrases
    r2 = re.compile(r'{number}\s*{multiplier}?(?:\s*[a-z]+)?\s*(?:per|/|-| )?\s*{container}'\
                    .format(number=numbers, multiplier=multipliers, container=containers),
                    re.IGNORECASE)

    # Match "(quantity)(multiplier)" as in '2 dozen' or '6 each'
    r3 = re.compile(r'{number}\s*[-/]?\s*{multiplier}(?![a-z])'\
                    .format(number=numbers, multiplier=multipliers),
                    re.IGNORECASE)

    # Match "(number) (containers) of (number)"
    r4 = re.compile()



    quants = []
    matches = itertools.chain(r1.finditer(string),
                              r2.finditer(string),
                              r3.finditer(string),
                              r4.finditer(string))
    for match in matches:
        num = eval(match.group('num').replace(',', ''))
        mult = mult_lookup.get(match.group('mult'), 1)
        quants.append(num * mult)

    if not quants:
        return None

    # Calculate the modes (plural) of the quantities, and choose the largest one
    most = max(list(map(quants.count, quants)))
    modes = list(set(filter(lambda x: quants.count(x) == most, quants)))

    if modes:
        return max(modes)
    else:
        return max(quants)


class ParseError(Exception):
    pass


class XmlResponseElement:
    """Base class for an XML response element."""

    def __init__(self, tag=None):
        self._tag = tag

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    def xpath_get(self, path, dtype=str, default=None):
        """Use XPath to get values under the current tag. Return a value of type dtype, or the default value."""
        items = self._tag.xpath(path)
        try:
            return dtype(items[0].text)
        except (TypeError, IndexError):
            return default

    def xpath_get_all(self, path, dtype=str, default=None):
        """Return a list of all values with the given path."""
        items = self._tag.xpath(path)
        response = []
        for item in items:
            try:
                response.append(dtype(item.text))
            except TypeError:
                response.append(default)

        return response


class AmzResponseParser(XmlResponseElement):
    """Base class for parsing XML responses from the Amazon MWS or Product Advertising APIs."""

    # Regexes for removing namespaces from the XML - makes it easier to parse
    re_ns_decl = re.compile(r' xmlns(:\w*)?="[^"]*"', re.IGNORECASE)
    re_ns_open = re.compile(r'<\w+:')
    re_ns_close = re.compile(r'/\w+:')

    def __init__(self, xml):
        super(AmzResponseParser, self).__init__()

        try:
            tree = etree.fromstring(self._remove_namespace(xml))
        except Exception as e:
            raise ParseError(repr(e))

        self._tag = tree

    def _remove_namespace(self, xml):
        """Remove all traces of namespaces from an XML string."""
        response = self.re_ns_decl.sub('', xml)          # Remove namespace declarations
        response = self.re_ns_open.sub('<', response)    # Remove namespaces in opening tags
        response = self.re_ns_close.sub('/', response)   # Remove namespaces in closing tags
        return response


class ProductParser(XmlResponseElement):
    """Provides a normalized way to access information in a 'Product' or 'Item' tag."""

    def update(self, amz_listing):
        """Update the given Amazon listing with the information in this parser."""
        amz_listing.sku = self.asin
        amz_listing.title = self.title
        amz_listing.brand = self.brand
        amz_listing.model = self.model
        amz_listing.upc = self.upc
        amz_listing.quantity = self.quantity
        amz_listing.url = self.url
        amz_listing.salesrank = self.salesrank
        amz_listing.offers = self.offers
        amz_listing.hasprime = self.prime

        # Only update price if price information is provided
        if self._tag.xpath('.//Offers'):
            amz_listing.price = self.price

    @property
    def asin(self):
        return self.xpath_get('.//ASIN')

    @property
    def brand(self):
        return self.xpath_get('.//Brand') \
            or self.xpath_get('.//Manufacturer') \
            or self.xpath_get('.//Label') \
            or self.xpath_get('.//Publisher') \
            or self.xpath_get('.//Studio')

    @property
    def model(self):
        return self.xpath_get('.//Model') \
            or self.xpath_get('.//PartNumber') \
            or self.xpath_get('.//MPN')

    @property
    def title(self):
        return self.xpath_get('.//Title')

    @property
    def salesrank(self):
        return self.xpath_get('.//SalesRank/Rank', dtype=int) \
            or self.xpath_get('.//SalesRank', dtype=int)

    @property
    def price(self):
        price = self.xpath_get('.//OfferListing/Price/Amount', dtype=int)
        if price:
            price /= 100

        return price

    @property
    def upc(self):
        return self.xpath_get('.//UPC')

    @property
    def quantity(self):
        quantities = []

        # Check it quantity is specified in the product data
        quantities.append(max(self.xpath_get('.//NumberOfItems', dtype=int, default=1),
                              self.xpath_get('.//PackageQuantity', dtype=int, default=1)))

        # Check the title and 'features' section
        features = [tag.text for tag in self._tag.iterdescendants('Feature')]
        features.append(self.title)

        return max(*quantities, read_quantity(' '.join(features)) or 1)

    @property
    def offers(self):
        return self.xpath_get('.//OfferSummary/TotalNew', dtype=int)

    @property
    def merchant(self):
        return self.xpath_get('.//Offer/Merchant/Name')

    @property
    def prime(self):
        return bool(self.xpath_get('.//IsEligibleForPrime', dtype=int, default=0))

    @property
    def url(self):
        return "http://www.amazon.com/dp/%s" % self.asin

    @property
    def product_category_id(self):
        return self.xpath_get('.//ProductCategoryId')

    @property
    def product_group(self):
        return self.xpath_get('.//ProductGroup')


class ListMatchingProductsParser(AmzResponseParser):
    """Parses the response from ListMatchingProducts."""

    @property
    def products(self):
        """Iterate through the 'Product' response tags."""
        for tag in self._tag.iterdescendants('Product'):
            yield ProductParser(tag)


class MWSResponseParser:
    """Base class for the response parsers. Provides methods for parsing XML."""

    # Regexes for removing namespaces from the XML - makes it easier to parse
    re_ns_decl = re.compile(r' xmlns(:\w*)?="[^"]*"', re.IGNORECASE)
    re_ns_open = re.compile(r'<\w+:')
    re_ns_close = re.compile(r'/\w+:')

    def __init__(self, xml):
        try:
            self.tree = etree.fromstring(self._remove_namespace(xml))
        except Exception as e:
            raise ParseError(repr(e))

    def _remove_namespace(self, xml):
        """Remove all traces of namespaces from an XML string."""
        response = self.re_ns_decl.sub('', xml)          # Remove namespace declarations
        response = self.re_ns_open.sub('<', response)    # Remove namespaces in opening tags
        response = self.re_ns_close.sub('/', response)   # Remove namespaces in closing tags
        return response

    def xpath_get(self, path, root=None, dtype=str, default=None):
        """Use XPath to get values under a root node, including type casting and a default value."""
        root = root if root is not None else self.tree
        items = root.xpath(path)
        try:
            return dtype(items[0].text)
        except (TypeError, IndexError):
            return default


class ErrorResponseParser(AmzResponseParser):
    """Provides information from an error response."""

    @property
    def type(self):
        return self.xpath_get('.//Error/Type')

    @property
    def code(self):
        return self.xpath_get('.//Error/Code')

    @property
    def message(self):
        return self.xpath_get('.//Error/Message')


# class ListMatchingProductsParser(MWSResponseParser):
#     """Parses a response from ListMatchingProducts."""
#
#     def products(self):
#
#         session = Session()
#
#         for tag in self.tree.iterdescendants('Product'):
#             asin = self.xpath_get('.//MarketplaceASIN/ASIN', tag)
#             product = dbhelpers.get_or_create(session, AmazonListing, sku=asin)
#
#             product.brand = self.xpath_get('.//Brand', tag) \
#                             or self.xpath_get('.//Manufacturer', tag) \
#                             or self.xpath_get('.//Label')
#
#             product.model = self.xpath_get('.//Model', tag) \
#                             or self.xpath_get('.//PartNumber', tag)
#
#             product.title = self.xpath_get('.//Title', tag)
#
#             product.salesrank = self.xpath_get('.//SalesRank/Rank', tag, int)
#
#             # Try to determine product category
#             category_id = self.xpath_get('.//ProductCategoryId', tag)
#             product_group = self.xpath_get('.//ProductGroup', tag)
#
#             product.category = dbhelpers.get_or_create_category(session, category_id, product_group)
#
#             # Try to determine listing quantity
#             product.quantity = max(self.xpath_get('.//NumberOfItems', tag, int, default=1),
#                                    self.xpath_get('.//PackageQuantity', tag, int, default=1))
#
#             yield product



class GetCompetitivePricingForASINParser(MWSResponseParser):

    def get_product_info(self):

        for tag in self.tree.iterdescendants('Product'):
            product = {}
            product['asin'] = self.xpath_get('.//ASIN', tag)

            for comp_price in tag.iterdescendants('CompetitivePrice'):
                if comp_price.attrib['condition'] == 'New':
                    product['landed price'] = self.xpath_get('.//LandedPrice/Amount', tag, float)
                    product['list price'] = self.xpath_get('.//ListingPrice/Amount', tag, float)
                    product['price'] = product['landed price'] or product['list price']
            else:
                product['landed price'] = product.get('landed', None)
                product['list price'] = product.get('listing', None)
                product['price'] = product.get('price', None)

            product['productcategoryid'] = self.xpath_get('.//SalesRank/ProductCategoryId')
            product['salesrank'] = self.xpath_get('.//SalesRank/Rank', tag, int)

            product['newlistings'] = 0
            for count in tag.iterdescendants('OfferListingCount'):
                if count.attrib['condition'] == 'New':
                    product['newlistings'] = int(count.text)

            yield product


class GetLowestOfferListingsForASINParser(MWSResponseParser):

    def get_product_info(self):

        for result_tag in self.tree.iterdescendants('GetLowestOfferListingsForASINResult'):
            result = {}

            if result_tag.attrib['status'] != 'Success':
                result['error'] = True
                result['asin'] = result_tag.attrib['ASIN']
                result['type'] = self.xpath_get('.//Type', result_tag)
                result['code'] = self.xpath_get('.//Code', result_tag)
                result['message'] = self.xpath_get('.//Message', result_tag)
            else:
                result['error'] = False
                result['asin'] = self.xpath_get('.//ASIN', result_tag)
                result['price'] = self.xpath_get('.//LandedPrice/Amount', result_tag, float) \
                                  or self.xpath_get('.//ListingPrice/Amount', result_tag, float)

                channel = self.xpath_get('.//FulfillmentChannel', result_tag)
                if channel == 'Amazon':
                    result['prime'] = True
                else:
                    result['prime'] = False

            yield result


class GetMyFeesEstimateParser(MWSResponseParser):

    def get_fees(self):

        for tag in self.tree.iterdescendants('FeesEstimateResult'):
            result = {}
            result['status'] = self.xpath_get('.//Status', tag)
            result['asin'] = self.xpath_get('.//IdValue', tag)
            result['amount'] = self.xpath_get('.//TotalFeesEstimate/Amount', tag, float)
            result['errortype'] = self.xpath_get('.//Error/Type', tag)
            result['errorcode'] = self.xpath_get('.//Error/Code', tag)
            result['errormessage'] = self.xpath_get('.//Error/Message', tag)

            yield result


class ItemLookupParser(AmzResponseParser):

    @property
    def product(self):
        items = self._tag.xpath('//Item')
        if items:
            return ProductParser(items[0])
        else:
            return None


# class ItemLookupParser(MWSResponseParser):
#
#     def get_info(self):
#         info = {}
#
#         info['asin'] = self.xpath_get('.//ASIN')
#         info['url'] = self.xpath_get('.//DetailPageURL')
#         info['salesrank'] = self.xpath_get('.//SalesRank', dtype=int)
#         info['upc'] = self.xpath_get('.//UPC')
#
#         info['offers'] = self.xpath_get('.//OfferSummary/TotalNew', dtype=int)
#         info['merchant'] = self.xpath_get('.//Merchant/Name')
#         info['price'] = self.xpath_get('.//Price/Amount', dtype=int)
#
#         if info['price']:
#             info['price'] /= 100
#
#         info['prime'] = bool(self.xpath_get('.//IsEligibleForPrime', dtype=int, default=0))
#
#         return info




testxml = """<ListMatchingProductsResponse xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01">
  <ListMatchingProductsResult>
    <Products xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01" xmlns:ns2="http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd">
      <Product>
        <Identifiers>
          <MarketplaceASIN>
            <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
            <ASIN>B000V4Q9E6</ASIN>
          </MarketplaceASIN>
        </Identifiers>
        <AttributeSets>
          <ns2:ItemAttributes xml:lang="en-US">
            <ns2:Brand>Ansell</ns2:Brand>
            <ns2:Color>Black</ns2:Color>
            <ns2:Feature>Polyurethane palm coating provides maximum tactile sensitivity in the finger area for exceptional feel</ns2:Feature>
            <ns2:Feature>excellent fit and performance to maintain high productivity</ns2:Feature>
            <ns2:Feature>Ultra-cool stretch nylon liner provides barehand dexterity</ns2:Feature>
            <ns2:IsAutographed>false</ns2:IsAutographed>
            <ns2:IsMemorabilia>false</ns2:IsMemorabilia>
            <ns2:Label>Ansell</ns2:Label>
            <ns2:Manufacturer>Ansell</ns2:Manufacturer>
            <ns2:MaterialType>Polyurethane</ns2:MaterialType>
            <ns2:PackageDimensions>
              <ns2:Height Units="inches">4.50</ns2:Height>
              <ns2:Length Units="inches">10.50</ns2:Length>
              <ns2:Width Units="inches">5.40</ns2:Width>
              <ns2:Weight Units="pounds">0.02</ns2:Weight>
            </ns2:PackageDimensions>
            <ns2:PackageQuantity>1</ns2:PackageQuantity>
            <ns2:PartNumber>BCBI9685</ns2:PartNumber>
            <ns2:ProductGroup>BISS</ns2:ProductGroup>
            <ns2:ProductTypeName>LAB_SUPPLY</ns2:ProductTypeName>
            <ns2:Publisher>Ansell</ns2:Publisher>
            <ns2:SmallImage>
              <ns2:URL>http://ecx.images-amazon.com/images/I/31sM6gGqJEL._SL75_.jpg</ns2:URL>
              <ns2:Height Units="pixels">75</ns2:Height>
              <ns2:Width Units="pixels">75</ns2:Width>
            </ns2:SmallImage>
            <ns2:Studio>Ansell</ns2:Studio>
            <ns2:Title>Ansell Hyflex, Size 9 Black (pack of 12)</ns2:Title>
          </ns2:ItemAttributes>
        </AttributeSets>
        <Relationships/>
        <SalesRankings>
          <SalesRank>
            <ProductCategoryId>biss_display_on_website</ProductCategoryId>
            <Rank>7321</Rank>
          </SalesRank>
          <SalesRank>
            <ProductCategoryId>553608</ProductCategoryId>
            <Rank>344</Rank>
          </SalesRank>
        </SalesRankings>
      </Product>
      <Product>
        <Identifiers>
          <MarketplaceASIN>
            <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
            <ASIN>B01GGNW6K6</ASIN>
          </MarketplaceASIN>
        </Identifiers>
        <AttributeSets>
          <ns2:ItemAttributes xml:lang="en-US">
            <ns2:Binding>Kitchen</ns2:Binding>
            <ns2:Brand>Ansell</ns2:Brand>
            <ns2:Color>White</ns2:Color>
            <ns2:Feature>Use with medical supplies or cleaning tools</ns2:Feature>
            <ns2:Feature>Offers excellent dexterity for food service, parts handling, cleanup, janitorial and more</ns2:Feature>
            <ns2:Feature>High-quality exam grade gloves</ns2:Feature>
            <ns2:Feature>Vinyl gloves</ns2:Feature>
            <ns2:Feature>Latex-free gloves</ns2:Feature>
            <ns2:ItemDimensions>
              <ns2:Height Units="inches">7.50</ns2:Height>
              <ns2:Length Units="inches">7.50</ns2:Length>
              <ns2:Width Units="inches">6.00</ns2:Width>
            </ns2:ItemDimensions>
            <ns2:IsAutographed>false</ns2:IsAutographed>
            <ns2:Label>(Ansell)</ns2:Label>
            <ns2:Manufacturer>(Ansell)</ns2:Manufacturer>
            <ns2:MaterialType>vinyl</ns2:MaterialType>
            <ns2:Model>15-0191</ns2:Model>
            <ns2:PackageDimensions>
              <ns2:Height Units="inches">3.00</ns2:Height>
              <ns2:Length Units="inches">7.50</ns2:Length>
              <ns2:Width Units="inches">6.00</ns2:Width>
            </ns2:PackageDimensions>
            <ns2:ProductGroup>Home</ns2:ProductGroup>
            <ns2:ProductTypeName>HOME</ns2:ProductTypeName>
            <ns2:Publisher>(Ansell)</ns2:Publisher>
            <ns2:SmallImage>
              <ns2:URL>http://ecx.images-amazon.com/images/I/51goNufR5%2BL._SL75_.jpg</ns2:URL>
              <ns2:Height Units="pixels">75</ns2:Height>
              <ns2:Width Units="pixels">75</ns2:Width>
            </ns2:SmallImage>
            <ns2:Studio>(Ansell)</ns2:Studio>
            <ns2:Title>Ansell Vinyl Touch Gloves, 100ct</ns2:Title>
          </ns2:ItemAttributes>
        </AttributeSets>
        <Relationships/>
        <SalesRankings>
          <SalesRank>
            <ProductCategoryId>home_garden_display_on_website</ProductCategoryId>
            <Rank>653827</Rank>
          </SalesRank>
          <SalesRank>
            <ProductCategoryId>15751151</ProductCategoryId>
            <Rank>319</Rank>
          </SalesRank>
        </SalesRankings>
      </Product>
      <Product>
        <Identifiers>
          <MarketplaceASIN>
            <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
            <ASIN>B009EAMGQS</ASIN>
          </MarketplaceASIN>
        </Identifiers>
        <AttributeSets>
          <ns2:ItemAttributes xml:lang="en-US">
            <ns2:Binding>Misc.</ns2:Binding>
            <ns2:Brand>Ansell</ns2:Brand>
            <ns2:Feature>Multipurpose glove protects hands from punctures, cuts, and abrasions during  landscaping, flooring, roofing, and other general maintenance tasks</ns2:Feature>
            <ns2:Feature>Reinforced ridges for flexibility and dexterity, to resist wear, and to help protect palm and index finger from abrasions</ns2:Feature>
            <ns2:Feature>DuPont Kevlar fiber provides cut protection</ns2:Feature>
            <ns2:Feature>Foam nitrile coating on palm and fingers to facilitate gripping objects under wet or dry environmental conditions</ns2:Feature>
            <ns2:Feature>Meets ANSI standards for cut, abrasion, and puncture resistance</ns2:Feature>
            <ns2:IsAutographed>false</ns2:IsAutographed>
            <ns2:IsMemorabilia>false</ns2:IsMemorabilia>
            <ns2:Label>Ansell</ns2:Label>
            <ns2:ListPrice>
              <ns2:Amount>181.63</ns2:Amount>
              <ns2:CurrencyCode>USD</ns2:CurrencyCode>
            </ns2:ListPrice>
            <ns2:Manufacturer>Ansell</ns2:Manufacturer>
            <ns2:MaterialType>Nitrile</ns2:MaterialType>
            <ns2:NumberOfItems>1</ns2:NumberOfItems>
            <ns2:PackageDimensions>
              <ns2:Height Units="inches">0.60</ns2:Height>
              <ns2:Length Units="inches">9.30</ns2:Length>
              <ns2:Width Units="inches">4.20</ns2:Width>
              <ns2:Weight Units="pounds">0.15</ns2:Weight>
            </ns2:PackageDimensions>
            <ns2:PackageQuantity>1</ns2:PackageQuantity>
            <ns2:PartNumber>111810</ns2:PartNumber>
            <ns2:ProductGroup>BISS Basic</ns2:ProductGroup>
            <ns2:ProductTypeName>SAFETY_SUPPLY</ns2:ProductTypeName>
            <ns2:Publisher>Ansell</ns2:Publisher>
            <ns2:Size>Small</ns2:Size>
            <ns2:SmallImage>
              <ns2:URL>http://ecx.images-amazon.com/images/I/41dVK5CatRL._SL75_.jpg</ns2:URL>
              <ns2:Height Units="pixels">46</ns2:Height>
              <ns2:Width Units="pixels">75</ns2:Width>
            </ns2:SmallImage>
            <ns2:Studio>Ansell</ns2:Studio>
            <ns2:Title>Ansell ActivArmr 97-008 Multipurpose Medium Duty Gloves, Small (1 Pair)</ns2:Title>
          </ns2:ItemAttributes>
        </AttributeSets>
        <Relationships>
          <VariationParent>
            <Identifiers>
              <MarketplaceASIN>
                <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
                <ASIN>B00PUC70YW</ASIN>
              </MarketplaceASIN>
            </Identifiers>
          </VariationParent>
        </Relationships>
        <SalesRankings>
          <SalesRank>
            <ProductCategoryId>biss_basic_display_on_website</ProductCategoryId>
            <Rank>4816</Rank>
          </SalesRank>
          <SalesRank>
            <ProductCategoryId>553608</ProductCategoryId>
            <Rank>2473</Rank>
          </SalesRank>
        </SalesRankings>
      </Product>
    </Products>
  </ListMatchingProductsResult>
  <ResponseMetadata>
    <RequestId>fbbb2fac-c03b-468c-b6e5-3eb6fb767e3b</RequestId>
  </ResponseMetadata>
</ListMatchingProductsResponse>
"""

throttled_xml = """<?xml version="1.0"?>
<ErrorResponse xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01">
  <Error>
    <Type>
</Type>
    <Code>RequestThrottled</Code>
    <Message>Request is throttled</Message>
  </Error>
  <RequestID>b4cfc711-1a54-4df7-904b-af38b4644638</RequestID>
</ErrorResponse>"""

getcompetitivexml = """<?xml version="1.0"?>
<GetCompetitivePricingForASINResponse xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01">
<GetCompetitivePricingForASINResult ASIN="B013YTG2VY" status="Success">
  <Product xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01" xmlns:ns2="http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd">
    <Identifiers>
      <MarketplaceASIN>
        <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
        <ASIN>B013YTG2VY</ASIN>
      </MarketplaceASIN>
    </Identifiers>
    <CompetitivePricing>
      <CompetitivePrices>
        <CompetitivePrice belongsToRequester="false" condition="New" subcondition="New">
          <CompetitivePriceId>1</CompetitivePriceId>
          <Price>
            <LandedPrice>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>32.99</Amount>
            </LandedPrice>
            <ListingPrice>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>32.99</Amount>
            </ListingPrice>
            <Shipping>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>0.00</Amount>
            </Shipping>
          </Price>
        </CompetitivePrice>
      </CompetitivePrices>
      <NumberOfOfferListings>
        <OfferListingCount condition="New">3</OfferListingCount>
        <OfferListingCount condition="Any">3</OfferListingCount>
      </NumberOfOfferListings>
    </CompetitivePricing>
    <SalesRankings>
      <SalesRank>
        <ProductCategoryId>home_improvement_display_on_website</ProductCategoryId>
        <Rank>20325</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>2314207011</ProductCategoryId>
        <Rank>899</Rank>
      </SalesRank>
    </SalesRankings>
  </Product>
</GetCompetitivePricingForASINResult>
<GetCompetitivePricingForASINResult ASIN="B004ZH4GKE" status="Success">
  <Product xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01" xmlns:ns2="http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd">
    <Identifiers>
      <MarketplaceASIN>
        <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
        <ASIN>B004ZH4GKE</ASIN>
      </MarketplaceASIN>
    </Identifiers>
    <CompetitivePricing>
      <CompetitivePrices>
        <CompetitivePrice belongsToRequester="true" condition="New" subcondition="New">
          <CompetitivePriceId>1</CompetitivePriceId>
          <Price>
            <LandedPrice>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>32.99</Amount>
            </LandedPrice>
            <ListingPrice>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>32.99</Amount>
            </ListingPrice>
            <Shipping>
              <CurrencyCode>USD</CurrencyCode>
              <Amount>0.00</Amount>
            </Shipping>
          </Price>
        </CompetitivePrice>
      </CompetitivePrices>
      <NumberOfOfferListings>
        <OfferListingCount condition="New">2</OfferListingCount>
        <OfferListingCount condition="Any">2</OfferListingCount>
      </NumberOfOfferListings>
    </CompetitivePricing>
    <SalesRankings>
      <SalesRank>
        <ProductCategoryId>biss_basic_display_on_website</ProductCategoryId>
        <Rank>2697</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>7491822011</ProductCategoryId>
        <Rank>20</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>7491820011</ProductCategoryId>
        <Rank>23</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>393303011</ProductCategoryId>
        <Rank>88</Rank>
      </SalesRank>
    </SalesRankings>
  </Product>
</GetCompetitivePricingForASINResult>
<GetCompetitivePricingForASINResult ASIN="GKJDLKJ30984" status="ClientError">
  <Error>
    <Type>Sender</Type>
    <Code>InvalidParameterValue</Code>
    <Message>ASIN GKJDLKJ30984 is not valid for marketplace ATVPDKIKX0DER</Message>
  </Error>
</GetCompetitivePricingForASINResult>
<ResponseMetadata>
  <RequestId>1079189b-f4ff-4d72-9bc5-f4c0d696e30b</RequestId>
</ResponseMetadata>
</GetCompetitivePricingForASINResponse>"""

xml3 = """<?xml version="1.0"?>
<GetCompetitivePricingForASINResponse xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01">
<GetCompetitivePricingForASINResult ASIN="B001V9LQLG" status="Success">
  <Product xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01" xmlns:ns2="http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd">
    <Identifiers>
      <MarketplaceASIN>
        <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
        <ASIN>B001V9LQLG</ASIN>
      </MarketplaceASIN>
    </Identifiers>
    <CompetitivePricing>
      <CompetitivePrices/>
      <NumberOfOfferListings>
        <OfferListingCount condition="New">1</OfferListingCount>
        <OfferListingCount condition="Any">1</OfferListingCount>
      </NumberOfOfferListings>
    </CompetitivePricing>
    <SalesRankings>
      <SalesRank>
        <ProductCategoryId>office_product_display_on_website</ProductCategoryId>
        <Rank>80307</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>8090706011</ProductCategoryId>
        <Rank>569</Rank>
      </SalesRank>
    </SalesRankings>
  </Product>
</GetCompetitivePricingForASINResult>
<ResponseMetadata>
  <RequestId>97fcb77a-9c70-4379-baab-ce47b719f26f</RequestId>
</ResponseMetadata>
</GetCompetitivePricingForASINResponse>"""

xml4 = """<?xml version="1.0"?>
<GetCompetitivePricingForASINResponse xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01">
<GetCompetitivePricingForASINResult ASIN="B01BF6DQK8" status="Success">
  <Product xmlns="http://mws.amazonservices.com/schema/Products/2011-10-01" xmlns:ns2="http://mws.amazonservices.com/schema/Products/2011-10-01/default.xsd">
    <Identifiers>
      <MarketplaceASIN>
        <MarketplaceId>ATVPDKIKX0DER</MarketplaceId>
        <ASIN>B01BF6DQK8</ASIN>
      </MarketplaceASIN>
    </Identifiers>
    <CompetitivePricing>
      <CompetitivePrices/>
      <NumberOfOfferListings/>
    </CompetitivePricing>
    <SalesRankings>
      <SalesRank>
        <ProductCategoryId>home_garden_display_on_website</ProductCategoryId>
        <Rank>4023848</Rank>
      </SalesRank>
      <SalesRank>
        <ProductCategoryId>2245508011</ProductCategoryId>
        <Rank>1856</Rank>
      </SalesRank>
    </SalesRankings>
  </Product>
</GetCompetitivePricingForASINResult>
<ResponseMetadata>
  <RequestId>1e37d1fe-9479-4501-adff-a88948ee0248</RequestId>
</ResponseMetadata>
</GetCompetitivePricingForASINResponse>"""

listmatchesxml = """<?xml version="1.0"?>
<ItemLookupResponse xmlns="http://webservices.amazon.com/AWSECommerceService/2011-08-01">
<OperationRequest>
    <HTTPHeaders>
        <Header Name="UserAgent" Value="amazonmws/0.0.1 (Language=Python)"/>
    </HTTPHeaders>
    <RequestId>a52c73b5-2bff-447d-bed9-aad53f101215</RequestId>
    <Arguments>
        <Argument Name="AWSAccessKeyId" Value="AKIAJ5DMMGOMROO42YTQ"/>
        <Argument Name="AssociateTag" Value="gmksourcing-20"/>
        <Argument Name="ItemId" Value="B0000VLZK8"/>
        <Argument Name="Operation" Value="ItemLookup"/>
        <Argument Name="ResponseGroup" Value="OfferFull, SalesRank, ItemAttributes"/>
        <Argument Name="Service" Value="AWSECommerceService"/>
        <Argument Name="SignatureMethod" Value="HmacSHA256"/>
        <Argument Name="SignatureVersion" Value="2"/>
        <Argument Name="Timestamp" Value="2016-11-13T23:50:02Z"/>
        <Argument Name="Version"/>
        <Argument Name="Signature" Value="sG7nAA29rHgm+HcHPQoz+wksoh15fLT3ZuT9sYybYdo="/>
    </Arguments>
    <RequestProcessingTime>0.0452704550000000</RequestProcessingTime>
</OperationRequest>
<Items>
    <Request>
        <IsValid>True</IsValid>
        <ItemLookupRequest>
            <IdType>ASIN</IdType>
            <ItemId>B0000VLZK8</ItemId>
            <ResponseGroup>OfferFull</ResponseGroup>
            <ResponseGroup>SalesRank</ResponseGroup>
            <ResponseGroup>ItemAttributes</ResponseGroup>
            <VariationPage>All</VariationPage>
        </ItemLookupRequest>
    </Request>
    <Item>
        <ASIN>B0000VLZK8</ASIN>
        <ParentASIN>B004P1HTOU</ParentASIN>
        <DetailPageURL>https://www.amazon.com/Rubbermaid-FG193300WHT-2-Inch-Spoon-Shaped-Spatula/dp/B0000VLZK8%3Fpsc%3D1%26SubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D165953%26creativeASIN%3DB0000VLZK8</DetailPageURL>
        <ItemLinks>
            <ItemLink>
                <Description>Technical Details</Description>
                <URL>https://www.amazon.com/Rubbermaid-FG193300WHT-2-Inch-Spoon-Shaped-Spatula/dp/tech-data/B0000VLZK8%3FSubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>Add To Baby Registry</Description>
                <URL>https://www.amazon.com/gp/registry/baby/add-item.html%3Fasin.0%3DB0000VLZK8%26SubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>Add To Wedding Registry</Description>
                <URL>https://www.amazon.com/gp/registry/wedding/add-item.html%3Fasin.0%3DB0000VLZK8%26SubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>Add To Wishlist</Description>
                <URL>https://www.amazon.com/gp/registry/wishlist/add-item.html%3Fasin.0%3DB0000VLZK8%26SubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>Tell A Friend</Description>
                <URL>https://www.amazon.com/gp/pdp/taf/B0000VLZK8%3FSubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>All Customer Reviews</Description>
                <URL>https://www.amazon.com/review/product/B0000VLZK8%3FSubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
            <ItemLink>
                <Description>All Offers</Description>
                <URL>https://www.amazon.com/gp/offer-listing/B0000VLZK8%3FSubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</URL>
            </ItemLink>
        </ItemLinks>
        <SalesRank>47598</SalesRank>
        <ItemAttributes>
            <Binding>Misc.</Binding>
            <Brand>Rubbermaid Commercial</Brand>
            <CatalogNumberList>
                <CatalogNumberListElement>FG193300WHT</CatalogNumberListElement>
                <CatalogNumberListElement>RCP1933WHI</CatalogNumberListElement>
            </CatalogNumberList>
            <Color>white</Color>
            <EAN>0086876162226</EAN>
            <EANList>
                <EANListElement>0086876162226</EANListElement>
            </EANList>
            <Feature>Spoon, scrape and spread with one easy tool. Clean-Rest reduces risk of cross-contamination.</Feature>
            <Feature>Blades are molded into handles for seamless construction that reduces build-up of dirt and bacteria</Feature>
            <Feature>Clean-Rest feature keeps blade off countertops, reducing cross-contamination</Feature>
            <Feature>NSF certified and commercial dishwasher safe</Feature>
            <Feature>Blades molded onto handles for permanent bond</Feature>
            <Feature>Seamless construction resists dirt or bacteria build up</Feature>
            <Feature>All handles and blades are white</Feature>
            <Feature>Commercial dishwasher safe</Feature>
            <Feature>Certified to NSF Standard</Feature>
            <ItemDimensions>
                <Height Units="hundredths-inches">50</Height>
                <Length Units="hundredths-inches">950</Length>
                <Weight Units="hundredths-pounds">50</Weight>
                <Width Units="hundredths-inches">347</Width>
            </ItemDimensions>
            <Label>Rubbermaid</Label>
            <ListPrice>
                <Amount>422</Amount>
                <CurrencyCode>USD</CurrencyCode>
                <FormattedPrice>$4.22</FormattedPrice>
            </ListPrice>
            <Manufacturer>Rubbermaid</Manufacturer>
            <Model>FG193300WHT</Model>
            <MPN>FG193300WHT</MPN>
            <NumberOfItems>1</NumberOfItems>
            <PackageDimensions>
                <Height Units="hundredths-inches">40</Height>
                <Length Units="hundredths-inches">950</Length>
                <Weight Units="hundredths-pounds">22</Weight>
                <Width Units="hundredths-inches">270</Width>
            </PackageDimensions>
            <PackageQuantity>1</PackageQuantity>
            <PartNumber>FG193300WHT</PartNumber>
            <ProductGroup>Kitchen</ProductGroup>
            <ProductTypeName>HOME</ProductTypeName>
            <Publisher>Rubbermaid</Publisher>
            <Size>9-1/2"</Size>
            <Studio>Rubbermaid</Studio>
            <Title>Rubbermaid FG193300WHT 9-1/2-Inch Spoon-Shaped Spatula</Title>
            <UPC>086876162226</UPC>
            <UPCList>
                <UPCListElement>086876162226</UPCListElement>
            </UPCList>
        </ItemAttributes>
        <OfferSummary>
            <LowestNewPrice>
                <Amount>562</Amount>
                <CurrencyCode>USD</CurrencyCode>
                <FormattedPrice>$5.62</FormattedPrice>
            </LowestNewPrice>
            <TotalNew>11</TotalNew>
            <TotalUsed>0</TotalUsed>
            <TotalCollectible>0</TotalCollectible>
            <TotalRefurbished>0</TotalRefurbished>
        </OfferSummary>
        <Offers>
            <TotalOffers>1</TotalOffers>
            <TotalOfferPages>1</TotalOfferPages>
            <MoreOffersUrl>https://www.amazon.com/gp/offer-listing/B0000VLZK8%3FSubscriptionId%3DAKIAJ5DMMGOMROO42YTQ%26tag%3Dgmksourcing-20%26linkCode%3Dxm2%26camp%3D2025%26creative%3D386001%26creativeASIN%3DB0000VLZK8</MoreOffersUrl>
            <Offer>
                <Merchant>
                    <Name>GMK Sourcing</Name>
                </Merchant>
                <OfferAttributes>
                    <Condition>New</Condition>
                </OfferAttributes>
                <OfferListing>
                    <OfferListingId>vs5OsPGRRvPFy2uxvdaaILVrTn6Y9hrTlOrF%2FsspuX8QmwM6gDn4goT9Psf5Uw%2F2JfMaoOaPXaX3Lb5IGaZF2yu1pNH06lB9FojHylWn7EG7MStbTr2N8Qa1rn%2Fuvs4ISho%2FvswbrKVESX1AX8ZJJuc62cSCcT0T</OfferListingId>
                    <Price>
                        <Amount>1099</Amount>
                        <CurrencyCode>USD</CurrencyCode>
                        <FormattedPrice>$10.99</FormattedPrice>
                    </Price>
                    <Availability>Usually ships in 24 hours</Availability>
                    <AvailabilityAttributes>
                        <AvailabilityType>now</AvailabilityType>
                        <MinimumHours>24</MinimumHours>
                        <MaximumHours>24</MaximumHours>
                    </AvailabilityAttributes>
                    <IsEligibleForSuperSaverShipping>0</IsEligibleForSuperSaverShipping>
                    <IsEligibleForPrime>1</IsEligibleForPrime>
                </OfferListing>
            </Offer>
        </Offers>
    </Item>
</Items>
</ItemLookupResponse>
"""