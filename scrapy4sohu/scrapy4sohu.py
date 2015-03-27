#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
import time
from bs4 import BeautifulSoup

socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

allPicsResultList = []

def loadProcess():
    carNum = 0
    try:
        carNum = int(open('process.txt').read())
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()
    return carNum

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
        print 'cannot print content'

    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()


     
def writeBrandAndTypeInfo():
    filehandler = open('newcarBrand.txt', 'w')
    mainPage = urllib2.urlopen('http://db.auto.sohu.com/photo/').read()
    #print mainPage
    #return

    pagesoup = BeautifulSoup(mainPage)
    #print pagesoup
    #return
    brandSection = pagesoup.find_all("li", class_='close_child')
    #print len(brandSection)
    for brand in brandSection:
        #print str(brand)
        #continue
        h4String = str(brand.h4)
        brandNamePattern = re.compile(r'</em>(.+?)<span>')
        brandName = brandNamePattern.findall(h4String)[0]
        carTypePattern = re.compile(r'<li><a href="(.+?)" id=".+?" target="content"><em></em>(.+?)<span>')
        #<li><a href="/model_2817/picture.shtml" id="m2817" target="content"><em></em>迷你巴士<span>(13)</span></a></li>
        carTypeList = carTypePattern.findall(str(brand))
        for carType in carTypeList:
            typeLink = 'http://db.auto.sohu.com' + carType[0]
            typeName = carType[1]
            filehandler.write('%s,%s,%s\n'%(brandName, typeName, typeLink))

    filehandler.close()


def loadCarBrandAndLink():
    CarInfoFile = open('newcarBrand.txt').read().split('\n')
    if '\n' in CarInfoFile:
        CarInfoFile.remove('\n')
    carInfoList=[]
    for i in range(len(CarInfoFile)):
        CarInfoPair = CarInfoFile[i].split(',')
        carInfoList.append((CarInfoPair[0], CarInfoPair[1], CarInfoPair[2]))
    #第一个存brand号，第二个存品牌，例如 brand_206 英菲尼迪
    return carInfoList




def processTypePicsUrl(brand, carType, url):
    try:
        mainPageRaw = urllib2.urlopen(url)
        mainPage = mainPageRaw.read().decode('GBK').encode('utf8')
        #print mainPageRaw.headers
    except Exception as ep:
        print 'cannot open,%s,%s,%s\n' % (brand, carType, url)
        return 
    #outPicsPattern = re.compile(r'外观')
    #此处设置的是寻找外观图，如果要寻找官方图也在此处改
    outPicsPattern = re.compile(r'<a href="(.+?)" title=".+?" >外观</a>\((\d+)\)<b class="sj">')
    try:
        outPicsNumAndLink = outPicsPattern.findall(mainPage)[0]
        firstPicUrl = outPicsNumAndLink[0]
        picsNum = int(outPicsNumAndLink[1])
        print 'out pics link is %s and num is %s' % (outPicsNumAndLink[0], outPicsNumAndLink[1])
    except Exception as ep:
        #print ep.message
        writeToLog('cannot find out pics for car,%s,%s,%s' % (brand, carType, url))
        return



    pageNum = (picsNum-1) / 40 + 1
    print 'pageNum is %s' % pageNum



    for i in range(pageNum):
        outPicsUrl = ''
        if i == 0:
            outPicsUrl = 'http://db.auto.sohu.com' + firstPicUrl
        else:
            outPicsUrl = 'http://db.auto.sohu.com' + firstPicUrl.replace('_t1000.shtml', '_t1000_%s.shtml'%(i+1))
        
        #print 'outPicsUrl is %s'  % outPicsUrl

        outPicsPage = urllib2.urlopen(outPicsUrl).read().decode('gb2312', 'ignore').encode('utf8')

        yearAndPicLinkPattern = re.compile(r'<img alt="([\d]{4}|[\d]{2})款.+?" src="([^"]+?)">')

        yearAndPicLinkList = yearAndPicLinkPattern.findall(outPicsPage)
        # if len(yearAndPicLinkList) == 0:
        #     twoDigitYearAndPicLinkPattern = re.compile(r'<img alt="([\d]{2})款" src="([^"]+?)">')
        #     yearAndPicLinkList = twoDigitYearAndPicLinkPattern.findall(outPicsPage)

        if len(yearAndPicLinkList) == 0:
            writeToLog('cannot find yearInfo pics,%s,%s,%s' % (brand,carType, outPicsUrl))
            continue

        for yearAndPicLink in yearAndPicLinkList:
            year = yearAndPicLink[0]
            if int(year) >=0 and int(year) <= 16:
                year = '20' + year
            elif int(year) >=2000 and int(year) <=2016:
                pass
            elif int(year) >=90 and int(year) <= 99:
                year = '19' + year
            else:
                writeToLog('cannot find yearinfo,%s,%s,%s,%s' % (brand, carType, year, outPicsUrl))
                continue

            bigPicUrl = yearAndPicLink[1].replace('_150', '_800')
            bigPicUrl = bigPicUrl.replace('/150/', '/800/')

            yearPath = os.path.join(brand, carType, year)
            if not os.path.exists(yearPath):
                os.makedirs(yearPath)
            filehandler = open(os.path.join(yearPath, 'picsUrlList.txt'), 'a')
            filehandler.write(bigPicUrl + '\n')
            filehandler.close()
    print 'done for %s,%s\n' % (brand, carType)









#carBrandList中第一个是链接，第二项的.decode('utf8')是品牌名
#carBrandList = getAllCarBrandAndLink()


#writeBrandAndTypeInfo()
#processTypePicsUrl('aa', 'sdf', 'http://db.auto.sohu.com/model_3196/picture.shtml')
#sys.exit()
#processTypePicsUrl('aa', 'sdf', 'http://db.auto.sohu.com/model_3196/picture.shtml')
#sys.exit()




carNum = loadProcess()
# if carNum == 0:
#     filehandler = open('log.txt','w')
#     filehandler.close()

print 'process is %s' % carNum
carBrandList = loadCarBrandAndLink()

#print len(carBrandList)
#sys.exit()

#carBrandDict={}
for i in range(carNum, len(carBrandList)):
    print 'processing %s\n' % i 
    setProcess(str(i)) 
    processTypePicsUrl(carBrandList[i][0], carBrandList[i][1], carBrandList[i][2])
    