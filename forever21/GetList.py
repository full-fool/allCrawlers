#! /usr/bin/env python
#coding=utf-8

import os
import sys
import re
import urllib2, urllib
import codecs
import socket
import time
import threading
from bs4 import BeautifulSoup

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


def getItemList(realcate, cate, url, fhandler, page):
    pageContent = getPageWithSpecTimes(0, 
            url+'&pagesize=120&page=%d' % page)
    if pageContent == None:
        writeToLog('cannot open list page: %s' % url)
        getItemList(realcate, cate, url, fhandler, page + 1)
    else:
        productPattern = re.compile(r"<a class='pdpLink' href='.+&ProductID=(\d+).+'>")
        productList = productPattern.findall(pageContent)
        for productId in productList:
            fhandler.write('%s %s\n' % (realcate, productId))
        print 'Found %d products in page %d, cate %s' \
                % (len(productList), page, cate)
        if len(productList) < 120:
            return

        if '<a class="PagerHyperlinkStyle"' in pageContent:
            getItemList(realcate, cate, url, fhandler, page + 1)





class Product(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, realcate, cate, url, parent, page):
        threading.Thread.__init__(self)
        self.realcate = realcate
        self.cate = cate
        self.url = url
        self.parent = parent
        self.page = page


    def run(self):
        realcate = self.realcate
        cate = self.cate
        url = self.url
        parent = self.parent
        page = self.page
        
        path = os.path.join(parent, '%s.txt'%a.text)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            return

        fhandler = open(path,'w')

        # print str(os.path.join(parent, '%s.txt'%a.text))
        getItemList(realcate, cate, url, fhandler, page)

        fhandler.close()









def findThread(realcate, cate, url, parent, page):
    global threadNum
    global threadNumPool
    findThread = False
    while findThread == False:
        for k in range(threadNum):
            if (not threadNumPool.has_key(k)) or \
                    (not threadNumPool[k].isAlive()):
                threadNumPool[k] = Product(realcate, cate, url, parent, page)
                threadNumPool[k].start()
                findThread = True
                break
        if findThread == False: 
            time.sleep(5)


threadNum = 100
threadNumPool = {}


listDir = 'list'
if not os.path.exists(listDir):
    os.makedirs(listDir)

content = getPageWithSpecTimes(0, 'http://www.forever21.com/default.aspx')
soup = BeautifulSoup(content)
cates = [ 
    ('WOMEN', 'women'), 
    ('MEN', 'men'), 
    ('CONTEMPORARY', 'love21'), 
    ('ACCESSORIES', 'acc'), 
    ('KIDS', 'girls'), 
    ('PLUS SIZES', 'plus')
    ]
for cate in cates:
    for col in soup\
            .find(class_='%s dropdown' % cate[1])\
            .find_all(class_='col'):
        for a in col.find_all('a'):
            if a['href'].find('Category.aspx') > -1:
                parent = os.path.join(listDir, cate[0])


                if not os.path.exists(parent):
                    os.makedirs(parent)
                category = a['href'].split('=')[-1]
                #fhandler = open(os.path.join(parent, '%s.txt'%a.text),'w')
                
                
                findThread(\
                        category,
                        '%s > %s' % (cate[0], a.text), 
                        a['href'], parent ,1)
                #fhandler.close()


