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
        print 'wrong with the process.txt'
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
            print 'cannot get %s page for %s time' % (url, alreadyTriedTimes+1)
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
    
    filehandler = open('doneword_tuangouInfo.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneword_tuangouInfo.txt'):
        return []
    return open('doneword_tuangouInfo.txt').read().split('\n')






def getAllCities():
    url =  'http://www.dianping.com/beijing'
    pageContent = urllib.urlopen(url).read()
    filehandler = open('citiesList.txt', 'w')

    cityPattern = re.compile(r'onclick="pageTracker\._trackPageview\(\'dp_head_hotcity_(.+?)\'\);">(.+?)</a>')
    citiesList = cityPattern.findall(pageContent)
    for city in citiesList:
        if city[0] == 'hongkong':
            break
        print city[1].decode('utf8')
        filehandler.write('%s,%s\n'%(city[0], city[1]))
    print len(citiesList)
    filehandler.close()


def getCitiesInfo():
    citiesList = open('citiesList.txt').read().split('\n')
    resultList = []
    for eachCity in citiesList:
        resultList.append((eachCity.split(',')[0], eachCity.split(',')[1]))
    return resultList

def getFoodTypes(cityName, url):
    #pageContent = urllib.urlopen(url).read()
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open food page,%s,%s' % (cityName.decode('utf8'), url))
        return None

    foodTypeSectionPattern = re.compile(r'<div class="tg-nav-submenu">\s.+<h3><a href="/list/home-category_1">美食</a></h3>(.+?)</div>', re.S)
    foodTypeSection = foodTypeSectionPattern.findall(pageContent)[0]
    #print foodTypeSection
    #return
    foodTypeInfoPattern = re.compile(r'<a href="(/list/home-category_\d+)">(.+?)</a>')
    foodTypeInfoList = foodTypeInfoPattern.findall(foodTypeSection)
    resultFoodTypeList = []
    for eachFoodType in foodTypeInfoList:
        if eachFoodType[1].strip(' ') == '其他美食':
            continue
        foodTypeUrl = 'http://t.dianping.com' + eachFoodType[0] + '?desc=1&sort=sale'
        foodTypeName = eachFoodType[1].strip(' ')
        print foodTypeUrl, foodTypeName

    return resultFoodTypeList


def getEachShopLinkForOnePage(cityName, foodType, pageNum, url):
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for page,%s,%s,%s,%s' % (cityName.decode('utf8'), foodType.decode('utf8'), pageNum, url))
        return None
    #pageContent = urllib2.urlopen(url).read()
    #print pageContent
    shopIdPattern = re.compile(r'"s":(\d+)')
    shopIdList = shopIdPattern.findall(pageContent)
    shopUrlList = []
    for shopId in shopIdList:
        shopUrlList.append('http://www.dianping.com/shop/%s' % shopId)
    return shopUrlList






def fetchAllInfoForOneShop(city, foodType, ID, url):
    print url
    time.sleep(1)
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for one shop,%s,%s,%s' % (city.decode('utf8'), foodType.decode('utf8'), url))
        return None

    targetDir = os.path.join(city.decode('utf8'), foodType.decode('utf8'), ID)
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)
    filehandler = open(os.path.join(targetDir, 'info.txt'), 'w')
    filehandler.write('ID: %s\n' % ID)
    filehandler.write('url: %s\n' % (url))

    # get rating and write to file
    try:
        rateStarPattern = re.compile(r'<span class="star-rate">(.+?)</span>')
        rateStar = rateStarPattern.findall(pageContent)[0]

        filehandler.write('rating: %s\n' % rateStar)
    except Exception as ep:
        print ep.message
    filehandler.close()


    # get tuangou details
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    detailSection = pagesoup.find_all('div', attrs={'data-eval-config': '{"title":"团购详情","hippoSeq":3}'})[0]
    #print detailSection
    filehandler = open(os.path.join(targetDir, 'detail.html'), 'w')
    filehandler.write('<html><head><meta charset="UTF-8"/></head>')
    filehandler.write(str(detailSection))
    filehandler.write('</html>')
    filehandler.close()

    # get product introduction
    productIntroductionSection = None
    allDetailSection = pagesoup.find_all('div', attrs={'class':"detail"})
    for eachSection in allDetailSection:
        if '产品介绍'  in str(eachSection):
            productIntroductionSection = eachSection
            break

    dishNamePattern = re.compile(r'<p class="listitem">(.+?)</p>')
    dishList = dishNamePattern.findall(str(productIntroductionSection))

    imgSrcPattern = re.compile(r'<img lazy-src-load="([^"]+?)"/>')
    imgSrcList = imgSrcPattern.findall(str(productIntroductionSection))

    filehandler = open(os.path.join(targetDir, 'picUrl.txt'), 'w')
    if len(dishList) != len(imgSrcList):
        writeToLog('dish num and pic num doesn\'t match,%s,%s,%s,%s' % city, foodType, ID, url)
    for i in range(min(len(dishList), len(imgSrcList))):
        picUrl = imgSrcList[i]
        suffix = picUrl.split('.')[-1]
        picName = '%s.%s' % (i+1, suffix)
        filehandler.write('%s,%s,%s\n' % (dishList[i], picName, picUrl))
        # picPath = os.path.join(targetDir, picName)
        # try:
        #     urllib.urlretrieve(picUrl, picPath)
        # except Exception as ep:
        #     writeToLog('cannot download pic,%s,%s,%s,%s' % (city, foodType, ID, picUrl))

    
    filehandler.close()
    writeDoneWork('%s,%s,%s' % (city, foodType, ID))


    return True



#fetchAllInfoForOneShop('a', 'b', '5010342', 'http://t.dianping.com/deal/5010342')
#sys.exit()

citiesInfoList = getCitiesInfo()
for i in range(len(citiesInfoList)):
    cityName = citiesInfoList[i][1]
    cityCode = citiesInfoList[i][0]
    print cityName.decode('utf8')
    cityUrl = 'http://t.dianping.com/%s' % cityCode
    allFoodTypesAndLink = getFoodTypes(cityName, cityUrl)
    if allFoodTypesAndLink == None:
        writeToLog('allFoodTypesAndLink is None, process is,%s' % (i))
        continue

    for j in range(len(allFoodTypesAndLink)):
        foodType = allFoodTypesAndLink[j][1]
        print foodType.decode('utf8')

        for k in range(7):
            foodPageUrl = allFoodTypesAndLink[j][0] + 'p%s' % (k+1)
            shopListsForOnePage = getEachShopLinkForOnePage(cityName, foodType, k, foodPageUrl)
            if shopListsForOnePage == None:
                writeToLog('shopListsForOnePage is None, process is,%s,%s,%s' % (i,j,k))
                continue

            if len(shopListsForOnePage) == 0:
                break
            for z in range(len(shopListsForOnePage)):
                if '%s,%s,%s' % (cityName, foodType, shopListsForOnePage[z]) in doneWorkList:
                    print 'alread done %s,%s,%s' % (cityName, foodType, shopListsForOnePage[z])
                    continue
                result = fetchRecommendedDishes(cityName, foodType, shopListsForOnePage[z])
                if result == None:
                    writeToLog('fetchAllInfoForOneShop result is None, process is,%s,%s,%s,%s' % (i,j,k,z))
                else:
                    writeDoneWork('%s,%s,%s' % (cityName, foodType, shopListsForOnePage[z]))








