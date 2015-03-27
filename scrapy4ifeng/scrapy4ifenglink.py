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
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3
allCarBrandNum = 159

def loadProcess():
    try:
       carBrandNum = int(open('process.txt').read())
       return carBrandNum
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()



#type 1,gb2312, 2,gbk, 3,GBK
def getPageWithSpecTimes(decodeType, url):
    global tryTimes
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
                html = urllib.urlopen(url).read()              
            elif decodeType == 1:
                html = urllib.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            else:
                html = urllib.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            break
        except Exception as ep:
            alreadyTriedTimes += 1
            if alreadyTriedTimes < tryTimes:
                time.sleep(200 * alreadyTriedTimes)
                print 'sleeping for %s secs now for %s' % (200*alreadyTriedTimes, url) 
                pass
            else:
                return None
    return html

def writeToLog(content):
    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()



#包含开始，也包含结束，表示行号
def loadCarBrandAndLink():
    CarInfoFile = open('carbrandinfo.txt').read().split('\n')
    if '\n' in CarInfoFile:
        CarInfoFile.remove('\n')
    carInfoList=[]
    for i in range(len(CarInfoFile)):
        CarInfoPair = CarInfoFile[i].split(',')
        carInfoList.append((CarInfoPair[0], CarInfoPair[1], CarInfoPair[2]))
    
    #第一个存品牌，第二个存车型，第三个存链接
    return carInfoList



def saveCarInfoFromNet():
    carinfo = open('carinfo.js').read()
    pagesoup = BeautifulSoup(carinfo, from_encoding='utf8')
    allCarBrandSection = pagesoup.find_all('dl', attrs={"class": 'nav-class-l nav-class-close'})
    filehandler = open('carbrandinfo.txt', 'w')
    for carBrandSection in allCarBrandSection:
        link = carBrandSection.find_all('a')[0].get('href')
        string = carBrandSection.find_all('a')[0]
        pattern = re.compile(r'</span>(.+?)<span')
        brandname = pattern.findall(str(string))[0]
        caridPattern = re.compile(r'/photo/b-(\d+)-1-1\.html')
        carid = caridPattern.findall(link)[0]
        jsQueryUrl = 'http://data.auto.ifeng.com/frag/priceInc/photo_%s.inc' % carid
        carpageresult = getPageWithSpecTimes(0, jsQueryUrl)
        carTypeInfoPattern = re.compile(r'<dd class=\'nav-class-md\' id=\'.+?\'><a href=\'(.+?)\'>(.+?)</a></dd>')
        carTypeInfoList = carTypeInfoPattern.findall(carpageresult)
        for carTypeInfo in carTypeInfoList:
            filehandler.write(brandname+',' + carTypeInfo[1] + ',http://data.auto.ifeng.com' + carTypeInfo[0]+'\n')
    filehandler.close()

def getPicLinkFromMainPage(carBrand, carType, url):
    print carBrand, carType
    typeMainPage = getPageWithSpecTimes(0, url)
    if typeMainPage == None:
        writeToLog('cannot open main page for car,%s,%s,%s' % (carBrand, carType, url))
        return 
    #<td width="150"><a href="/photo/pd-c-34248-1-0-0-1.html">外观(<em class="red">47</em>张)</a></td>
    outPicLinkPattern = re.compile(r'<td class="name"><a href=".+?">([\d]{4})款.+?</a></td>.+?td width="150"><a href="(.+?)">外观\(<em class="red">(\d+)</em>张\)</a></td>', re.S)
    outPicLinkInfoList = outPicLinkPattern.findall(typeMainPage)
    #print outPicLinkList
    for outPicInfoLink in outPicLinkInfoList:
        year = outPicInfoLink[0]
        newPath = os.path.join(carBrand, carType, year)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
        filehandler = open(os.path.join(newPath, 'picsUrlList.txt'), 'a')
        picsNum = int(outPicInfoLink[2])
        pageNum = (picsNum - 1) / 25 + 1
        for i in range(pageNum):
            outPicUrl = 'http://data.auto.ifeng.com' + outPicInfoLink[1]
            outPicUrl = outPicUrl[:-6]+str(i+1)+outPicUrl[-5:]
            #print outPicUrl
            picsMainPage = getPageWithSpecTimes(0, outPicUrl)
            if picsMainPage == None:
                writeToLog('cannot open some pics page,%s,%s,%s' % (carBrand, carType, outPicUrl))
                continue
            picsUrlPattern = re.compile(r'class="img"><img alt="[^"]+?" title="[^"]+?" src="(.+?)" width="135" height="90"></a>')
            picsUrlList =  picsUrlPattern.findall(picsMainPage)
            for picsUrl in picsUrlList:
                bigPicsUrl = picsUrl.replace('_1', '_5')
                filehandler.write(bigPicsUrl+'\n')
        filehandler.close()


carInfoList = loadCarBrandAndLink()
typeNum = loadProcess()
for i in range(typeNum, len(carInfoList)):
    setProcess(str(i))
    getPicLinkFromMainPage(carInfoList[i][0], carInfoList[i][1], carInfoList[i][2])




