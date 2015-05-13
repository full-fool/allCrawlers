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

# cookiefile ="./cookies.txt"   
# cookies = cookielib.MozillaCookieJar(cookiefile)
# try:
#     """加载已存在的cookie，尝试此cookie是否还有效"""
#     cookies.load(ignore_discard=True, ignore_expires=True)
# except Exception:
# #        print Exception.message,e
#     """加载失败，说明从未登录过，需创建一个cookie kong 文件"""
#     cookies.save(cookiefile,ignore_discard=True, ignore_expires=True)

# """将cookie带入到open中"""
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies))





# cookieFile = urllib2.HTTPCookieProcessor()
# opener = urllib2.build_opener(cookieFile)
# opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.92 Safari/537.4')]
# urllib2.install_opener(opener)


cookies = 'cookies.txt'
cj = cookielib.LWPCookieJar(cookies)
cj.save()


headers = ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

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


def getStarFromForeground(text):
    fullStarPattern = re.compile(r'"icon icon-beach icon-star"')
    fullStarNum = len(fullStarPattern.findall(text))
    halfStarPattern = re.compile(r'icon icon-beach icon-star-half')
    halfStarNum = len(halfStarPattern.findall(text))
    return fullStarNum + 0.5 * halfStarNum

class DownloadPicsForOnePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, fatherDir, ID):
        threading.Thread.__init__(self)
        self.fatherDir = fatherDir
        self.ID = ID

    def run(self):
        fatherDir = self.fatherDir
        ID = self.ID
        #print 'thread is running for,%s,%s,%s' % (city, district, url)

        getInfoForProduct(fatherDir, ID, False)
        print 'thread is done for,%s,%s' % (fatherDir,  ID)





def getInfoForProduct(fatherDir, ID, isMatch):
    ID = str(ID)
    url = 'http://item.jd.com/%s.html' % ID
    print 'product url is ' + url
    productMainPage = getPageWithSpecTimes(2, url)
    if productMainPage == None:
        writeToLog('cannot open page,%s' % url)
        return

    if '京东网上商城' in productMainPage:
        writeToLog('url out of date,%s' % url)
        return

    pagesoup = BeautifulSoup(productMainPage, from_encoding='utf8')

    #resultDict['info']['detail'] = {}

    #getPics
    if not os.path.exists(os.path.join(fatherDir, ID)):
        os.makedirs(os.path.join(fatherDir, ID))
    picUrlPattern = re.compile(r'<img class=\'img-hover\' alt=\'.+?\' src=\'(.+?)\' data-url=')
    picUrlList = picUrlPattern.findall(productMainPage)
    extraPicUrlPattern = re.compile(r'<img alt=\'.+?\' src=\'(.+?)\' data-url=')
    picUrlList += extraPicUrlPattern.findall(productMainPage)
    print 'there are %s pics' % len(picUrlList)
    #bigPicUrlList = []
    for i in range(len(picUrlList)):
        #bigPicUrlList.append(eachPic.replace('/n5/', '/n0/'))
        bigPicUrl = picUrlList[i].replace('/n5/', '/n0/')
        picName = '%s.jpg' % i
        picPath = os.path.join(fatherDir, ID, picName)
        print 'picPath is %s' % picPath
        try:
            urllib.urlretrieve(bigPicUrl, picPath)
            print 
        except Exception as ep:
            writeToLog('cannot download pic for product,%s,%s,%s,%s' % (fatherDir, ID, picPath, bigPicUrl))





    descriptionPattern = re.compile(r'<meta name="keywords" content="(.+?)"/>')
    description = descriptionPattern.findall(productMainPage)[0]
    filehandler = open(os.path.join(fatherDir, ID, 'info.txt'), 'w')
    filehandler.write('product description:%s\n' % description)


    # get the price
    priceQueryUrl = 'http://p.3.cn/prices/get?skuid=J_%s' % ID
    try:
        price = json.load(urllib.urlopen(priceQueryUrl))[0]['p']
    except Exception as ep:
        writeToLog('cannot find price for product,%s,%s,%s' % (ID, url, priceQueryUrl))
    filehandler.write('price:%s\n' % price)


    #形如 http://item.jd.com/1322433653.html 这样的网页布局
    if 'p-parameter-list' in productMainPage:
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'p-parameter-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return 
        allAttributes = detailSection.find_all('li')
        allAttributesList = []
        for attribute in allAttributes:
           allAttributesList.append(attribute.get_text())
           filehandler.write(attribute.get_text() + '\n')



    #形如 http://item.jd.com/1411304215.html 这样的网页布局
    elif 'detail-list' in productMainPage:
        #print 'detail-list in page'
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'detail-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return
        allAttributes = detailSection.find_all('li')
        allAttributesList = []
        for attribute in allAttributes:
            allAttributesList.append(attribute.get_text())
            filehandler.write(attribute.get_text() + '\n')

    
    # process match
    if isMatch == False:
        matchUrl = "http://diviner.jd.com/diviner?lid=1&lim=6&uuid=%s&p=102001&sku=%s" % (ID, ID)
        matchJson = getPageWithSpecTimes(2, matchUrl)
        matchJsonResult = json.loads(matchJson)
        matchPath = os.path.join(fatherDir, ID, 'match')
        for eachItem in matchJsonResult['data']:
            #print eachItem['sku']
            getInfoForProduct(matchPath, eachItem['sku'], True)        


    writeDoneWork(str(os.path.join(fatherDir, ID)))






threadNum = 50
threadNumPool = {}

doneWorkList = getDoneWork()

for filePart in os.walk('.'):
    if 'itemList.txt' in filePart[2]:
        robustPrint('itemList.txt in ' + filePart[0])
        filePath = os.path.join(filePart[0], 'itemList.txt')
        itemList = getListFromFile(filePath)

        for eachItem in itemList:
            productPath = os.path.join(filePart[0], eachItem)
            if str(productPath) in doneWorkList:
                print 'already done ' + str(productPath)
                continue
            
            findThread = False
            while findThread == False:
                for k in range(threadNum):
                    if not threadNumPool.has_key(k):
                        threadNumPool[k] = DownloadPicsForOnePeople(filePart[0], eachItem)
                        threadNumPool[k].start()
                        findThread = True
                        break
                    else:
                        if not threadNumPool[k].isAlive():
                            #threadNumPool[j].stop()
                            threadNumPool[k] = DownloadPicsForOnePeople(filePart[0], eachItem)
                            threadNumPool[k].start()
                            findThread = True
                            break
                if findThread == False: 
                    time.sleep(5)



