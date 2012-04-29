import lxml.html
import time

def get_rows(tree):
    """Yield all item 'rows' with some quantity remaining to be purchased.

    Prunes the tree, yielding only the bits with information we care about.

    """
    for row in tree.xpath('//table[@class="registryViewTable"]/tr'
                          '[contains(@id,"MainContentArea")]'):
        yield row

def parse_row(row):
    """Parse an item 'row.'
    
    Parses a row, returning the sku and a dict representation of the item.

    """
    sku = row.xpath('td[2]/span/text()')[0]
    item = {
        'name': row.xpath('td[1]/div[2]/a/text()')[0]\
                .encode('ascii','ignore'),
        'requested': int(row.xpath('td[5]/span/text()')[0]),
        'remaining': int(row.xpath('td[6]/span/text()')[0])
    }
    return sku, item

def parse(url):
    """Yield all parsed items from the given url."""
    tree = lxml.html.parse(url)
    for row in get_rows(tree):
        yield parse_row(row)

def run(url, delay=60):
    """Continuously parse the given url, yielding items as they are bought."""
    # initialize data
    initial = {}
    for sku, item in parse(url):
        initial[sku] = item

    while True:
        print 'looping..'
        time.sleep(delay)
        data = initial.copy()
        for sku, item in parse(url):
            # get items that are still on the list
            if item['remaining'] != data[sku]['remaining']:
                yield sku, item
                initial[sku]['remaining'] = item['remaining']
            del data[sku]
        # check for items that are no longer on the list
        for sku, item in data.iteritems():
            item['remaining'] = 0
            yield sku, item
            del initial[sku]

if __name__ == '__main__':
    import os

    url = ('http://www1.burlingtoncoatfactory.com/'
           'PurchaseRegistryItems.aspx?id=30413117')

    for sku, i in run(url, 600):
        print sku, i
        os.popen('echo "someone just bought: %s. %s remaining." | '\
                 'mailx 1234567890@vmobl.com' % (i['name'],i['remaining']))