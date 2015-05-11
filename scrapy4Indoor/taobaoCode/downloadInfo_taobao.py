#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import threading
import time
import cookielib
import os
import socket
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()




headers = ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

opener = urllib2.build_opener()
opener.addheaders = [headers]
urllib2.install_opener(opener)

def robustPrint(content):
    try:
        print content
    except Exception as ep:
        print ep.message

def loadProcess():
    try:
        contentList = open('process.txt').read().split(',')
        return int(contentList[0]), int(contentList[1]), int(contentList[2]), int(contentList[3])
    except Exception as ep:
        print 'something wrong with the process.txt. you can create a process.txt and write "0,0,0,0" into it, then \
        restart the program'
        sys.exit()

def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()

#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    tryTimes = 4
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            #print 'url is %s, try time is %s' % (url, alreadyTriedTimes)
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
            if '忘记登录密码' in html:
                print 'too much visit for,%s' % url
                raise Exception
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
    writeLock.acquire()

    robustPrint(content)
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork.txt'):
        return []
    return open('doneWork.txt').read().split('\n')



def getListFromFile(fileName):
    originalList = open(fileName).read().split('\n')
    resultList = []
    for eachItem in originalList:
        if eachItem != '' and eachItem !='\n' and eachItem != '\r':
            resultList.append(eachItem)
    return resultList




def fetchallInfoForOneProduct(fatherDirName, url, isAMatch):
    print 'url is ' + url
    contentPage = getPageWithSpecTimes(2, url)
    #contentPage = open('page.html').read()

    if contentPage == None:
        writeToLog('cannot open page for one product,%s,%s' % (fatherDirName, url))
        return None
    titlePattern = re.compile(r'<title>(.+?)</title>')
    title = titlePattern.findall(contentPage)[0]
    if 'tmall' in title:    
        #对于天猫
        productNamePattern = re.compile(r'<meta name="keywords" content="([^"]+?)"/>')
        try:
            productName = productNamePattern.findall(contentPage)[0].strip(' ')
            productName = re.sub(' ', '', productName)
            productName = re.sub('/','&', productName)
            productName = re.sub(r'\\','&', productName)
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product name,%s,%s' % (fatherDirName, url))
            return None
        
        # if isAMatch == False:
        #     productDirName = os.path.join(furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8'))
        # else:
        #     productDirName = os.path.join(fatherDir, 'match', productName.decode('utf8'))

        

        productDirName = os.path.join(fatherDirName, productName.encode('gbk'))
        if not os.path.exists(productDirName):
            os.makedirs(productDirName)

        filehandler = open(os.path.join(productDirName, 'productInfo.txt'), 'w')
        filehandler.write(productName+'\n')

        #对于天猫，价格用defaultItemPrice去匹配，对于淘宝，则用tb-rmb-num去匹配
        pricePattern = re.compile(r'defaultItemPrice":"([^"]+?)"')
        try:
            price = pricePattern.findall(contentPage)[0]
        except Exception as ep:
            writeToLog('cannot find price in page,%s,%s' % (productDirName, url))
            return None

        filehandler.write('price:%s\n' % price)
        
        pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
        detailSection = pagesoup.find_all("ul", attrs={"id": "J_AttrUL"})[0]
        detailLiList = detailSection.find_all('li')
        for eachDetailLi in detailLiList:
            filehandler.write(eachDetailLi.string+'\n')
        filehandler.close()

        #robustPrint('done info for,%s,%s' % (fatherDirName, productName.decode('utf8')))

        picsUrlPattern = re.compile(r'<img src="([^"]+\.jpg)[^"]+" />')
        picsUrlList = picsUrlPattern.findall(contentPage)
        for i in range(len(picsUrlList)):
            picUrl = picsUrlList[i]
            picName = '%s.jpg' % i
            picPath = os.path.join(productDirName, picName)
            try:
                urllib.urlretrieve(picUrl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (productDirName, picUrl))
                continue

        if '搭配套餐' in contentPage and isAMatch == False:
            userIdPattern = re.compile(r' <meta name="microscope-data" content="[^"]+?userid=(\d+?)[^"]+?">')
            userId = userIdPattern.findall(contentPage)[0]
            itemId = url.split('=')[-1]
            newMatchJsonUrl = 'http://otds.alicdn.com/json/MMComponent.htm?&meal=1&userId=%s&itemId=%s' % (userId, itemId)
            
            try:
                resultJson = json.loads(urllib2.urlopen(newMatchJsonUrl).read().decode('gbk', 'ignore').encode('utf8'))
                mealItemsList = resultJson['data']['mealComponentBO']['mealItems']
                for eachItem in mealItemsList:
                    if int(eachItem['itemId']) != 0 and int(eachItem['itemId']) != int(itemId):
                        itemUrl = 'http://item.taobao.com/item.htm?&id=%s' % eachItem['itemId']
                        #fetchallInfoForOneProduct(furnitureType, style, itemUrl, True, productDirName)
                        fetchallInfoForOneProduct(os.path.join(productDirName, 'match'), itemUrl, True)
            except Exception as ep:
                pass


    else:
        #对于淘宝
        productNamePattern = re.compile(r'"title":"([^"]+?)"}')
        try:
            productName = productNamePattern.findall(contentPage)[0].strip(' ')
            productName = re.sub(' ', '', productName)
            productName = re.sub('/','&', productName)
            productName = re.sub(r'\\','&', productName)



        except Exception as ep:
            print ep.message
            writeToLog('cannot find product name,%s,%s' % (fatherDirName, url))
            return None
        #print 'productName is ' + productName.decode('utf8')
        #print fatherDirName, productName.decode('utf8')
        productDirName = os.path.join(fatherDirName, productName.encode('gbk'))
        if not os.path.exists(productDirName):
            os.makedirs(productDirName)
        
        filehandler = open(os.path.join(productDirName, 'productInfo.txt'), 'w')
        filehandler.write(productName+'\n')

        #对于天猫，价格用defaultItemPrice去匹配，对于淘宝，则用tb-rmb-num去匹配
        pricePattern = re.compile(r'<em class="tb-rmb-num">(.+?)</em>')
        try:
            price = pricePattern.findall(contentPage)[0]
        except Exception as ep:
            writeToLog('cannot find price in page,%s,%s' % (productDirName, url))
            return None

        filehandler.write('price:%s\n' % price)
        
        pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
        #<ul class="attributes-list">
        detailSection = pagesoup.find_all("ul", attrs={"class": "attributes-list"})[0]
        detailLiList = detailSection.find_all('li')
        for eachDetailLi in detailLiList:
            filehandler.write(eachDetailLi.string+'\n')
        filehandler.close()
        #robustPrint('done info for,%s,%s' % (fatherDirName, productName.decode('utf8')))

        #<img data-src="http://img04.taobaocdn.com/imgextra/i4/2011177078/TB2CelyaXXXXXXtXpXXXXXXXXXX_!!2011177078.jpg_50x50.jpg" src="http://gd4.alicdn.com/imgextra/i4/2011177078/TB2CelyaXXXXXXtXpXXXXXXXXXX_!!2011177078.jpg_50x50.jpg_.webp">
        picsUrlPattern = re.compile(r'<img data-src="([^"]+\.jpg)[^"]+" />')
        picsUrlList = picsUrlPattern.findall(contentPage)
        for i in range(len(picsUrlList)):
            picUrl = picsUrlList[i]
            picName = '%s.jpg' % i
            picPath = os.path.join(productDirName, picName)
            try:
                urllib.urlretrieve(picUrl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (productDirName, picUrl))
                continue

        if '搭配套餐' in contentPage and isAMatch == False :
            matchDir = os.path.join(productDirName, 'match')
            userIdPattern = re.compile(r' <meta name="microscope-data" content="[^"]+?userid=(\d+?)[^\d]')
            userId = userIdPattern.findall(contentPage)[0]
            itemId = url.split('=')[-1]
            newMatchJsonUrl = 'http://otds.alicdn.com/json/MMComponent.htm?&meal=1&userId=%s&itemId=%s' % (userId, itemId)
            
            try:
                resultJson = json.loads(urllib2.urlopen(newMatchJsonUrl).read().decode('gbk', 'ignore').encode('utf8'))
                mealItemsList = resultJson['data']['mealComponentBO']['mealItems']
                for eachItem in mealItemsList:
                    if int(eachItem['itemId']) != 0 and int(eachItem['itemId']) != int(itemId):
                        itemUrl = 'http://item.taobao.com/item.htm?&id=%s' % eachItem['itemId']
                        #fetchallInfoForOneProduct(furnitureType, style, itemUrl, True, productDirName)
                        fetchallInfoForOneProduct(os.path.join(productDirName, 'match'), itemUrl, True)
            except Exception as ep:
                pass

    robustPrint('done for,%s,%s' % (fatherDirName, productName))




doneWorkList = getDoneWork()

for filePart in os.walk('.'):
    if 'itemList.txt' in filePart[2]:
        robustPrint('itemList.txt in ' + filePart[0])
        if filePart[0] in doneWorkList:
            robustPrint('already done ' + filePart[0])
            continue
        
        filePath = os.path.join(filePart[0], 'itemList.txt')
        itemList = getListFromFile(filePath)

        for eachItem in itemList:
            #print 'eachItem ' + eachItem
            fetchallInfoForOneProduct(filePart[0], eachItem, False)

        writeDoneWork(filePart[0])