#! /usr/bin/env python
#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
from bs4 import BeautifulSoup
import time
import threading

socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
logLock = threading.Lock()


#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    tryTimes = 4
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
                html = urllib2.urlopen(url).read()                
            elif decodeType == 1:
                html = urllib2.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib2.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            elif decodeType == 3:
                html = urllib2.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else:
                html = urllib2.urlopen(url).read()
            break
        except Exception as ep:
            print ep.message
            alreadyTriedTimes += 1
            if alreadyTriedTimes == 1:
                time.sleep(1)
            elif alreadyTriedTimes == 2:
                time.sleep(60)
            elif alreadyTriedTimes == 3: 
                time.sleep(300)
            else:
                return None
    return html


def writeToLog(content):
    try:
        print content
    except Exception as ep:
        print ep.message

    logLock.acquire()
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()
    logLock.release()


class Product(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, cate, subcate, info, count, num):
        threading.Thread.__init__(self)
        self.url = 'http://www.forever21.com/'\
                +'Product/Product.aspx?'\
                +'Category=%s&ProductID=%s'\
                % tuple(info)
        self.count = count
        self.num = num
        self.resultDir = 'result'
        self.cate = cate
        self.subcate = subcate
        self.productId = info[1]
        self.imgsides = ['front', 'side', 'back', 
                'full', 'detail', 'flat', 'additional']

    def run(self):
        info = {
                'url': self.url,
                'info': {
                    'category': self.cate,
                    'sub_category': self.subcate,
                    'code': self.productId
                    },
                'img': []
                }
        err = self.getProductInfo(info)
        if err == -1:
            return

        productDir = os.path.join(\
                self.resultDir, self.cate, self.subcate, 
                self.productId)
        if not os.path.exists(productDir):
            os.makedirs(productDir)
        
        self.downloadImages(info, productDir)

        f = open(os.path.join(productDir, 'Product_Description.txt'), 'w')
        f.write(json.dumps(info, indent=4, 
                ensure_ascii=False, 
                separators=(',',':')))
        f.close()

        print 'Finished product %s/%d in cate %s>%s' \
                % (self.count, self.num, \
                self.cate, self.subcate)

    def getProductInfo(self, info):
        pageContent = getPageWithSpecTimes(1, info['url'])
        if pageContent == None:
            writeToLog('cannot open item page: %s' % item['url'])
            return -1

        namePattern = re.compile(r'<h1 class="product-title">(.*?)</h1>')
        name = namePattern.findall(pageContent)
        if len(name) > 0:
            info['info']['name'] = name[0]

        pricePattern = re.compile(r'<p class="product-price">(.*?)</p>')
        price = pricePattern.findall(pageContent)
        if len(price) > 0:
            info['info']['price'] = price[0]

        soup = BeautifulSoup(pageContent)
        descs = soup.find(id='product_overview')
        desc = []
        p = descs.find('p')
        if p != None:
            desc.append(p.text)
        ul = descs.find('ul')
        if ul != None:
            for li in ul.find_all('li'):
                desc.append(li.text)
        info['info']['description'] = desc

        imgPattern = re.compile(r'<input .*? src="http://www.forever21.com/images/sw_22/(.*?).jpg" .*? />')
        imgs = imgPattern.findall(pageContent)
        colorList = soup\
                .find(id='ctl00_MainContent_upColorList')\
                .find_all('option')
        for img in imgs:
            color = img
            for c in colorList:
                if c['value'].find(img) == 0:
                    color = c.text
            for i in range(7):
                info['img'].append({
                    'url': 'http://www.forever21.com/images/'\
                            + '%d_%s_750/%s.jpg'\
                            % (i+1, self.imgsides[i], img),
                    'color': '-'.join(color.split('/'))
                    })

        return 0

    def downloadImages(self, info, parent):
        curr_color = -1
        curr_count = 1
        err_img = []
        for img in info['img']:
            imgDir = os.path.join(parent, img['color'])
            if not os.path.exists(imgDir):
                os.makedirs(imgDir)
            if img['color'] != curr_color:
                curr_color = img['color']
                curr_count = 1
            name = '%s_%s_%d.jpg' \
                    % (info['info']['code'], \
                    img['color'], curr_count)
            tryTime = 1
            while tryTime < tryTimes:
                try:
                    path = os.path.join(imgDir, name)
                    urllib.urlretrieve(img['url'], path)
                    if os.path.getsize(path) == 16:
                        err_img.append(img)
                        os.remove(path)
                    else:
                        img['name'] = name
                        curr_count += 1
                    fail = 0
                    break
                except Exception as ep:
                    tryTime += 1
                    fail = 1
            if fail == 1:
                writeToLog('cannot download image: %s' % img['url'])
        for img in err_img:
            info['img'].remove(img)

threadNum = 200
threadNumPool = {}

def findThread(cate, subcate, productId, count, num):
    global threadNum
    global threadNumPool
    findThread = False
    while findThread == False:
        for k in range(threadNum):
            if (not threadNumPool.has_key(k)) or \
                    (not threadNumPool[k].isAlive()):
                threadNumPool[k] = Product(\
                        cate, subcate, productId,
                        count, num)
                threadNumPool[k].start()
                findThread = True
                break
        if findThread == False: 
            time.sleep(5)


listDir = 'list'

for cate in os.listdir(listDir):
    cateDir = os.path.join(listDir, cate)
    for subcate in os.listdir(cateDir):
        if subcate.find('.') == 0:
            continue
        f = open(os.path.join(cateDir, subcate))
        lines = f.readlines()
        count = 0
        num = len(lines)
        for line in lines:
            count += 1
            info = line.strip().split(' ')
            findThread(cate, subcate.split('.')[0], info,
                    count, num)
        f.close()


