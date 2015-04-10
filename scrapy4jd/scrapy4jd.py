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
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3



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
    tryTimes = 3
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
            alreadyTriedTimes += 1
            if alreadyTriedTimes < tryTimes:
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


def getListFromFile(fileName):
    namelist = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            namelist.append(line2)
    return namelist

def getInfoForProduct(url):
    try:
        productMainPage = urllib.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
    except Exception as ep:
        print ep.message
        writeToLog('cannot open page,%s' % url)
        return

    pagesoup = BeautifulSoup(productMainPage, from_encoding='utf8')

    #形如 http://item.jd.com/1322433653.html 这样的网页布局
    if 'p-parameter-list' in productMainPage:
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'p-parameter-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return 
        allAttributes = detailSection.find_all('li')
        allAttributesList = {}
        for attribute in allAttributes:
            if attribute.string == None:
                if '店铺' in str(attribute):
                    allAttributesList['店铺'] = attribute.a.string
                else:
                    print 'unknown attribute, %s' % str(attribute)
            else:
                allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])

        for eachItem in allAttributesList:
            print eachItem, allAttributesList[eachItem]




    #形如 http://item.jd.com/1411304215.html 这样的网页布局
    elif 'detail-list' in productMainPage:
        #print 'detail-list in page'
        try:
            detailSection = pagesoup.find_all("ul", attrs={"class": 'detail-list'})[0]
        except Exception as ep:
            print ep.message
            writeToLog('cannot find product detail for url,%s' % url)
            return
        allAttributes = detailSection.find_all('li')
        allAttributesList = {}
        for attribute in allAttributes:
            #厚度：普通
            allAttributesList[attribute.string.split('：')[0]] = '：'.join(attribute.string.split('：')[1:])

        for eachItem in allAttributesList:
           print eachItem, allAttributesList[eachItem]
        #print allAttributesList





getInfoForProduct('http://item.jd.com/1322433653.html')
sys.exit()



cookieFile = urllib2.HTTPCookieProcessor()
opener = urllib2.build_opener(cookieFile)
opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.92 Safari/537.4')]
urllib2.install_opener(opener)


startPage = loadProcess()
for i in range(startPage, 9683+1):
    setProcess(str(i))
    print 'start to process %s' % i
    
    queryUrl = 'http://www.lol99.com/online/?page=%s&type=1' % i 
    onePage = getPageWithSpecTimes(0, queryUrl)
    if onePage == None:
        #print 'cannot open page,%s' % queryUrl
        writeToLog('cannot open page,%s' % queryUrl)
        continue
    print 'successfully get page %s' % i

    onePersonUrlPatten = re.compile(r'<p class="xiangxi"><a href="([^"]+?)" target="_blank">详细信息>></a></p>')
    personUrlList = onePersonUrlPatten.findall(onePage)

    print 'there are %s people found' % len(personUrlList)
    for compPersonUrl in personUrlList:
        uidPattern = re.compile(r'\?uid=(\d+)')
        try:
            uid = uidPattern.findall(compPersonUrl)[0]
        except Exception as ep:
            print 'cannot find uid in %s' % compPersonUrl
            continue

        picsQueryUrl = 'http://www.lol99.com/member/photo_list.php?uid=%s' % uid
        picsInfoForOnePerson = getPageWithSpecTimes(0, picsQueryUrl)
        if picsInfoForOnePerson == None:
            writeToLog('cannot find pics info for,%s,%s' % (uid, picsQueryUrl))
            continue

        picsUrlPattern = re.compile(r'<img src="(http://head.+?)" /></a>')
        picsUrlList = picsUrlPattern.findall(picsInfoForOnePerson)
        if len(picsUrlList) < 5:
            print '%s pics found, not enough,%s' % (len(picsUrlList), uid)
            continue


        onePersonPage = getPageWithSpecTimes(0, compPersonUrl)
        if onePersonPage == None:
            print 'cannot open page for person,%s' % compPersonUrl
            writeToLog('cannot open page for person,%s' % compPersonUrl)
            continue


        rawGenderPattern = re.compile(r'<span>性别：(.+?)</span>')
        gender = 0
        try:
            rawGender = rawGenderPattern.findall(onePersonPage)[0]
            if rawGender == '男':
                gender = 'm'
            elif rawGender == '女':
                gender = 'f'
            else:
                print 'raw gender is %s' % rawGender
                continue
        except Exception as ep:
            writeToLog('cannot find gender info,%s' % compPersonUrl)
            continue

        agePattern = re.compile(r'<span>年龄：(\d+)岁</span>')
        try:
            age = agePattern.findall(onePersonPage)[0]
        except Exception as ep:
            writeToLog('cannot find age info,%s' % compPersonUrl)
            continue



        print 'dir name is %s_%s_%s' % (uid, age, gender)

        if not os.path.exists('%s_%s_%s' % (uid, age, gender)):
            os.makedirs('%s_%s_%s' % (uid, age, gender))

        for j in range(len(picsUrlList)):
            picurl = picsUrlList[j].replace('_slt', '_y')
            picPath = os.path.join('%s_%s_%s' % (uid, age, gender), '%s.jpg' % j)
            try:
                #urllib.urlretrieve(picurl, picPath)
                picContent = urllib2.urlopen(picurl).read()
                filehandler = open(picPath, 'wb')
                filehandler.write(picContent)
                filehandler.close()
                print 'pic url is %s\n' % picurl
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s\n' % (picurl, compPersonUrl))





