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
        resultFoodTypeList.append(('http://www.dianping.com' + eachType[0] + 'o2', eachType[1]))
    #print resultFoodTypeList
    #print len(resultFoodTypeList)
    return resultFoodTypeList

def getEachShopLinkForOnePage(cityName, foodType, pageNum, url):
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for page,%s,%s,%s,%s' % (cityName.decode('utf8'), foodType.decode('utf8'), pageNum.decode('utf8'), url))
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
        writeToLog('cannot open page for one shop,%s,%s,%s' % (city.decode('utf8'), foodType.decode('utf8'), url))
        return None


    
    # get location and write to file
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    try:
        iList = str(pagesoup.find_all("div", attrs={"class": "breadcrumb"})[0])
    except Exception as ep:
        #print pageContent
        writeToLog('open main page for shop,%s,%s,%s'%(city.decode('utf8'),foodType.decode('utf8'),url))
        return None
    placeListPattern = re.compile(r'<a href=".+?" itemprop="url">\s+(\S+?)\s+</a>',re.S)
    placeList = placeListPattern.findall(iList)
    shopNamePattern = re.compile(r'<title>(.+?)电话,')
    shopName = shopNamePattern.findall(pageContent)[0]
    placeList.append(shopName)
    robustPrint(shopName.decode('utf8'))

    if not os.path.exists(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'))):
        os.makedirs(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8')))
    filehandler = open(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), 'info.txt'), 'w')
    filehandler.write(shopName+'\n')
    filehandler.write('location: %s' % placeList[0])
    for i in range(1, len(placeList)):
        filehandler.write('->%s' % placeList[i])
    filehandler.write('\n')
    robustPrint('done locatioin for %s' % shopName.decode('utf8'))

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
    filehandler.close()
    robustPrint('down rating for %s' % shopName.decode('utf8'))


    # all pics and tabs
    picPageUrl = url + '/photos'
    picPageContent = getPageWithSpecTimes(0, picPageUrl)
    if picPageContent == None:
        writeToLog('cannot open picPage for shop,%s,%s,%s,%s' % (city.decode('utf8'),foodType.decode('utf8'), shopName.decode('utf8'), picPageUrl))
        return None        
    #picPageContent = urllib2.urlopen(picPageUrl).read()
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
        filehandler = open(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), 'dishPicUrlList.txt'), 'w')
        tagFileHandler = open(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), 'dishTag.txt'), 'w')

        dishNameAndLinkPattern = re.compile(r'<a href="(.+?)" onclick="pageTracker\._trackPageview.+?;" title="([^"]+?)\(')
        dishNameAndLinkList = dishNameAndLinkPattern.findall(dishesSection)
        time.sleep(1)
        for eachDish in dishNameAndLinkList:
            dishName = eachDish[1]
            dishUrl = 'http://www.dianping.com' + eachDish[0]
            #dishPicPage = urllib2.urlopen(dishUrl).read()
            dishPicPage = getPageWithSpecTimes(0, dishUrl)
            if dishPicPage == None:
                writeToLog('cannot open one dish,%s,%s,%s,%s' % (city.decode('utf8'),foodType.decode('utf8'), shopName.decode('utf8'), dishUrl))
                continue
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
                #dishPicPage = urllib2.urlopen(dishUrl).read()
                dishPicPage = getPageWithSpecTimes(0, dishUrl)
                if dishPicPage == None:
                    writeToLog('cannot open spec page for one dish,%s,%s,%s,%s,%s' % \
                        (city.decode('utf8'),foodType.decode('utf8'), shopName.decode('utf8'),currentPage, dishUrl))
                    break
                dishPicUrlList += dishPicUrlPattern.findall(dishPicPage)                
            for i in range(len(dishPicUrlList)):
                resultUrl = dishPicUrlList[i].replace('240c180', '700x700')
                picName = dishName + '%s.jpg' % (i+1)
                filehandler.write('%s,%s\n'%(picName, resultUrl))
        filehandler.close()
        tagFileHandler.close()

    else:
        writeToLog('cannot find pics of dishes in url,%s,%s,%s,%s' % (city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), picPageUrl))

    robustPrint('done all dishes for %s' % shopName.decode('utf8'))


    #process enviconment
    if environmentSection != None:
        environFilehandler = open(os.path.join(city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), 'environPicUrlList.txt'), 'w')
        environNameAndLinkPattern = re.compile(r'<a href="([^"]+?)" onclick="pageTracker\._trackPageview[^"]+?" title="([^"]+?)\(')
        environNameAndLinkList = environNameAndLinkPattern.findall(environmentSection)
        for eachEnviron in environNameAndLinkList:
            environName = eachEnviron[1]
            environUrl = 'http://www.dianping.com' + eachEnviron[0]
            #environPicPage = urllib2.urlopen(environUrl).read()
            environPicPage = getPageWithSpecTimes(0, environUrl)
            if environPicPage == None:
                writeToLog('cannot open environ page for shop,%s,%s,%s,%s,%s' % \
                    (city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), environName.decode('utf8'), environUrl))
                continue
            environPicUrlPattern = re.compile(r'<img src="(.+?thumb\.jpg)"')
            environPicUrlList = environPicUrlPattern.findall(environPicPage)
            currentPage = 1
            while '下一页' in environPicPage:
                currentPage += 1
                environUrl = 'http://www.dianping.com' + eachEnviron[0] + '?pg=%s' % currentPage
                #environPicPage = urllib2.urlopen(environUrl).read()

                environPicPage = getPageWithSpecTimes(0, environUrl)
                if environPicPage == None:
                    writeToLog('cannot open environ page for shop,%s,%s,%s,%s,%s' % \
                        (city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), environName.decode('utf8'), environUrl))
                    break

                environPicUrlList += environPicUrlPattern.findall(environPicPage)
            for i in range(len(environPicUrlList)):
                resultUrl = environPicUrlList[i].replace('240c180', '700x700')
                picName = environName + '%s.jpg' % (i+1)
                environFilehandler.write('%s,%s\n' % (picName, resultUrl))
        environFilehandler.close()
    else:
        writeToLog('cannot find pics of environment in url,%s,%s,%s,%s' % (city.decode('utf8'), foodType.decode('utf8'), shopName.decode('utf8'), picPageUrl))
    robustPrint('done all environment for %s' % shopName.decode('utf8'))

    return True



citiesInfoList = getCitiesInfo()
process1, process2, process3, process4 = loadProcess()
for i in range(process1, len(citiesInfoList)):
    cityName = citiesInfoList[i][1]
    cityCode = citiesInfoList[i][0]
    robustPrint(cityName.decode('utf8')) 
    cityUrl = 'http://www.dianping.com/%s' % cityCode
    allFoodTypesAndLink = getFoodTypes(cityName, cityUrl)
    if allFoodTypesAndLink == None:
        writeToLog('allFoodTypesAndLink is None, process is,%s' % (i))
        continue

    if i == process1:
        jStartPoint = process2
    else:
        jStartPoint = 0
    for j in range(jStartPoint, len(allFoodTypesAndLink)):
        foodType = allFoodTypesAndLink[j][1]
        robustPrint(foodType.decode('utf8'))

        if i == process1 and j == process2:
            kStartPoint = process3
        else:
            kStartPoint = 0
        for k in range(kStartPoint, 7):
            foodPageUrl = allFoodTypesAndLink[j][0] + 'p%s' % (k+1)
            shopListsForOnePage = getEachShopLinkForOnePage(cityName, foodType, k, foodPageUrl)
            if shopListsForOnePage == None:
                writeToLog('shopListsForOnePage is None, process is,%s,%s,%s' % (i,j,k))
                continue

            if i == process1 and j == process2 and k == process3:
                zStartPoint = process4
            else:
                zStartPoint = 0
            for z in range(zStartPoint, len(shopListsForOnePage)):
                setProcess('%s,%s,%s,%s' % (i,j,k,z))
                result = fetchAllInfoForOneShop(cityName, foodType, shopListsForOnePage[z])
                if result == None:
                    writeToLog('fetchAllInfoForOneShop result is None, process is,%s,%s,%s,%s' % (i,j,k,z))








