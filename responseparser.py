import re
from lxml import etree


class ParseError(Exception):
    pass

class AmazonError(Exception):

    def __init__(self, msg, type, code):
        super(AmazonError, self).__init__(msg)
        self.type = type
        self.code = code


class MWSResponseParser:

    re_ns_decl = re.compile(r' xmlns(:\w*)?="[^"]*"', re.IGNORECASE)
    re_ns_open = re.compile(r'<\w+:')
    re_ns_close = re.compile(r'/\w+:')

    def __init__(self, xml=None):
        if xml:
            self.tree = etree.fromstring(self._remove_namespace(xml))
            self.error_test()
        else:
            self.tree = None

    def _remove_namespace(self, xml):
        """Remove all traces of namespaces from an XML string."""
        response = self.re_ns_decl.sub('', xml)     # Remove namespace declarations
        response = self.re_ns_open.sub('<', response)    # Remove namespaces in opening tags
        response = self.re_ns_close.sub('/', response)   # Remove namespaces in closing tags
        return response

    def _xpath_get(self, root, path, dtype=str, default=None):
        """Use XPath to get values under a root node, including type casting and a default value."""
        items = root.xpath(path)
        try:
            return dtype(items[0].text)
        except (TypeError, IndexError):
            return default

    def error_test(self):
        """Test if the response is valid, or is an ErrorResponse"""
        if self.tree is None:
            raise ParseError('No XML has been provided.')

        if self.tree.tag == 'ErrorResponse':
            msg = self._xpath_get(self.tree, './Error/Message')
            type_ = self._xpath_get(self.tree, './Error/Type')
            code = self._xpath_get(self.tree, './Error/Code')
            raise AmazonError(msg, type_, code)

    def parse(self, xml):
        self.tree = etree.fromstring(self._remove_namespace(xml))
        self.error_test()


class ListMatchingProductsParser(MWSResponseParser):

    def get_products(self):
        if self.tree is None:
            raise ParseError('No XML has been provided.')

        for tag in self.tree.iterdescendants('Product'):
            product = {}

            product['asin'] = self._xpath_get(tag, './/MarketplaceASIN/ASIN')

            product['brand'] = self._xpath_get(tag, './/Brand') \
                               or self._xpath_get(tag, './/Manufacturer') \
                               or self._xpath_get(tag, './/Label')

            product['model'] = self._xpath_get(tag, './/Model') \
                               or self._xpath_get(tag, './/PartNumber')

            # I don't know if UPC is provided by ListMatchingProducts...
            product['upc'] = self._xpath_get(tag, './/UPC')

            product['title'] = self._xpath_get(tag, './/Title')

            # TODO: Implement a more robust/accurate way to get category and sales rank
            product['productgroup'] = self._xpath_get(tag, './/ProductGroup')
            product['salesrank'] = self._xpath_get(tag, './/SalesRank/Rank', int)

            product['numberofitems'] = self._xpath_get(tag, './/NumberOfItems', int)
            product['packagequantity'] = self._xpath_get(tag, './/PackageQuantity', int)

            features = []
            for feature in tag.iterdescendants('Feature'):
                features.append(feature.text)
            product['features'] = '\n'.join(features)

            yield product


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