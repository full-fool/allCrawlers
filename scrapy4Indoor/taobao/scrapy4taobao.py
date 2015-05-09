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


cookies = 'cookies.txt'
cj = cookielib.LWPCookieJar(cookies)
cj.save()
headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
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
    writeLock.acquire()

    robustPrint(content)
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


def getListFromFile(fileName):
    originalList = open(fileName).read().split('\n')
    resultList = []
    for eachItem in originalList:
        resultList.append((eachItem.split(',')[0], eachItem.split(',')[1]))
    return resultList

def decodeUnicode(text):
    while '&nbsp;' in text:
        text = text.replace('&nbsp;', '')
    characterPattern = re.compile(r'(&#\d+?;)')
    while len(characterPattern.findall(text)) > 0:
        #print text
        characterInt = characterPattern.findall(text)[0]
        character = unichr(int(characterInt[2:-1]))
        text = text.replace(characterInt, character)
    return text

def getStylesForOneTypeFurniture(html):
    stylePattern = re.compile(r'title="([^"]+?)" data-ppath="(20608:\d+?)"')
    return stylePattern.findall(html)


def getProductUrlForOnePage(furnitureType,  contentPage):
    nidPattern = re.compile(r'{"nid":"(\d+?)"}')
    nidList = nidPattern.findall(contentPage)
    productUrlList = []
    for eachNid in nidList:
        productUrl = 'http://item.taobao.com/item.htm?&id=%s' % eachNid
        productUrlList.append(productUrl)
    #print '%s url found' % len(productUrlList)
    return productUrlList

def getInfoForOneFurnitureType(furnitureType, url):
    print 'in getinfo'
    pageContent = getPageWithSpecTimes(2,url)
    if pageContent == None:
        writeToLog('cannot open page for furnitureType,%s,%s' % (furnitureType.decode('utf8'), url))
        return None
    print 'fetch the page'
    styleList = getStylesForOneTypeFurniture(pageContent)

    productUrlList = getProductUrlForOnePage(furnitureType,  pageContent)
    if len(styleList) == 0:
        for i in range(2,10):
            newUrl = url+'&s=%s' % ((i-1) * 60)
            newPageContent = getPageWithSpecTimes(2, newUrl)
            if newPageContent == None:
                writeToLog('cannot open some page for furnitureType,%s,%s,%s' % (furnitureType.decode('utf8'), i, newUrl))
                continue
            addedList = getProductUrlForOnePage(furnitureType, newPageContent)
            if len(addedList) == 0:
                break
            if i == 9:
                productUrlList += addedList[:20]
            else:
                productUrlList += addedList
        if not os.path.exists(furnitureType.decode('utf8')):
            os.makedirs(furnitureType.decode('utf8'))
        filehandler = open(os.path.join(furnitureType.decode('utf8'), 'itemList.txt'), 'w')
        for eachProduct in productUrlList:
            filehandler.write(eachProduct+'\n')
        filehandler.close()
        print 'done for,%s' % (furnitureType.decode('utf8'))


    else:
        for eachStyle in styleList:
            productUrlList = []
            for i in range(1,10):
                newUrl = url + '&ppath=%s&s=%s' % (eachStyle[1], (i-1) * 60)
                #print 'new url is ' + newUrl
                newPageContent = getPageWithSpecTimes(2, newUrl)
                if newPageContent == None:
                    writeToLog('cannot open some page for furnitureType and style,%s,%s,%s,%s' % (furnitureType.decode('utf8'),eachStyle[0].decode('utf8'), i, newUrl))
                    continue
                addedList = getProductUrlForOnePage(furnitureType, newPageContent)
                if len(addedList) == 0:
                    break
                if i == 9:
                    productUrlList += addedList[:20]
                else:
                    productUrlList += addedList
                #print '%s url in all' % len(productUrlList)
        

            if not os.path.exists(os.path.join(furnitureType.decode('utf8'), eachStyle[0].decode('utf8'))):
                os.makedirs(os.path.join(furnitureType.decode('utf8'), eachStyle[0].decode('utf8')))
            filehandler = open(os.path.join(furnitureType.decode('utf8'), eachStyle[0].decode('utf8'), 'itemList.txt'), 'w')
            for eachProduct in productUrlList:
                filehandler.write(eachProduct+'\n')
            filehandler.close()   
            print 'done for,%s,%s' % (furnitureType.decode('utf8'), eachStyle[0].decode('utf8'))    

        



class DownloadPicsForOnePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, furnitureType, url):
        threading.Thread.__init__(self)
        self.furnitureType = furnitureType
        self.url = url

    def run(self):
        furnitureType = self.furnitureType
        url = self.url
        #print 'thread is running for %s,%s' % (furnitureType, url)
        getInfoForOneFurnitureType(furnitureType, url)



def fetchallInfoForOneProduct(furnitureType, style, url, isAMatch, fatherDir):
    contentPage = getPageWithSpecTimes(2, url)
    if contentPage == None:
        writeToLog('cannot open page for one product,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), url))
        return None

    titlePattern = re.compile(r'<title>(.+?)</title>')
    title = titlePattern.findall(contentPage)[0]
    if 'tmall' in title:    
        #对于天猫
        productNamePattern = re.compile(r'<meta name="keywords" content="([^"]+?)"/>')
        try:
            productName = productNamePattern.findall(contentPage)[0].strip(' ')
        except Exception as ep:
            writeToLog('cannot find product name,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), url))
            return None
        
        if isAMatch == False:
            productDirName = os.path.join(furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8'))
        else:
            productDirName = os.path.join(fatherDir, 'match', productName.decode('utf8'))
        if not os.path.exists(productDirName):
            os.makedirs(productDirName)
        
        filehandler = open(os.path.join(productDirName, 'productInfo.txt'), 'w')
        filehandler.write(productName+'\n')

        #对于天猫，价格用defaultItemPrice去匹配，对于淘宝，则用tb-rmb-num去匹配
        pricePattern = re.compile(r'defaultItemPrice":"([^"]+?)"')
        try:
            price = pricePattern.findall(contentPage)[0]
        except Exception as ep:
            writeToLog('cannot find price in page,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), url))
            return None

        filehandler.write('price:%s\n' % price)
        
        pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
        detailSection = pagesoup.find_all("ul", attrs={"id": "J_AttrUL"})[0]
        detailLiList = detailSection.find_all('li')
        for eachDetailLi in detailLiList:
            filehandler.write(eachDetailLi.string+'\n')
        filehandler.close()

        robustPrint('done info for,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8')))

        picsUrlPattern = re.compile(r'<img src="([^"]+\.jpg)[^"]+" />')
        picsUrlList = picsUrlPattern.findall(contentPage)
        for i in range(len(picsUrlList)):
            picUrl = picsUrlList[i]
            picName = '%s.jpg' % i
            picPath = os.path.join(productDirName, picName)
            try:
                urllib.urlretrieve(picUrl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8'), picUrl))
                continue

        if '搭配套餐' in contentPage and isAMatch == False:
            userIdPattern = re.compile(r' <meta name="microscope-data" content="[^"]+?userid=(\d+?)[^"]+?">')
            userId = userIdPattern.findall(contentPage)[0]
            itemId = url.split('=')[-1]
            newMatchJsonUrl = 'http://otds.alicdn.com/json/MMComponent.htm?&meal=1&userId=%s&itemId=%s' % (userId, itemId)
            resultJson = json.loads(urllib2.urlopen(newMatchJsonUrl).read().decode('gbk', 'ignore').encode('utf8'))
            mealItemsList = resultJson['data']['mealComponentBO']['mealItems']
            for eachItem in mealItemsList:
                if int(eachItem['itemId']) != 0 and int(eachItem['itemId']) != int(itemId):
                    itemUrl = 'http://item.taobao.com/item.htm?&id=%s' % eachItem['itemId']
                    fetchallInfoForOneProduct(furnitureType, style, itemUrl, True, productDirName)


    else:
        #对于淘宝
        productNamePattern = re.compile(r'"title":"([^"]+?)"}')
        try:
            productName = productNamePattern.findall(contentPage)[0].strip(' ')
        except Exception as ep:
            writeToLog('cannot find product name,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), url))
            return None
        
        if isAMatch == False:
            productDirName = os.path.join(furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8'))
        else:
            productDirName = os.path.join(fatherDir, 'match', productName.decode('utf8'))
        if not os.path.exists(productDirName):
            os.makedirs(productDirName)
        
        filehandler = open(os.path.join(productDirName, 'productInfo.txt'), 'w')
        filehandler.write(productName+'\n')

        #对于天猫，价格用defaultItemPrice去匹配，对于淘宝，则用tb-rmb-num去匹配
        pricePattern = re.compile(r'<em class="tb-rmb-num">(.+?)</em>')
        try:
            price = pricePattern.findall(contentPage)[0]
        except Exception as ep:
            writeToLog('cannot find price in page,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), url))
            return None

        filehandler.write('price:%s\n' % price)
        
        pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
        #<ul class="attributes-list">
        detailSection = pagesoup.find_all("ul", attrs={"class": "attributes-list"})[0]
        detailLiList = detailSection.find_all('li')
        for eachDetailLi in detailLiList:
            filehandler.write(eachDetailLi.string+'\n')
        filehandler.close()
        robustPrint('done info for,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8')))

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
                writeToLog('cannot download pic,%s,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8'), picUrl))
                continue

        if '搭配套餐' in contentPage and isAMatch == False :
            matchDir = os.path.join(productDirName, 'match')
            userIdPattern = re.compile(r' <meta name="microscope-data" content="[^"]+?userid=(\d+?)[^\d]')
            userId = userIdPattern.findall(contentPage)[0]
            itemId = url.split('=')[-1]
            newMatchJsonUrl = 'http://otds.alicdn.com/json/MMComponent.htm?&meal=1&userId=%s&itemId=%s' % (userId, itemId)
            resultJson = json.loads(urllib2.urlopen(newMatchJsonUrl).read().decode('gbk', 'ignore').encode('utf8'))
            mealItemsList = resultJson['data']['mealComponentBO']['mealItems']
            for eachItem in mealItemsList:
                if int(eachItem['itemId']) != 0 and int(eachItem['itemId']) != int(itemId):
                    itemUrl = 'http://item.taobao.com/item.htm?&id=%s' % eachItem['itemId']
                    fetchallInfoForOneProduct(furnitureType, style, itemUrl, True, productDirName)

    robustPrint('done for,%s,%s,%s' % (furnitureType.decode('utf8'), style.decode('utf8'), productName.decode('utf8')))



#getInfoForOneFurnitureType('水床', 'http://s.taobao.com/list?&atype=b&cat=50094063')

#resultList = getProductUrlForOnePage('a', 'b', '12', 'http://s.taobao.com/list?atype=b&cat=50040540&ppath=20608:76856228')
#fetchallInfoForOneProduct('gf', 'sa', 'http://item.taobao.com/item.htm?&id=43096084342', False, None)

#print unescape('出租车是否可运输:&nbsp;&#26159;')
#print decodeUnicode('<li title="&nbsp;&#25972;&#35013;">是否组装:&nbsp;&#25972;&#35013;</li>')
furnitureList = getListFromFile('furnitureTypes.txt')


threadNum = 70
threadNumPool = {}

for i in range(len(furnitureList)):
    url = 'http://s.taobao.com/list?&atype=b&cat=%s' % furnitureList[i][1]
    #getInfoForOneFurnitureType(furnitureList[i][0], url)

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadPicsForOnePeople(furnitureList[i][0], url)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadPicsForOnePeople(furnitureList[i][0], url)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)

