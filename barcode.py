# -*- coding: utf-8 -*-
import csv     
import requests
import json
import datetime
from bs4 import BeautifulSoup 
import sys
reload(sys)
sys.setdefaultencoding('utf8')



session = requests.Session()
session.headers.update({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
})

proxies = [
    "163.172.48.109:15002",
    "163.172.48.117:15002",
    "163.172.48.119:15002",
    "163.172.48.121:15002",
    "163.172.36.181:15002",
    "163.172.36.191:15002",
    "62.210.251.228:15002",
    "163.172.36.207:15002"
]




def get_detail(detail_url, count):
    r = session.get(detail_url, proxies={
		"https": proxies[count % 9]
    })
    soup = BeautifulSoup(r.text, features="html.parser")
    if len(soup.findAll('table')) == 0:
        return get_detail(detail_url, count + 1)
    else:
        return soup


def scrape_data(keyword):
    csv.register_dialect('myDialect1',
      quoting=csv.QUOTE_ALL,
      skipinitialspace=True)
    date = datetime.datetime.now()
    f = open('{}_{}_{}_{}.csv'.format(keyword, date.month, date.day, date.year), 'w')
    writer = csv.writer(f, dialect='myDialect1')
    writer.writerow(['Name', 'Image', 'UPC-A', 'EAN-13', 'Amazon ASIN', 'Category', 'Brand', 'Model', 'Last Scanned', 'Store Name', 'Price', 'Currency'])
    url = 'https://www.barcodespider.com/{}'

    r = session.get(url.format(keyword), proxies={
        "https": "83.149.70.159:13042"
    })
    soup = BeautifulSoup(r.text, features="html.parser")
    # print(soup)
    # print(r.text)
    pagecount = len(soup.findAll('li', class_='page-item'))
    if pagecount == 0:
        pagecount = 1
    baseurl = 'https://www.barcodespider.com/search/{}/{}'
    print(pagecount)

    for page in range(1, pagecount + 1):
        print(baseurl.format(keyword, page))
        r = session.get(baseurl.format(keyword, page), proxies={
            "https": "83.149.70.159:13042"
        })
        soup = BeautifulSoup(r.text, features="html.parser")
        items = soup.findAll('div', class_='UPCdetail')
        print(len(items))
        for item in items:
            detail_url = item.find('a').attrs['href']
            data = [ item.find('p').text]
            soup = get_detail(detail_url, 0)
            data.append(soup.find('div', class_='thumb-image').find('img').attrs['src'])
            attr_table = soup.findAll('table')[0]
            attrs = attr_table.findAll('tr')
            for attr in attrs:
                data.append("=\"" + attr.findAll('td')[1].text + "\"")
            store_table = soup.findAll('table')[1]
            for store in store_table.find('tbody').findAll('tr'):
                data.append(store.findAll('td')[0].text)
                if store.findAll('td')[2].text[0] == 'c':
                    data.append(store.findAll('td')[2].text)
                    data.append('')

                else:
                    data.append(store.findAll('td')[2].text.split(store.findAll('td')[2].text[0])[1].split(' ')[0])
                    data.append(store.findAll('td')[2].text.split(store.findAll('td')[2].text[0])[1].split(' ')[1])

            print(data)
            writer.writerow(data)
    f.close()
if __name__ == '__main__':
    print(sys.argv[1].strip().replace(' ', '-'))
    scrape_data(sys.argv[1].strip().replace(' ', '-'))