import requests
import yaml
from bs4 import BeautifulSoup
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import random
import redis
from app import sendBot
import asyncio
import nest_asyncio
import time
from Utils import postgres_tool

nest_asyncio.apply()

with open('./config/config.yml', 'r') as f:
    config = yaml.safe_load(f)

# redis_sv = config['redis_sv']
# print(redis_sv)
# redis_client = redis.Redis(**redis_sv)

urlproxy = config['url']['urlproxy']
listip = []
listport = []

def getproxy(urlproxy):
    headers = config['headers'] 
    response = requests.get(urlproxy, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for item in data['proxies']:
            listip.append(item['ip'])
            listport.append(item['port'])
            
def getData(urlbonban,df):
    # dfproxy = pd.read_csv('./data/proxys.csv')
    dfproxy = df
    proxies = dfproxy.to_dict('records')
    
    while proxies:
        proxy = random.choice(proxies)
        proxy_dict = {
            "http": f"http://{proxy['ip']}:{proxy['port']}",
            "https": f"http://{proxy['ip']}:{proxy['port']}"
        }

        try:
            response = requests.get(url=urlbonban, proxies=proxy_dict, timeout=10)   
            # print(response.status_code)         
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                all_results = soup.find_all('li', class_=['car-item row1','car-item row2'])
                db_config = config["database"]    
                conn =  postgres_tool.PostgresTool(**db_config)
                for result in all_results:
                    data = {}
                    data["name"] = result.find('h3').text
                    data["price"] = result.find('div', class_='cb3').text
                    data["location"] = result.find('div', attrs={'class':'cb7'}).text
                    data["urlcar"] = "https://bonbanh.com/" + result.find('a', attrs={'itemprop':'url'}).get('href')
                    data['image'] = result.find('img',attrs={"class":"h-car-img"}).get('src')
                    data['sent'] = False
                    conn.push_data('car', data)
                conn.close()
                return  
        except :
            pass        
    
def main():

    listproxy = []
    for i in range(0, 1000, 15):
        listproxy.append(urlproxy.format(i))

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(getproxy, listproxy)
    df = pd.DataFrame({'ip': listip, 'port': listport})

    listUrl = ['https://bonbanh.com/tp-hcm/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/tp-hcm/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/tp-hcm/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/tp-hcm/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/tp-hcm/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/an-giang/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/an-giang/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/an-giang/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/an-giang/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/an-giang/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/ba-ria-vung-tau/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/ba-ria-vung-tau/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/ba-ria-vung-tau/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/ba-ria-vung-tau/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/ba-ria-vung-tau/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/bac-lieu/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/bac-lieu/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/bac-lieu/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/bac-lieu/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/bac-lieu/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/ben-tre/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/ben-tre/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/ben-tre/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/ben-tre/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/ben-tre/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/binh-duong/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/binh-duong/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/binh-duong/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/binh-duong/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/binh-duong/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/binh-phuoc/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/binh-phuoc/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/binh-phuoc/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/binh-phuoc/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/binh-phuoc/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/ca-mau/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/ca-mau/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/ca-mau/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/ca-mau/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/ca-mau/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/can-tho/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/can-tho/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/can-tho/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/can-tho/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/can-tho/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/dong-nai/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/dong-nai/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/dong-nai/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/dong-nai/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/dong-nai/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/dong-thap/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/dong-thap/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/dong-thap/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/dong-thap/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/dong-thap/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/hau-giang/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/hau-giang/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/hau-giang/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/hau-giang/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/hau-giang/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/kien-giang/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/kien-giang/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/kien-giang/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/kien-giang/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/kien-giang/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/long-an/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/long-an/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/long-an/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/long-an/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/long-an/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/soc-trang/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/soc-trang/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/soc-trang/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/soc-trang/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/soc-trang/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/tay-ninh/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/tay-ninh/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/tay-ninh/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/tay-ninh/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/tay-ninh/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/tien-giang/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/tien-giang/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/tien-giang/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/tien-giang/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/tien-giang/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/tra-vinh/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/tra-vinh/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/tra-vinh/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/tra-vinh/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/tra-vinh/oto-gia-duoi-200-trieu/page,5',
               'https://bonbanh.com/vinh-long/oto-gia-duoi-200-trieu/page,1','https://bonbanh.com/vinh-long/oto-gia-duoi-200-trieu/page,2','https://bonbanh.com/vinh-long/oto-gia-duoi-200-trieu/page,3','https://bonbanh.com/vinh-long/oto-gia-duoi-200-trieu/page,4','https://bonbanh.com/vinh-long/oto-gia-duoi-200-trieu/page,5',
               ]
    for url in listUrl:
        getData(url,df)

if __name__ == '__main__':
    while True:
        main()
        time.sleep(30*60) # 30 p
        # time.sleep(2)

