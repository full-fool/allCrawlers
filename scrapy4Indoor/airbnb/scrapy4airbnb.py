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






        



class DownloadPicsForOnePeople(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, processi,processj,city, district, url):
        threading.Thread.__init__(self)
        self.city = city
        self.url = url
        self.district = district
        self.processi = processi
        self.processj = processj

    def run(self):
        district = self.district
        city = self.city
        url = self.url
        #print 'thread is running for,%s,%s,%s' % (city, district, url)

        getAllHouses(city, district, url)
        print 'thread is done for,%s,%s,%s,%s,%s' % (city, district, url, self.processi, self.processj)




def getCities():
    url = 'https://www.airbnb.com/locations'
    pageContent = getPageWithSpecTimes(0, url)
    locationsPattern = re.compile(r'<li>\s+?<a href="([^"]+?)">(.+?)</a>\s+?</li>')
    locationsList = locationsPattern.findall(pageContent)
    filehandler = open('citiesList.txt', 'w')
    for location in locationsList:
        filehandler.write('https://www.airbnb.com' + location[0] + ',' + location[1] + '\n')
    filehandler.close()


def getAllNeighbours(city, url):
    contentPage = getPageWithSpecTimes(0, url)
    if contentPage == None:
        writeToLog('cannot open page for city,%s,%s' % (city, url))
        return None
    pagesoup = BeautifulSoup(contentPage, from_encoding='utf8')
    neighbourHoodListSection = pagesoup.find_all('div', attrs={"class":"neighborhood-list section section-offset"})[0].find_all('li')

    districtList = []
    for eachNeighbour in neighbourHoodListSection:
        districtList.append(('https://www.airbnb.com'+eachNeighbour.a.get("href"), eachNeighbour.get_text()))
    print 'neighbourList for %s is done' % city
    return districtList

def getAllHouses(city, district, url):    
    contentPage = getPageWithSpecTimes(0, url)
    if contentPage == None:
        writeToLog('cnanot open page for district,%s,%s,%s' % (city, district, url))
        return None
    allPlacesPattern = re.compile(r'<a class="btn" id="listings_button" href="([^"]+?)" target="_blank">')
    allPlacesUrl = 'https://www.airbnb.com' + allPlacesPattern.findall(contentPage)[0]

    allHousesNum = 0
    allHouseUrlList = []
    for i in range(1,7):
        pageUrl = allPlacesUrl + '&page=%s' % i
        #print 'pageUrl is ' + pageUrl
        contentPage = getPageWithSpecTimes(0, pageUrl)
        if contentPage == None:
            writeToLog('cnanot open page for district for page,%s,%s,%s' % (city, district,i, pageUrl))
            continue

        #print contentPage
        #sys.exit()
        houseUrlPattern = re.compile(r'<a href="([^"]+?)" target="[^"]+?" class="media-photo media-cover">')
        houseUrlList = houseUrlPattern.findall(contentPage)
        #print houseUrlList

        if i == 6:
            allHouseUrlList += houseUrlList[:11]
        else:
            allHouseUrlList += houseUrlList
        
        if len(houseUrlList) < 18:
            break

    pathName = os.path.join(city, district)

    if not os.path.exists(pathName):
        os.makedirs(pathName)


    filehandler = open(os.path.join(city, district, 'houseUrlList.txt'),'w')
    for eachHouse in allHouseUrlList:
        filehandler.write('https://www.airbnb.com' + eachHouse+'\n')
    filehandler.close()






#getInfoForOneFurnitureType('水床', 'http://s.taobao.com/list?&atype=b&cat=50094063')

#resultList = getProductUrlForOnePage('a', 'b', '12', 'http://s.taobao.com/list?atype=b&cat=50040540&ppath=20608:76856228')
#fetchallInfoForOneProduct('gf', 'sa', 'http://item.taobao.com/item.htm?&id=43096084342', False, None)

#print unescape('出租车是否可运输:&nbsp;&#26159;')
#print decodeUnicode('<li title="&nbsp;&#25972;&#35013;">是否组装:&nbsp;&#25972;&#35013;</li>')
#furnitureList = getListFromFile('furnitureTypes.txt')
#citiesList = getListFromFile('citiesList.txt')
#getAllNeighbours('https://www.airbnb.com/locations/new-york')
#getAllHouses('new york', 'Windsor Terrace', 'https://www.airbnb.com/locations/new-york/windsor-terrace')

threadNum = 100
threadNumPool = {}

citiesList = getListFromFile('citiesList.txt')
for i in range(len(citiesList)):
    neighbourList = getAllNeighbours(citiesList[i][1], citiesList[i][0])
    if neighbourList == None:
        print 'cannot find neighbour, i is %s' % i
        continue
    for j in range(len(neighbourList)):
        findThread = False
        while findThread == False:
            for k in range(threadNum):
                if not threadNumPool.has_key(k):
                    threadNumPool[k] = DownloadPicsForOnePeople(i,j,citiesList[i][1], neighbourList[j][1], neighbourList[j][0])
                    threadNumPool[k].start()
                    findThread = True
                    break
                else:
                    if not threadNumPool[k].isAlive():
                        #threadNumPool[j].stop()
                        threadNumPool[k] = DownloadPicsForOnePeople(i,j,citiesList[i][1], neighbourList[j][1], neighbourList[j][0])
                        threadNumPool[k].start()
                        findThread = True
                        break
            if findThread == False: 
                time.sleep(5)
        #print '%s,%s done, %s,%s' % (citiesList[i][1], neighbourList[j][1], i, j)


sys.exit()


# for i in range(len(furnitureList)):
#     #getInfoForOneFurnitureType(furnitureList[i][0], url)

#     findThread = False
#     while findThread == False:
#         for j in range(threadNum):
#             if not threadNumPool.has_key(j):
#                 threadNumPool[j] = DownloadPicsForOnePeople(furnitureList[i][0], url)
#                 threadNumPool[j].start()
#                 findThread = True
#                 break
#             else:
#                 if not threadNumPool[j].isAlive():
#                     #threadNumPool[j].stop()
#                     threadNumPool[j] = DownloadPicsForOnePeople(furnitureList[i][0], url)
#                     threadNumPool[j].start()
#                     findThread = True
#                     break
#         if findThread == False: 
#             time.sleep(5)

