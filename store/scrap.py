from urllib.request import Request, urlopen
from bs4 import BeautifulSoup, SoupStrainer
from ebaysdk.finding import Connection

from ebaysdk import finding
import os


ebayapi = os.environ.get('EBAY_API')


def ebay(name):
    name = name.replace(' ', '+')
    req = Request(f"https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1313&_nkw={name}&_sacat=0", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    lis = soup.find_all('li', {'class': 's-item'})
    info = []
    for i in lis:
        try:
            img = i.find('img', {'class': 's-item__image-img'})
            p1 = i.find('h3', {'class': 's-item__title'})
            p2 = i.find('span', {'class': 's-item__price'})
            anchr = i.find('a', {'class': 's-item__link'})
            info.append((img.attrs['src'], anchr.get_text(), anchr.attrs['href'], p1.get_text(), p2.get_text()))
        except Exception as e:
            pass

    return info


def olx(name):
    name = name.replace(' ', '-')
    req = Request(f"https://www.olx.com.eg/en/ads/q-{name}/", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    lis = soup.find_all('div', {'class': 'ads__item'})
    info = []
    for i in lis:
        try:
            img = i.find('img', {'class': 'ads__item__photos'})
            p1 = i.find('p', {'class': 'ads__item__price price'})
            p2 = i.find('p', {'class': 'ads__item__location'})
            anchr = i.find('a', {'class': 'ads__item__ad--title'})
            info.append((img.attrs['src'], anchr.attrs["title"], anchr.attrs['href'], p1.get_text().replace('\n','').replace('\t',''), p2.get_text().replace('\n','').replace('\t','')))
        except Exception as e:
            pass

    return info

def get_amazon(name):
    req = Request("https://www.alibaba.com/products/iphone_x.html?IndexArea=product_en", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    lis = soup.find_all('div', {'class': 'organic-offer-wrapper'})
    print(soup)
    info = []
    for i in lis[:3]:
        try:
            img = i.find('img', {'class': 'J-img-switcher-item'})
            p1 = i.find('p', {'class': 'elements-title-normal__content'})
            p2 = i.find('p', {'class': 'elements-offer-price-normal'})
            p3 = i.find('span', {'class': 'element-offer-minorder-normal__value'})
            anchr = i.find('a', {'class': 'elements-title-normal one-line'})
            info.append((img.attrs['src'], anchr.attrs['title'], anchr.attrs['href'], p1.get_text(), p2.get_text(), p3.get_text()))
        except Exception as e:
            pass

    return info


def ebay_API(name):
    api = Connection(appid=ebayapi, siteid="EBAY-US", config_file=None)
    api_request = {'keywords' : f'{name}', 'outputSelector': "SellserInfo", 'sortOrder': 'CurrentPriceHighest'}
    response = api.execute("findItemsByKeywords", api_request)
    x = api.response.dict()
    info = []
    if 'item' in x['searchResult']:
        for i in x['searchResult']['item']:
            try:
                title = i["title"]
                img = i['galleryURL']
                a = i['viewItemURL']
                p = i['sellingStatus']['currentPrice']['value']
                info.append((img, title, a, p))
            except Exception as e:
                print(e)

    return info


def tinydeal(name):
    name = name.replace(' ', "+")
    req = Request(f"https://www.tinydeal.com/buy/{name}.html", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    lis = soup.find_all('li', {'class': 'productListing-even'})
    info = []
    print(len(lis))
    for i in lis:
        try:
            img = i.find('img', {'class': 'lazy_load'})
            p1 = i.find('span', {'class': 'productSpecialPrice'})
            p2 = i.find('span', {'class': 'normalprice'})
            anchr = i.find('a', {'class': 'p_box_title'})
            info.append((img.attrs['data-original'], anchr.get_text(), anchr.attrs['href'], p1.get_text(), p2.get_text()))
        except Exception as e:
            pass

    return info



def souq(name):
    name = name.replace(' ', "-")
    req = Request(f"https://egypt.souq.com/eg-en/{name}/s/?as=1", headers={'User-Agent': 'Mozilla/5.0'})
    response = urlopen(req).read()
    soup = BeautifulSoup(response, 'html.parser')
    lis2 = []
    lis = soup.find_all('div', {'class': 'column column-block block-list-large single-item'})
    if not lis:
        lis2 = soup.find_all('div', {'class': 'column column-block block-grid-large single-item'})

    info = []
    for i in lis:
        try:
            img_wrap = i.find('a', {'class': 'img-bucket img-link itemLink sPrimaryLink'})
            img = i.find('img', {'class': 'img-size-medium imageUrl'})
            p1 = i.find('h3', {'class': 'itemPrice'})
            anchr = i.find('a', {'class': 'itemLink sk-clr2 sPrimaryLink'})
            info.append((img.attrs['data-src'], anchr.attrs['title'], anchr.attrs['href'], p1.get_text()))
        except Exception as e:
            print(e)
            pass

    for i in lis2:
        try:
            p1 = i.find('span', {'class': 'itemPrice'})
            anchr = i.find('a', {'class': 'img-link quickViewAction sPrimaryLink'})
            info.append((anchr.attrs['data-img'], anchr.attrs['data-title'], anchr.attrs['href'], p1.get_text()))
        except Exception as e:
            print(e)
            pass

    return info
