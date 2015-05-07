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
            alreadyTriedTimes += 1
            if alreadyTriedTimes == 1:
                time.sleep(1)
            elif alreadyTriedTimes == 2:
                time.sleep(10)
            elif alreadyTriedTimes == 3: 
                time.sleep(60)
            else:
                return None
    return html

def writeToLog(content):
    writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log.txt', 'a')
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
        writeToLog('cannot open food page,%s,%s' % (cityName, url))
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
        resultFoodTypeList.append(('http://www.dianping.com' + eachType[0] + 'o2', eachType[1]))
    #print resultFoodTypeList
    #print len(resultFoodTypeList)
    return resultFoodTypeList

def getEachShopLinkForOnePage(cityName, foodType, pageNum, url):
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for page,%s,%s,%s,%s' % (cityName, foodType, pageNum, url))
        return None
    #pageContent = urllib2.urlopen(url).read()
    #print pageContent
    shopIdPattern = re.compile(r'"s":(\d+)')
    shopIdList = shopIdPattern.findall(pageContent)
    shopUrlList = []
    for shopId in shopIdList:
        shopUrlList.append('http://www.dianping.com/shop/%s' % shopId)
    return shopUrlList

def fetchAllInfoForOneShop(city, foodType, url):
    print url
    time.sleep(1)
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for one shop,%s,%s,%s' % (city, foodType, url))
        return None


    
    # get location and write to file
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    try:
        iList = str(pagesoup.find_all("div", attrs={"class": "breadcrumb"})[0])
    except Exception as ep:
        #print pageContent
        writeToLog('cannot open page for one shop,%s,%s,%s'%(city,foodType,url))
        return
    placeListPattern = re.compile(r'<a href=".+?" itemprop="url">\s+(\S+?)\s+</a>',re.S)
    placeList = placeListPattern.findall(iList)
    shopNamePattern = re.compile(r'<span>(.+?)</span>')
    shopName = shopNamePattern.findall(iList)[0]
    placeList.append(shopName)
    print shopName
    if not os.path.exists(os.path.join(city, foodType, shopName)):
        os.makedirs(os.path.join(city, foodType, shopName))
    filehandler = open(os.path.join(city, foodType, shopName, 'info.txt'), 'w')
    filehandler.write(shopName+'\n')
    filehandler.write('location: %s' % placeList[0])
    for i in range(1, len(placeList)):
        filehandler.write('->%s' % placeList[i])
        #print 'place is ' + placeList[i]
    filehandler.write('\n')
    print 'done locatioin for %s' % shopName

    # get rating and write to file
    try:
        filehandler.write('rating: ')
        ratingList = str(pagesoup.find_all("div", attrs={"class": "brief-info"})[0])
        starsPattern = re.compile(r'title="(.+?星商户)"')
        stars = starsPattern.findall(ratingList)[0]
        filehandler.write(stars+',')
        eachRatingPattern = re.compile(r'<span class="item">(.+?)</span>')
        eachRatingList = eachRatingPattern.findall(ratingList)
        for eachRating in eachRatingList:
            filehandler.write('%s,'%(eachRating))
    except Exception as ep:
        print ep.message
        pass
    filehandler.close()
    print 'down rating for %s' % shopName


    # all pics and tabs
    picPageUrl = url + '/photos'
    picPageContent = urllib2.urlopen(picPageUrl).read()
    picPagesoup = BeautifulSoup(picPageContent, from_encoding='utf8')
    allDlsInPage = picPagesoup.find_all("dl")
    dishesSection = None
    environmentSection = None
    for eachDl in allDlsInPage:
        if 'title="">菜(' in str(eachDl):
            dishesSection = str(eachDl)
        elif 'title="">环境(' in str(eachDl):
            environmentSection = str(eachDl)
    # process dish

    if dishesSection != None:
        # process each dish
        filehandler = open(os.path.join(city, foodType, shopName, 'dishPicUrlList.txt'), 'w')
        tagFileHandler = open(os.path.join(city, foodType, shopName, 'dishTag.txt'), 'w')

        dishNameAndLinkPattern = re.compile(r'<a href="(.+?)" onclick="pageTracker\._trackPageview.+?;" title="([^"]+?)\(')
        dishNameAndLinkList = dishNameAndLinkPattern.findall(dishesSection)
        time.sleep(1)
        for eachDish in dishNameAndLinkList:
            dishName = eachDish[1]
            dishUrl = 'http://www.dianping.com' + eachDish[0]
            dishPicPage = urllib2.urlopen(dishUrl).read()

            # get dish attributes here
            if 'class="picture-tag"' in dishPicPage:
                tagSectionPattern = re.compile(r'<div class="picture-tag">.+?</div>', re.S)
                tagSection =str(tagSectionPattern.findall(dishPicPage)[0])
                tagPattern = re.compile(r'<a target="_blank" href="[^"]+?" class="tag" onclick="[^"]+?">(.+?)</a>')
                tagList = tagPattern.findall(tagSection)
                tagFileHandler.write(dishName+':')
                for eachTag in tagList:
                    tagFileHandler.write(eachTag+',')
                tagFileHandler.write('\n')

            # get dishes pics here
            dishPicUrlPattern = re.compile(r'<img src="(.+?thumb\.jpg)"')
            dishPicUrlList = dishPicUrlPattern.findall(dishPicPage)
            currentPage = 1
            while '下一页' in dishPicPage:
                currentPage += 1
                dishUrl = 'http://www.dianping.com' + eachDish[0] + '?pg=%s' % currentPage
                dishPicPage = urllib2.urlopen(dishUrl).read()
                dishPicUrlList += dishPicUrlPattern.findall(dishPicPage)                
            for i in range(len(dishPicUrlList)):
                resultUrl = dishPicUrlList[i].replace('240c180', '700x700')
                picName = dishName + '%s.jpg' % (i+1)
                filehandler.write('%s,%s\n'%(picName, resultUrl))
        filehandler.close()
        tagFileHandler.close()

    else:
        writeToLog('cannot find pics of dishes in url,%s,%s,%s,%s' % (city, foodType, shopName, picPageUrl))

    print 'done all dishes for %s' % shopName
    

    #process enviconment
    if environmentSection != None:
        environFilehandler = open(os.path.join(city, foodType, shopName, 'environPicUrlList.txt'), 'w')
        environNameAndLinkPattern = re.compile(r'<a href="([^"]+?)" onclick="pageTracker\._trackPageview[^"]+?" title="([^"]+?)\(')
        environNameAndLinkList = environNameAndLinkPattern.findall(environmentSection)
        for eachEnviron in environNameAndLinkList:
            environName = eachEnviron[1]
            environUrl = 'http://www.dianping.com' + eachEnviron[0]
            environPicPage = urllib2.urlopen(environUrl).read()
            environPicUrlPattern = re.compile(r'<img src="(.+?thumb\.jpg)"')
            environPicUrlList = environPicUrlPattern.findall(environPicPage)
            currentPage = 1
            while '下一页' in environPicPage:
                currentPage += 1
                environUrl = 'http://www.dianping.com' + eachEnviron[0] + '?pg=%s' % currentPage
                environPicPage = urllib2.urlopen(environUrl).read()
                environPicUrlList += environPicUrlPattern.findall(environPicPage)
            for i in range(len(environPicUrlList)):
                resultUrl = environPicUrlList[i].replace('240c180', '700x700')
                picName = environName + '%s.jpg' % (i+1)
                environFilehandler.write('%s,%s\n' % (picName, resultUrl))
        environFilehandler.close()
    else:
        writeToLog('cannot find pics of environment in url,%s,%s,%s,%s' % (city, foodType, shopName, picPageUrl))
    print 'done all environment for %s' % shopName

    return True


citiesInfoList = getCitiesInfo()
for i in range(len(citiesInfoList)):
    cityName = citiesInfoList[i][1]
    cityCode = citiesInfoList[i][0]
    print cityName
    cityUrl = 'http://www.dianping.com/%s' % cityCode
    allFoodTypesAndLink = getFoodTypes(cityName, cityUrl)
    if allFoodTypesAndLink == None:
        writeToLog('allFoodTypesAndLink is None, process is,%s' % (i))
        continue
    for j in range(len(allFoodTypesAndLink)):
        foodType = allFoodTypesAndLink[j][1]
        print foodType
        for k in range(15):
            foodPageUrl = allFoodTypesAndLink[j][0] + 'p%s' % (k+1)
            shopListsForOnePage = getEachShopLinkForOnePage(cityName, foodType, k, foodPageUrl)
            if shopListsForOnePage == None:
                writeToLog('shopListsForOnePage is None, process is,%s,%s,%s' % (i,j,k))
                continue
            for z in range(len(shopListsForOnePage)):
                setProcess('%s,%s,%s,%s' % (i,j,k,z))
                result = fetchAllInfoForOneShop(cityName, foodType, shopListsForOnePage[z])
                if result == None:
                    writeToLog('fetchAllInfoForOneShop result is None, process is,%s,%s,%s,%s' % (i,j,k,z))








