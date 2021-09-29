from bs4 import BeautifulSoup
from tqdm import tqdm
import grequests
from tinydb import TinyDB, Query

db = TinyDB('vessels.json')

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 ' \
             'Safari/537.36'

headers = {'User-Agent': USER_AGENT}

def get_vessel_links(content, base_url):
    data =BeautifulSoup(content, 'html.parser')
    links = [base_url+a['href'] for a in data.find_all('a',class_="ship-link" ,href=True) if a.text]
    return list(set(links))


def get_all_vessel_links(flag="IR", pages=100, n1=20, n2=10):
    links=[]
    base_url='https://www.vesselfinder.com/'
    urls=["https://www.vesselfinder.com/vessels?page=%s&flag=%s"%(i, flag) for i in range(1,pages)]
    
    for i in tqdm(range(0, len(urls), n1)):
        rs=(grequests.get(url, headers=headers) for url in urls[i:i+n1])
        lst = grequests.map(rs)
        for item in lst:
            links.extend(get_vessel_links(item.content, base_url))
    links=list(set(links)) 
    for i in tqdm(range(0, len(links), n2)):
        rs = (grequests.get(url, headers=headers) for url in links[i:i+n2])
        lst = grequests.map(rs)
        for item in lst:
            if item:
                get_vessel_information(item.content)
    

def get_vessel_information(content):
    data =BeautifulSoup(content, 'html.parser')
    labels=[]
    values=[]
    if data.find('table', {'class':'aparams'}):
        labels = data.find('table', {'class':'aparams'}).find_all('td', {'class':'n3'})
        values = data.find('table', {'class':'aparams'}).find_all('td', {'class':'v3'})
        labels = [lbl.get_text(strip=True) for lbl in labels]
        values = [val.get_text(strip=True) for val in values]
        dic = dict(zip(labels, values))
        db.insert(dic)
