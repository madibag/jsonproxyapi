import time
import requests
import urllib.request
from traceback import print_exc
import pprint
from datetime import datetime
from pytz import timezone
import schedule
import json
from bs4 import BeautifulSoup as bs
def dailyProxy():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
    }
    url="https://proxy-daily.com/"
    source=requests.get(url).text
    soup=bs(source,'html.parser')
    ans = soup.findAll('div', {'class' : 'centeredProxyList freeProxyStyle'})
    #print(type(ans[0].text))
    l=ans[0].text.splitlines()
    return l

def free_proxy_list():
    required_url = "https://free-proxy-list.net/"
    response = requests.get(required_url )
    soup = bs(response.text, "html.parser")
    listing_dict={}
    i=0
    listing=[]
    table =  soup.find("table", id = "proxylisttable")
    k= table.find_all("tbody")
    for tbody in k:
    	for rows in tbody.find_all("tr"):
    		if rows.find_all("td")[3].get_text() == "India":
    			ip_address = rows.find_all("td")[0].get_text()
    			host = rows.find_all("td")[1].get_text()
    			str1 = ip_address + ":" + host
    			listing.append(str1)
    return listing

def set_proxy():
    resp=requests.get('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list')
    a=((resp.text).split('\n'))
    p_list=[]
    for i in a:
        try:
            p_list.append(json.loads(i))
        except Exception as e:
            continue
    np_list=[]
    for i in p_list:
        np_list.append(i)
    #print(len(np_list))
    proxy=[]
    for i in np_list:
        proxy.append((str(i['host'])+':'+str(i['port'])))
    print(len(proxy))
    return(proxy)


def get_proxy():
    proxies=[]
    user_agent = {'User-agent': 'Mozilla/5.0'}
    proxy=set_proxy()
    i,j=0,0

    try:
        #print("Entered getproxylist")
        proxies=proxies+getproxylist()
        #print("Length after getproxylist Proxy is ",len(proxies))
    except Exception:
        pass
    try:
        #print("Entered Spy proxy")
        proxies=proxies+spy_proxy()
        #print("Length after spy Proxy is ",len(proxies))
    except Exception :
        pass
    try:
        #print('Entered Fate Proxy')
        proxies=proxies+fate_proxy()
        #print("Length after fate Proxy is ",len(proxies))
    except Exception:
        pass
    try:
        #print("Entered FreeProxyList")
        proxies=proxies+free_proxy_list()
        #print("Length after freeproxy is ",len(proxies))
    except Exception as e:
        pass
    try:
        #print("Entered DailyProxy")
        proxies=proxies+dailyProxy()
        #print("Length after Daily Proxies is ",len(proxies))
    except Exception as e:
        print("Daily Proxy",e)
        pass

    for p in proxy:
        url = 'http://pubproxy.com/api/proxy?country=US&limit=20&https=True&user_agent=true'
        while(len(proxies)<100):
            try:
                j=0
                resp = requests.get(url=url,headers=user_agent,proxies={"http": p, "https": p})
                data = resp.json()
                time.sleep(2.1)
                for proxy in data['data']:
                    proxies.append(proxy['ipPort'])
                print('Length of Proxy till '+str(i)+'th attempt is ',len(proxies))
            except Exception as e:
                print(resp.text)
                print('Skipped proxy '+str(p)+" "+str(i)+' time')
                break
            finally:
                i=i+1

    return list(set(proxies))

def getproxylist():
    url='https://api.getproxylist.com/proxy?country[]=IN&lastTested=600'
    p=requests.get(url).json()
    l=[]
    l.append(str(p['ip'])+':'+str(p['port']))
    return l

def fate_proxy():
    resp=requests.get('https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list')
    a=((resp.text).split('\n'))
    p_list=[]
    for i in a:
        try:
            p_list.append(json.loads(i))
        except Exception as e:
            continue
    np_list=[]
    for i in p_list:
        if i['country']=='US':
            np_list.append(i)
    proxy=[]
    for i in np_list:
        proxy.append((str(i['host'])+':'+str(i['port'])))
    return(proxy)

def spy_proxy():
    resp=requests.get('http://spys.me/proxy.txt')
    data=((resp.text).split("Google_passed(+)")[1]).split('\r')[0]
    data=data.split('\n')
    l=[]
    for i in data:
        if 'US' in i:
            i=i.split(' US')[0]
            l.append(i)
    return l

def start():
    india = timezone('Asia/Kolkata')
    in_time = datetime.now(india)
    proxy_json={'data':get_proxy()}
    with open('proxy.json', 'w') as outfile:
        json.dump(proxy_json, outfile)
    print("Updated at "+ str(in_time.strftime('%H-%M-%S'))+" IST")
start()
schedule.every(15).minutes.do(start)
while True:
    # Checks whether a scheduled task is pending to run or not
    schedule.run_pending()
    time.sleep(1)