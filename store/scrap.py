from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from ebaysdk.finding import Connection

from ebaysdk import finding

ebayapi = "MoatazGh-test-PRD-16e4c7d7e-e927c4f5"


def ebay(name):
    req = Request("https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw=iphone+x&_sacat=0", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    # divs = soup.find_all('div', {'class': 'r_b_c'})
    lis = soup.find_all('li', {'class': 's-item'})
    info = []
    for i in lis:
        try:
            img = i.find('img', {'class': 's-item__image-img'})
            p1 = i.find('h3', {'class': 's-item__title'})
            p2 = i.find('span', {'class': 's-item__price'})
            anchr = i.find('a', {'class': 's-item__link'})
            # image.append(img.attrs['data-original'])
            # link.append((anchr.get_text(), anchr.attrs['href']))
            # price.append((p1.get_text(), p2.get_text()))
            info.append((img.attrs['src'], anchr.get_text(), anchr.attrs['href'], p1.get_text(), p2.get_text()))
        except Exception as e:
            pass

    return info


def olx(name):
    req = Request("https://www.olx.com.eg/en/ads/q-iphone-x/", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    # divs = soup.find_all('div', {'class': 'r_b_c'})
    lis = soup.find_all('div', {'class': 'ads__item'})
    info = []
    for i in lis:
        try:
            img = i.find('img', {'class': 'ads__item__photos'})
            p1 = i.find('p', {'class': 'ads__item__price price'})
            p2 = i.find('p', {'class': 'ads__item__location'})
            anchr = i.find('a', {'class': 'ads__item__ad--title'})
            # image.append(img.attrs['data-original'])
            # link.append((anchr.get_text(), anchr.attrs['href']))
            # price.append((p1.get_text(), p2.get_text()))
            info.append((img.attrs['src'], anchr.attrs["title"], anchr.attrs['href'], p1.get_text().replace('\n','').replace('\t',''), p2.get_text().replace('\n','').replace('\t','')))
        except Exception as e:
            pass

    return info


def ebay_API(name):
    api = Connection(appid=ebayapi, siteid="EBAY-US", config_file=None)
    api_request = {'keywords' : 'iphone x', 'outputSelector': "SellserInfo", 'sortOrder': 'CurrentPriceHighest'}

    response = api.execute("findItemsByKeywords", api_request)

    x = api.response.dict()
    # print(x['searchResult']['item'][0])
    print(x['searchResult']['item'][0]['title'])
    print(x['searchResult']['item'][0]['shippingInfo'])
    print(x['searchResult']['item'][0]['galleryURL'])
    print(x['searchResult']['item'][0]['viewItemURL'])
    print(x['searchResult']['item'][0]['sellingStatus']['currentPrice'])

    return '(((((((((((((())))))))))))))'
