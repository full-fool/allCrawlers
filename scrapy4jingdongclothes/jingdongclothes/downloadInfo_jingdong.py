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

        getInfoForProduct(fatherDir, ID)
        print 'thread is done for,%s,%s' % (fatherDir,  ID)



def getNameAndPicUrl(fatherDir, fatherID, color, url):
    productMainPage = getPageWithSpecTimes(2, url)
    if productMainPage == None:
        writeToLog('cannot open page for color,%s,%s,%s, %s' % (fatherDir, fatherID, color, url))
        return


    pagesoup = BeautifulSoup(productMainPage, from_encoding='utf8')

    # get name
    nameSection = pagesoup.find_all("div", attrs={"id": 'name'})[0]
    productName = nameSection.h1.get_text()



    picUrlPattern = re.compile(r'<img class=\'img-hover\' alt=\'.+?\' src=\'(.+?)\' data-url=')
    picUrlList = picUrlPattern.findall(productMainPage)
    extraPicUrlPattern = re.compile(r'<img alt=\'.+?\' src=\'(.+?)\' data-url=')
    picUrlList += extraPicUrlPattern.findall(productMainPage)
    picUrlList = picUrlList[:2]
    resultPicUrlList = []
    for i in range(len(picUrlList)):
        bigPicUrl = picUrlList[i].replace('/n5/', '/n0/')
        resultPicUrlList.append(bigPicUrl)
    

    return productName, resultPicUrlList





def getInfoForProduct(fatherDir, ID):
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




    resultDict = {}
    # get url
    resultDict['url'] = url
    resultDict['info'] = {}
    resultDict['info']['topInfo'] = []


    # get name and first two pic
    if not os.path.exists(os.path.join(fatherDir, ID)):
        os.makedirs(os.path.join(fatherDir, ID))
    productName, firstTwoPic = getNameAndPicUrl(fatherDir, ID, 'this', url)

    resultDict['info']['name'] = productName
    
    resultDict['info']['urls'] = firstTwoPic

    for i in range(len(firstTwoPic)):
        picUrl = firstTwoPic[i]
        suffix = picUrl.split('.')[-1]
        picPath = os.path.join(fatherDir, ID, '%s.%s' % (i, suffix))
        try:
            urllib.urlretrieve(picUrl, picPath)
        except Exception as ep:
            writeToLog('cannot download pic for product,%s,%s,%s' % (fatherDir, ID, picUrl))



    # get detail info
    #形如 http://item.jd.com/1322433653.html 这样的网页布局
    if 'p-parameter-list' in productMainPage:
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'p-parameter-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return 
        allAttributes = detailSection.find_all('li')
        allAttributesList = {}
        for attribute in allAttributes:
            if attribute.string == None:
                if '店铺' in str(attribute):
                    allAttributesList['店铺'] = attribute.a.string
                else:
                    print 'unknown attribute, %s' % str(attribute)
            else:
                allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])
        resultDict['info']['detail'] = allAttributesList
        # for eachItem in allAttributesList:
        #     print eachItem, allAttributesList[eachItem]




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
        allAttributesList = {}
        for attribute in allAttributes:
            #厚度：普通
            allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])

        resultDict['info']['detail'] = allAttributesList

        # for eachItem in allAttributesList:
        #    print eachItem, allAttributesList[eachItem]

    # get top info
    allTopInfoItems = pagesoup.find_all('a', attrs={"clstag": re.compile(r'.+?mbNav.+?')})
    if len(allTopInfoItems) == 0:
        print 'no top info for url,%s' % url
    for eachTopItemInfo in allTopInfoItems:
        resultDict['info']['topInfo'].append(eachTopItemInfo.string)


    # price
    priceQueryUrl = 'http://p.3.cn/prices/get?skuid=J_%s' % ID
    try:
        price = json.load(urllib.urlopen(priceQueryUrl))[0]['p']
    except Exception as ep:
        writeToLog('cannot find price for product,%s,%s,%s' % (ID, url, priceQueryUrl))
    resultDict['info']['price'] = price


    # find color
    resultDict['products'] = []
    try:
        colorSection = pagesoup.find_all("div", attrs={"id": "choose-color"})[0]
        colorPattern = re.compile(r'<div class="item"><b></b><a href="([^"]+?)" title="([^"]+?)"><img')
        allColor = colorPattern.findall(str(colorSection))
        for eachColor in allColor:
            colorName = eachColor[1]
            colorUrl = eachColor[0]
            productName, firstTwoPic = getNameAndPicUrl(fatherDir, ID, colorName, colorUrl)
            addedDict = {}
            addedDict['name'] = productName
            addedDict['color'] = colorName
            addedDict['urls'] = firstTwoPic
            resultDict['products'].append(addedDict)
            colorPath = os.path.join(fatherDir, ID, colorName)
            if not os.path.exists(colorPath):
                os.makedirs(colorPath)
            
            for i in range(len(firstTwoPic)):
                picUrl = firstTwoPic[i]
                suffix = picUrl.split('.')[-1]
                picPath = os.path.join(colorPath, '%s.%s' % (i, suffix))
                try:
                    urllib.urlretrieve(picUrl, picPath)
                except Exception as ep:
                    writeToLog('cannot download pic for product and color,%s,%s,%s,%s' % (fatherDir, ID, colorName, picUrl))


    except Exception as ep:
        print ep.message
        pass



    filePath = os.path.join(fatherDir, ID, 'info.txt')
    filehandler = open(filePath, 'w')
    filehandler.write(json.dumps(resultDict, indent=4, ensure_ascii=False))
    filehandler.close()
    
    writeDoneWork(str(os.path.join(fatherDir, ID)))







threadNum = 100
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



