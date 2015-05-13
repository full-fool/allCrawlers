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


def getStarFromForeground(text):
    fullStarPattern = re.compile(r'"icon icon-beach icon-star"')
    fullStarNum = len(fullStarPattern.findall(text))
    halfStarPattern = re.compile(r'icon icon-beach icon-star-half')
    halfStarNum = len(halfStarPattern.findall(text))
    return fullStarNum + 0.5 * halfStarNum

class DownloadPicsForOnePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, fatherDir, url):
        threading.Thread.__init__(self)
        self.fatherDir = fatherDir
        self.url = url

    def run(self):
        fatherDir = self.fatherDir
        url = self.url
        #print 'thread is running for,%s,%s,%s' % (city, district, url)

        fetchallInfoForOneHouse(fatherDir, url)
        print 'thread is done for,%s,%s' % (fatherDir,  url)





def fetchallInfoForOneHouse(fatherDir, url):
    #print 'url is ' + url
    contentPage = getPageWithSpecTimes(0, url)
    #contentPage = open('page.html').read()
    #https://www.airbnb.com/rooms/2183807?s=ohQX


    if contentPage == None:
        writeToLog('cannot open page for one house,%s' % (url))
        return None

    if not os.path.exists(fatherDir):
        os.makedirs(fatherDir)

    # title and address
    titlePattern = re.compile(r'<title>(.+?)</title>')
    title = titlePattern.findall(contentPage)[0]
    addressPattern = re.compile(r'<a href="#neighborhood" class="link-reset">(.+?)</a>')
    address = addressPattern.findall(contentPage)[0]
    #print 'title and address', title, address
    filehandler = open(os.path.join(fatherDir, 'info.txt'), 'w')
    filehandler.write('name and address:%s,%s\n' % (title, address))

    #对title和address作处理，一般是写入文件，字段名为 name and address

    # price
    pricePattern = re.compile(r'<div id="price_amount" itemprop="price" class="price-amount[^"]+?">\s+([\S]+)\s+</div>')
    price = pricePattern.findall(contentPage)[0]
    #print 'price', price
    filehandler.write('price:%s\n' % price)

    
    # amenities
    pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
    detailSection = pagesoup.find_all("div", attrs={"class": "row amenities"})[0]
    noItemList = []
    noItemListSection = detailSection.find_all("div", attrs={"class": "row-space-1 text-muted"})

    yesItemList = []
    yesItemListSection = detailSection.find_all("div", attrs={"class": "row-space-1 "})
    for each in yesItemListSection:
        #print each
        rawString = each.span.strong.get_text()
        yesItemList.append(rawString.strip(' ').strip('\n').strip(' '))

    
    for each in noItemListSection:
        rawString = str(each.span.find_all('del')[0].get_text())
        noItemList.append(rawString.strip(' ').strip('\n').strip(' '))

    #print 'yesItemList'
    #print yesItemList
    #print 'noItemList'
    #print noItemList
    filehandler.write('Amenities:\n')
    for yesItem in yesItemList:
        filehandler.write('%s:yes\n' % yesItem)
    for noItem in noItemList:
        filehandler.write('%s:no\n' % noItem)
    # yesItemList和noItemList中分别存储有的和没的东西

    


    # spaces
    spacePattern = re.compile(r'<div>([^><]+?)<strong>([^><]+?)</strong></div>')
    otherKindSpacePattern = re.compile(r'<div>([^><]+?)<strong><a href="[^"]+?" class="link-reset">([^><]+?)</a></strong></div>')
    accommodatesPattern = re.compile(r'[^>](Accommodates: )<strong>(\d+?)</strong>')
    spaceInfoList = spacePattern.findall(contentPage)
    spaceInfoList += otherKindSpacePattern.findall(contentPage)
    spaceInfoList += accommodatesPattern.findall(contentPage)
    #print 'spaceInfoList'
    #print spaceInfoList
    filehandler.write('The Spaces:\n')
    for spaceInfo in spaceInfoList:
        filehandler.write('%s:%s\n' % (spaceInfo[0], spaceInfo[1]))
    
    
    # descriptions
    try:
        descriptionSection = str(pagesoup.find_all("div", attrs={"class": "row description"})[0])
        pPattern = re.compile(r'<p>(.+?)</p>', re.S)
        rawPList = pPattern.findall(descriptionSection)
        description = '\n'.join(rawPList)
        description = re.sub(r'<br/>|<strong>|</strong>', '', description)
        #print 'description'
        #print description
        filehandler.write('Description:\n')
        filehandler.write(description+'\n')
    except Exception as ep:
        pass

    

    # pics
    picsInfoSection = str(pagesoup.find_all("meta", attrs={"id": "_bootstrap-room_options"})[0])
    picsInfoSection = picsInfoSection.replace('&quot;', '"')
    picsInfoSection = picsInfoSection.replace('amp;', '')
    #print 'picsInfoSection', picsInfoSection
    picsInfoPattern = re.compile(r'{"caption":"(.+?)",.+?"url":"([^"]+?)",.+?}')
    picsInfoList = picsInfoPattern.findall(picsInfoSection)

    # resultPicList = []
    # for picsInfo in picsInfoList:
    #     resultPicList.append((picsInfo[0], re.sub('amp;', '', picsInfo[1])))
    #print 'picsInfo'
    #print picsInfoList
    #print 'there are %s pics in all' % len(picsInfoList)

    filehandler.write('picDescription:\n')
    for i in range(len(picsInfoList)):
        picName = '%s.jpg' % i
        picPath = os.path.join(fatherDir, picName)
        try:
            urllib.urlretrieve(picsInfoList[i][1], picPath)
            filehandler.write('%s.jpg:%s\n' % (i, picsInfoList[i][0]))
        except Exception as ep:
            writeToLog('cannot download pic,%s,%s' % (picPath, picsInfoList[i][1]))





    # review and star
    #<h4 class="row-space-4 text-center-sm">
    ratingSection = pagesoup.find_all("h4", attrs={"class": "row-space-4 text-center-sm"})[1]
    rawReviewText = ratingSection.get_text().strip(' ').strip('\n').strip(' ')
    if 'No Reviews Yet' in rawReviewText:
        reviewNumber = 0
    #print 'rawReviewText is', rawReviewText
    else:
        reviewNumber =  int(re.sub(r'\D', '', rawReviewText))
    try:
        foregroundStarSection = ratingSection.find_all('div', attrs={"class":"foreground"})[0]
        starNumber = getStarFromForeground(str(foregroundStarSection))
    except Exception as ep:
        starNumber = 0
    

    #print 'reviewNumber, starNumber', reviewNumber, starNumber
    filehandler.write('reviewNumber:%s\nstarRating:%s' % (reviewNumber, starNumber))
    filehandler.close()
    writeDoneWork(fatherDir)












#fetchallInfoForOneHouse('this', 'https://www.airbnb.com/rooms/2326308?s=Y2Ga')
#sys.exit()
threadNum = 100
threadNumPool = {}

doneWorkList = getDoneWork()

for filePart in os.walk('.'):
    if 'houseUrlList.txt' in filePart[2]:
        robustPrint('houseUrlList.txt in ' + filePart[0])
        filePath = os.path.join(filePart[0], 'houseUrlList.txt')
        itemList = getListFromFile(filePath)

        for eachItem in itemList:
            
            apartmentIdPattern = re.compile(r'https://www\.airbnb\.com/rooms/(\d+)\?')
            apartmentId = apartmentIdPattern.findall(eachItem)[0]
            apartmentPath = os.path.join(filePart[0], apartmentId)
            if str(apartmentPath) in doneWorkList:
                print 'already done ' + str(apartmentPath)
                continue

            
            findThread = False
            while findThread == False:
                for k in range(threadNum):
                    if not threadNumPool.has_key(k):
                        threadNumPool[k] = DownloadPicsForOnePeople(apartmentPath, eachItem)
                        threadNumPool[k].start()
                        findThread = True
                        break
                    else:
                        if not threadNumPool[k].isAlive():
                            #threadNumPool[j].stop()
                            threadNumPool[k] = DownloadPicsForOnePeople(apartmentPath, eachItem)
                            threadNumPool[k].start()
                            findThread = True
                            break
                if findThread == False: 
                    time.sleep(5)