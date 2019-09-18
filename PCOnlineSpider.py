#-*- coding:utf-8 -*-
import requests
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import os
import pymysql
import json
import time

product_dict = {'cpu': '20812','motherboard': '20811','memory': '20813','hd': '20814','ssd': '42997','graphic_card': '20817','machine_box': '20872','power': '20881','display': '20950','keyboard': '20873','mouse': '20820','sound_box': '20848','radiator': '20973','sound_card': '20818','cdrom': '20874','earphone': '20990'}
id_list = [ product_dict['cpu'], product_dict['motherboard'], product_dict['memory'], product_dict['hd'], product_dict['ssd'], product_dict['graphic_card'], product_dict['machine_box'], product_dict['power'], product_dict['display'], product_dict['keyboard'], product_dict['mouse'], product_dict['sound_box'], product_dict['radiator'],product_dict['sound_card'], product_dict['cdrom'], product_dict['earphone'] ]
type_list = [ 'CPU', 'MOTHERBOARD', 'MEMORY', 'HD', 'SSD', 'GRAPHIC_CARD', 'MACHINE_BOX', 'POWER', 'DISPLAY', 'KEYBOARD', 'MOUSE', 'SOUND_BOX', 'RADIATOR', 'SOUND_CARD', 'CDROM', 'EARPHONE']
SERVER_IP = "127.0.0.1"
USERNAME = "root"
PASSWORD = ""
DB = "PC_Products"

try:
    db = pymysql.connect( SERVER_IP, USERNAME, PASSWORD, DB )
except:
    print("Fail to connect to the database, please check if the server is down.")
    os.system("pause")
    exit(0)
else:
    print("Connection successfully established!")
cursor = db.cursor()
start = time.perf_counter()

for id in range(0, 16):
    cursor.execute("DROP TABLE IF EXISTS %s" % (type_list[id])) 
    sql = """
    CREATE TABLE %s (
    NAME VARCHAR(64),
    ID INT,
    PRICE INT DEFAULT 0,
    SUMMARY VARCHAR(512) DEFAULT "None",
    DETAIL_URL VARCHAR(512) DEFAULT "None"
    )ENGINE=innodb DEFAULT CHARSET=utf8;
    """ % (type_list[id])
    cursor.execute(sql)

#headers = {
#    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#                 ' (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
#}
#url = 'https://mydiy.pconline.com.cn/'

driver = webdriver.PhantomJS(executable_path='/opt/phantomjs/bin/phantomjs')
#driver = webdriver.Chrome(executable_path="C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe")
for id in range(0, 16):
    if(id==10):
        print("#pconline corrupted json")
        continue
    pageNo = 1
    while(True):
        url = "http://product.pconline.com.cn/intf/_search_json.jsp?&refresh=true&callback=filter.callback&charset=utf8&sId="+id_list[id]+"&bId=&keyword=&pcId=&cId=&cId=&cId=&areaId=1&summaryLen=1000&pageNo="+str(pageNo)+"&pageSize=1000&order=1"
        driver.get(url)
        raw_json = driver.page_source
        raw_json = str(raw_json)
        raw_json = raw_json.replace('\n','')
        raw_json = raw_json.replace('\r','')
        raw_json = raw_json.replace('<html><head></head><body>filter.callback(','')
        raw_json = raw_json.replace(')</body></html>','')
        if(id==10):
            raw_json = raw_json.replace(')</br","id":"550869","detailurl":"></body></html>','')
        #open('json.txt','w',encoding='utf-8').write(str(raw_json))
        raw_value = json.loads(raw_json)
        data_json = raw_value['data']
        if(str(data_json)=='[]'):
            print('%s data update' % (type_list[id]))
            break
        for product_value in data_json:
            ID = int(product_value['id'].strip())
            NAME = str(product_value['shortName']).strip()
            PRICE = str(product_value['price']).strip()
            if(PRICE == "新品" or PRICE == "下市"):
                PRICE = 0
            PRICE = str(PRICE)
            summary = str(product_value['summary']).strip()
            summary = str(product_value['summary']).replace("'","")
            DETAIL_URL = 'https:' + str(product_value['detailUrl']).strip()
            #print(summary)
            upload = "INSERT INTO %s(NAME,ID,PRICE,SUMMARY,DETAIL_URL) \
            VALUES ('%s',%s,%s,'%s','%s')" % (type_list[id], NAME, ID, PRICE, summary, DETAIL_URL)
            # 执行sql语句
            cursor.execute(upload)
        try:
           # 提交到数据库执行
            db.commit()
        except:
           # 如果发生错误则回滚
           db.rollback()
           print("ERROR!")
           #os.system("pause")
        driver.implicitly_wait(1) # seconds
        time.sleep(2)
        pageNo = pageNo + 1
    #os.system("pause")
        
elapsed = (time.perf_counter() - start)
print("Time used: %f s" % elapsed)
driver.quit()
db.close()
