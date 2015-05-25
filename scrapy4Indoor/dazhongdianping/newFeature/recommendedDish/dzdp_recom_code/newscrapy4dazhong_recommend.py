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
headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [headers]
urllib2.install_opener(opener)

def robustPrint(content):
    try:
        print content
    except Exception as ep:
        print ep.message




def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork_fetchRecommend', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork_fetchRecommend'):
        return []
    return open('doneWork_fetchRecommend').read().split('\n')





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
    filehandler = open('log_matchPicsFetcher.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


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

    foodTypesSectionPattern = re.compile(r'美食频道</a> .+?</div>',re.S)
    foodTypesAllList = str(foodTypesSectionPattern.findall(pageContent)[0])
    #print 'food section is ' + str(foodTypesAllList)
    foodTypePattern = re.compile(r'<a data-key="[\d]+" href="([^"]+?)">(.+?)</a>')
    foodTypeList = foodTypePattern.findall(foodTypesAllList)
    resultFoodTypeList = []
    for eachType in foodTypeList:
        if eachType[1].decode('utf8') == '其他':
            foodTypeList.remove(eachType)
            continue
        #print eachType[0], eachType[1].decode('utf8')
        resultFoodTypeList.append(('http://www.dianping.com' + eachType[0] + 'o2', eachType[1].strip(' ')))
    #print resultFoodTypeList
    #print len(resultFoodTypeList)
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


def getNameIdPic(fatherDir, url):
    url = 'http://www.dianping.com' + urllib.quote(url)
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        print 'cannot open extra shop,%s' % url
        return None
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    infoSection = pagesoup.find_all("div", attrs={"class": "info-name"})[0]
    IdAndNamePattern = re.compile(r'<a href="/shop/(\d+)">(.+?)</a>')
    IdAndName = IdAndNamePattern.findall(str(infoSection))[0]
    Id = IdAndName[0]
    Name = IdAndName[1]


    targetDir = os.path.join(fatherDir, Name.decode('utf8'))
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)
    filehandler = open(os.path.join(targetDir, 'info.txt'), 'w')
    filehandler.write('name:%s\nid:%s\nurl:%s'%(Name, Id, url))
    filehandler.close()

    try:
        picUrlSection = pagesoup.find_all("div", attrs={"class": "menu-pic-list"})[0]
    except Exception as ep:
        #print ep.message
        return

    #print picUrlSection
    #return 
    imgSrcPattern = re.compile(r'<a href="/photos/(\d+)" title="点击看大图"><img alt=.+?src="([^"]+?)" width=')

    imgSrcList = imgSrcPattern.findall(str(picUrlSection))

    imgList = []
    for eachImgSrc in imgSrcList:
        picUrl = eachImgSrc[1]
        bigPicUrl = picUrl.replace('240c180', '700x700')
        picId = eachImgSrc[0]
        picName = picId + '.jpg'
        imgList.append((picName, bigPicUrl))

    filehandler = open(os.path.join(targetDir, 'picList.txt'), 'w')
    for img in imgList:
        filehandler.write('%s,%s\n' % (img[0], img[1]))
    filehandler.close()



#getNameIdPic('.', '/shop/21564619/dish-煲仔饭')


def getMatch(fatherDir, url):
    url =  'http://www.dianping.com' + url
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        print 'cannot open %s' % url
        return None
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    try:
        sameDishSection = pagesoup.find_all("div", attrs={"class": "news-list"})[0]
    except Exception as ep:
        print 'cannot find samedish, url is %s' % url
        return
    #print 'in get match'
    #print sameDishSection
    eachLinkPattern = re.compile(r'<a href="([^"]+?)">.+?</a>')
    linkList = eachLinkPattern.findall(str(sameDishSection))
    for eachShopLink in linkList:
        getNameIdPic(fatherDir, eachShopLink)


def fetchRecommendedDishes(city, foodType, url):
    print url
    time.sleep(1)
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for one shop,%s,%s,%s' % (city.decode('utf8'), foodType.decode('utf8'), url))
        return None

    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')



    try:
        iList = str(pagesoup.find_all("div", attrs={"class": "breadcrumb"})[0])
    except Exception as ep:
        writeToLog('open main page for shop,%s,%s,%s'%(city.decode('utf8'),foodType.decode('utf8'),url))
        return None
    shopNamePattern = re.compile(r'<span>(.+?)</span>')
    try:
        shopName = shopNamePattern.findall(iList)[0].strip(' ')
    except Exception as ep:
        shopNamePattern = re.compile(r'<strong>(.+?)</strong>')
        shopName = shopNamePattern.findall(iList)[0]


        
    print 'url %s' % url
    recommendScriptSection = pagesoup.find_all("script", attrs={"class": "J-panels"})[0]
    recommendSectionPattern = re.compile(r'<p class="recommend-name">.+?</p>', re.S)
    recommendSection = recommendSectionPattern.findall(str(recommendScriptSection))[0]
    recomDishPattern = re.compile(r'<a class="item" href="([^"]+?)" target="_blank" title="([^"]+?)">')
    recomDishList = recomDishPattern.findall(recommendSection)
    for recomDish in recomDishList:
        matchDir = os.path.join(city.decode('utf8'), foodType.decode('utf8'), \
            shopName.decode('utf8'), 'match-dish', recomDish[1].decode('utf8'))
        getMatch(matchDir, urllib.quote(recomDish[0]))

    print 'done recommendedDish for %s' % url
    return True

doneWorkList = getDoneWork()

citiesInfoList = getCitiesInfo()
for i in range(len(citiesInfoList)):
    cityName = citiesInfoList[i][1]
    cityCode = citiesInfoList[i][0]
    print cityName.decode('utf8')
    cityUrl = 'http://www.dianping.com/%s' % cityCode
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










