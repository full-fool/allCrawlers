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
            if decodeType == 1:
                html = urllib2.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib2.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            else:
                html = urllib2.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
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

def writeMapping(url, path):

    filehandler = open('Mapping.csv', 'a')
    filehandler.write(url+','+path+',\n')
    filehandler.close()

#一共159种品牌
def getAllCarBrandAndLink():
    carlistLink = 'http://price.pcauto.com.cn/cars/'
    page = getPageWithSpecTimes(1, carlistLink)
    pagesoup = BeautifulSoup(page, from_encoding='utf8')
    divList = pagesoup.find_all('div', class_='dFix')
    carList = []
    filehandler = open('carBrand.txt', 'a')
    for div in divList:
        filehandler.write(div.a.get('href')+','+div.p.string.decode('utf8')+'\n')
    filehandler.close()

#包含开始，也包含结束，表示行号
def loadCarBrandAndLink():
    CarInfoFile = open('carBrandPicPage.txt').read().split('\n')
    if '\n' in CarInfoFile:
        CarInfoFile.remove('\n')
    carInfoList=[]
    for i in range(len(CarInfoFile)):
        CarInfoPair = CarInfoFile[i].split(',')
        carInfoList.append((CarInfoPair[0], CarInfoPair[1]))
    
    #第一个存链接，第二个存品牌
    return carInfoList

#√,返回第一个是链接，第二个是车型
def getAllTypesFromLink(brand, url):
    #print brand
    brand = brand.strip(' ')
    brandMainPage = getPageWithSpecTimes(1, url)
    if brandMainPage == None:
        writeToLog('cannot open main page for one brand,%s,%s' % (brand, url))
        return None

    pagesoup = BeautifulSoup(brandMainPage, from_encoding='utf8')
    linkList = []
    iList = pagesoup.find_all("ul", attrs={"class": "ulPic ulPic-b clearfix"})
    for eachClass in iList:
        itemList  = eachClass.find_all("li")
        for item in itemList:
            linkList.append((item.a.get('href'), item.p.get('title').decode('utf8')))

    for linkitem in linkList:
        print linkitem[0], linkitem[1].decode('utf8')

    return linkList



#这个list中全是图片的链接
def downloadAllPicsForAList(brand, carType, outPicLinkList):
    for link in outPicLinkList:
        year = link[1]
        bigPicUrl = link[0]
        stopOrNot = link[2]
        newPath = os.path.join(brand.decode('utf8'), carType.decode('utf8'), year)
        if not os.path.exists(newPath):
            os.makedirs(newPath)

        filehandler = open(os.path.join(newPath, 'picsUrlList.txt'), 'a')
        filehandler.write(bigPicUrl+','+str(stopOrNot)+'\n')
        filehandler.close()



def getPicsForOneType(brand, carType, url):
    brand = brand.strip(' ')
    carType = carType.strip(' ')
    typeMainPage = getPageWithSpecTimes(1, url)
    if typeMainPage == None:
        writeToLog('cannot open main page for one brand,%s,%s,%s' % (brand,carType, url))
        return None
    #step1，搞定所有在售、未售车型
    #<a href="http://price.pcauto.com.cn/cars/s11302-o1/">2013款</a>
    yearLinkPattern = re.compile(r'<a href="([^"]+?)">([\d]{4})款</a>')
    yearLinkList = yearLinkPattern.findall(typeMainPage)
    #print yearLinkList

    #存储图片链接和年款信息
    linkList = []

    #在售、未售车型中没有年款选项
    if len(yearLinkList) == 0:
        pageNum = 1
        while 1:
            pageNum += 1
            outPicsUrl = url[:-1] + '-o1-1-10/p%s.html' % pageNum
            picsMainPage = getPageWithSpecTimes(1, outPicsUrl)
            if picsMainPage == None:
                writeToLog('cannot open out pics page for brand and type,%s,%s,%s' % (brand, carType, outPicsUrl))
            elif '当前车系暂无实拍图片' in picsMainPage:
                pass
            else:
                pagesoup = BeautifulSoup(picsMainPage, from_encoding='utf8')
                ulList = pagesoup.find_all("ul", attrs={"class": "ulPic ulPic-180 clearfix"})
                for eachClass in ulList:
                    itemList  = eachClass.find_all("li")
                    for item in itemList:
                        picLink = item.img.get('data-src')
                        desp = item.p.string
                        if picLink == None or desp == None:
                            continue
                        yearPattern = re.compile(r'([\d]{4})款')
                        yearList = yearPattern.findall(desp)
                        if len(yearList) != 0:
                            linkList.append((picLink, yearList[0], 0))
            if not '下一页' in picsMainPage:
                break

    else:
        pageNum = 0
        while 1:
            pageNum += 1
            for yearLink in yearLinkList:
                outPicsUrl = yearLink[0][:-1] + '-1-10/p%s.html' % pageNum
                #print 'outPicsUrl is ' + outPicsUrl
                picsMainPage = getPageWithSpecTimes(1, outPicsUrl)
                if picsMainPage == None:
                    writeToLog('cannot open out pics page for brand and type,%s,%s,%s' % (brand, carType, outPicsUrl))
                elif '当前车系暂无实拍图片' in picsMainPage:
                    pass
                else:
                    pagesoup = BeautifulSoup(picsMainPage, from_encoding='utf8')
                    ulList = pagesoup.find_all("ul", attrs={"class": "ulPic ulPic-180 clearfix"})
                    for eachClass in ulList:
                        itemList  = eachClass.find_all("li")
                        for item in itemList:
                            picLink = item.img.get('data-src')
                            desp = item.p.string
                            if desp == None or picLink == None:
                                continue
                            yearPattern = re.compile(r'([\d]{4}).+?')
                            yearList = yearPattern.findall(desp)
                            if len(yearList) != 0:
                                linkList.append((picLink, yearList[0], 0))
            if not '下一页' in picsMainPage:
                break

    #停售车型中的年款
    if '停售车型' in typeMainPage:
        stopSaleMainPageUrl = url[:-1] + '-o2/'
        stopSaleMainPage = getPageWithSpecTimes(1, stopSaleMainPageUrl)
        if stopSaleMainPage == None:
            writeToLog('cannot open main page for stop sale for, one brand,%s,%s,%s' % (brand, carType, stopSaleMainPageUrl))
            return None

        yearLinkPattern = re.compile(r'<a href="([^"]+?)">([\d]{4})款</a>')
        yearLinkList = yearLinkPattern.findall(typeMainPage)
        if len(yearLinkList) == 0:
            pageNum = 0
            while 1:
                pageNum += 1 
                outPicsUrl = stopSaleMainPageUrl[:-1] + '-1-10/p%s.html' % pageNum
                picsMainPage = getPageWithSpecTimes(1, outPicsUrl)
                if picsMainPage == None:
                    writeToLog('cannot open out pics page for brand and type,%s,%s,%s' % (brand, carType, outPicsUrl))
                elif '当前车系暂无实拍图片' in picsMainPage:
                    pass
                else:
                    #http://price.pcauto.com.cn/cars/sg2313-o2-1-10/
                    pagesoup = BeautifulSoup(picsMainPage, from_encoding='utf8')
                    ulList = pagesoup.find_all("ul", attrs={"class": "ulPic ulPic-180 clearfix"})
                    for eachClass in ulList:
                        itemList  = eachClass.find_all("li")
                        for item in itemList:
                            picLink = item.img.get('data-src')
                            desp = item.p.string
                            if picLink == None or desp == None:
                                continue
                            yearPattern = re.compile(r'([\d]{4})款')
                            yearList = yearPattern.findall(desp)
                            if len(yearList) != 0:
                                linkList.append((picLink, yearList[0], 1))
                if not '下一页' in picsMainPage:
                    break
        else:
            pageNum = 0
            while 1:
                pageNum += 1
                for yearLink in yearLinkList:
                    outPicsUrl = yearLink[0][:-1] + '-1-10/p%s.html' % pageNum
                    picsMainPage = getPageWithSpecTimes(1, outPicsUrl)
                    if picsMainPage == None:
                        writeToLog('cannot open out pics page for brand and type,%s,%s,%s' % (brand, carType, outPicsUrl))
                    elif '当前车系暂无实拍图片' in picsMainPage:
                        pass
                    else:
                        pagesoup = BeautifulSoup(picsMainPage, from_encoding='utf8')
                        ulList = pagesoup.find_all("ul", attrs={"class": "ulPic ulPic-180 clearfix"})
                        for eachClass in ulList:
                            itemList  = eachClass.find_all("li")
                            for item in itemList:
                                picLink = item.img.get('data-src')
                                desp = item.p.string
                                if desp == None or picLink == None:
                                    continue
                                yearPattern = re.compile(r'([\d]{4}).+?')
                                yearList = yearPattern.findall(desp)
                                if len(yearList) != 0:
                                    linkList.append((picLink, yearList[0], 1))
                if not '下一页' in picsMainPage:
                    break

    resultList = []
    for eachlink in linkList:
        tempLink = eachlink[0].replace('_180x135', '_800x600')
        resultList.append((tempLink, eachlink[1], eachlink[2]))
    return resultList




carBrandList = loadCarBrandAndLink()
alreadyDoneCarBrandNum = loadProcess()



for i in range(alreadyDoneCarBrandNum, len(carBrandList)):
    setProcess(str(i))
    print carBrandList[i][1].decode('utf8') 
    carTypeList = getAllTypesFromLink(carBrandList[i][1].decode('utf8'), carBrandList[i][0])
    #sys.exit()
    if carTypeList == None:
        print 'cannot find carType for %s' % carBrandList[i][1].decode('utf8')
        continue
    if len(carTypeList) == 0:
         print 'cannot find carType for %s, the length is 0' % carBrandList[i][1].decode('utf8')
    for carType in carTypeList:
        try:
            print carType[1].decode('utf8')
        except Exception as ep:
            print ep.message
            pass
        resultLinkList = getPicsForOneType(carBrandList[i][1].decode('utf8'), carType[1].decode('utf8'), carType[0])
        downloadAllPicsForAList(carBrandList[i][1].decode('utf8'), carType[1].decode('utf8'),resultLinkList)

