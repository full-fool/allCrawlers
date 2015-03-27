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
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

#print dazhongList


def loadProcess():
    try:
        carBrandNum = int(open('newprocess.txt').read())
        return carBrandNum
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(process):
    filehandler = open('newprocess.txt', 'w')
    filehandler.write(process)
    filehandler.close()

#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
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
            elif decodeType == 3:
                html = urllib.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else:
                html = urllib.urlopen(url).read()
            break
        except Exception as ep:
            if alreadyTriedTimes < tryTimes - 1:
                alreadyTriedTimes += 1
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



#包含开始，也包含结束，表示行号
def loadCarBrandTypeAndLink():
    CarInfoFile = open('newbrandlist.txt').read().split('\n')
    if '\n' in CarInfoFile:
        CarInfoFile.remove('\n')
    if '' in CarInfoFile:
        CarInfoFile.remove('')
    carInfoList=[]
    for i in range(len(CarInfoFile)):
        CarInfoPair = CarInfoFile[i].split('_')
        carInfoList.append((CarInfoPair[0], CarInfoPair[1], CarInfoPair[2]))

    
    #第一个存品牌，第二个存车型，第三个存链接
    return carInfoList




def getAllCarTypeListFromNet():
    mainPage = getPageWithSpecTimes(1, 'http://pic.auto.163.com/autopic/')
    pagesoup = BeautifulSoup(mainPage, from_encoding='utf8')
    brandSection = pagesoup.find_all("li", id=re.compile(r'[\d]+'))
    filehandler = open('newbrandlist.txt', 'w')
    for brandunit in brandSection:
        typePattern = re.compile(r'<h2 id="[0-9a-zA-Z]+?"><a href="(.+?) " target="_self">(.+?)</a></h2>')
        typeAndLinkList = typePattern.findall(str(brandunit))
        for typeAndLink in typeAndLinkList:      
            filehandler.write(brandunit.h2.find_all('a')[2].string+'_'+typeAndLink[1]+'_http://pic.auto.163.com'+typeAndLink[0]+'\n')
    filehandler.close()

def downloadPicsFromOnePage(carBrand,carType,url):
    print carBrand, carType
    mainPage = getPageWithSpecTimes(1, url)
    if mainPage == None:
        writeToLog('cannot open page,%s,%s,%s' % (carBrand, carType, url))
        return

    outPicsNumPattern = re.compile(r'<a target="_self" href=".+?">车身外观\((\d+)\)</a>')
    outPicsNumList = outPicsNumPattern.findall(mainPage)
    if len(outPicsNumList) == 0:
        writeToLog('cannot find out pics,%s,%s,%s' % (carBrand, carType, url))
        return
    outPicsNum = int(outPicsNumList[0])
    pageNum = (outPicsNum-1)/24+1
    #print 'page num is %s' % pageNum
    for i in range(pageNum):
        #此处如果是外观图，则用wg，如果是官方图，则用gf
        queryUrl = url.replace('ckindex', 'ckindexpage/gf')
        queryUrl = queryUrl.replace('.html', ',pageindex=%s.html' % i)
        eachPage = getPageWithSpecTimes(0, queryUrl)
        if eachPage == None:
            writeToLog('cannot one page for car,%s,%s,%s' % carBrand, carType, queryUrl)
            continue
        pagesoup = BeautifulSoup(eachPage, from_encoding='utf8')
        #brandSection = pagesoup.find_all("li", id=re.compile(r'[\d]+'))
        picsSectionList = pagesoup.find_all("li")
        for picsSection in picsSectionList:
            #print len(picsSection)
            carName = picsSection.find_all('a')[1].string
            carName = re.sub(r'\s','', carName)
            carDesp = picsSection.find('span').string
            yearPattern = re.compile(r'([\d]{4})款')
            if len(yearPattern.findall(carName.encode('utf8'))) != 0:
                year = yearPattern.findall(carName.encode('utf8'))[0]
            else:
                continue
            
            try:
                carPicUrl = picsSection.find_all('img')[0].get('src')
                carPicUrl = carPicUrl.replace('/t_', '/')
                #print carPicUrl
            except Exception as ep:
                print 'cannot find pic url'
                print ep.message
                continue
            #print carName
            if carDesp != None:
                carDesp = re.sub(r'\s','',carDesp)
                if len(carDesp) != 0:
                    carName = carName + carDesp
            newPath = os.path.join(carBrand, carType, year)
            if not os.path.exists(newPath):
                os.makedirs(newPath)
            filehandler = open(os.path.join(newPath, 'picsUrlList.txt'), 'a')
            filehandler.write(carPicUrl+','+carName+'\n')
            filehandler.close()




carInfoList = loadCarBrandTypeAndLink()
typeNum = loadProcess()
for i in range(typeNum, len(carInfoList)):
    setProcess(str(i))
    downloadPicsFromOnePage(carInfoList[i][0].decode('utf8'), carInfoList[i][1].decode('utf8'), carInfoList[i][2])



#downloadPicsFromOnePage('aa', 'bb', 'http://pic.auto.163.com/autopic/ckindex/topicid=293P0008,setid=0.html')
# a = '奥迪A82011款3.0TFSIquattro尊贵型(245KW)'
# yearPattern = re.compile(r'([\d]{4})款')
# print yearPattern.findall(a.encode('utf8'))


# 外观可能的链接

# http://pic.auto.163.com/autopic/ckindexpage/wg/topicid=29HC0008,setid=0,pageindex=0.html
# http://pic.auto.163.com/autopic/ckindex/topicid=29HC0008,setid=0.html
# http://pic.auto.163.com/autopic/ckindexpage/wg/topicid=29HC0008,setid=0,pageindex=2.html