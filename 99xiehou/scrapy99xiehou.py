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


#一共159种品牌
startPage = loadProcess()
for i in range(startPage, 1419):
    setProcess(str(i))
    print 'start to process %s' % i
    
    queryUrl = 'http://99xiehou.lvbjp.com/Search/index/sex/%E7%94%B7/age_min/16/age_max/80/province/%E8%AF%B7%E9%80%89%E6%8B%A9%E7%9C%81%E4%BB%BD%E5%90%8D/city/%E8%AF%B7%E9%80%89%E6%8B%A9%E5%9F%8E%E5%B8%82%E5%90%8D/pic/1/p/' + str(i+1) + '.html' 
    onePage = getPageWithSpecTimes(0, queryUrl)
    #onePage = urllib.urlopen(queryUrl).read()
    if onePage == None:
        print 'cannot open page %s' % (i+1)
        writeToLog('cannot open page %s'%(i+1))
        continue
    print 'successfully get page %s' % (i+1)

    onePersonUrlPatten = re.compile(r'<a href="([^"]+?)">\[详情\]</a>')
    personUrlList = onePersonUrlPatten.findall(onePage)

    print 'there are %s people found' % len(personUrlList)
    if len(personUrl) == 0:
        print 'website had broken'
        sys.exit()
    for personUrl in personUrlList:
        compPersonUrl = 'http://99xiehou.lvbjp.com' + personUrl
        #onePersonPage = getPageWithSpecTimes(0, compPersonUrl)

        #onePersonPage = urllib.urlopen(compPersonUrl).read()
        onePersonPage = getPageWithSpecTimes(0, compPersonUrl)
        if onePersonPage == None:
            print 'cannot open page for person,%s' % compPersonUrl
            writeToLog('cannot open page for person,%s' % compPersonUrl)
            continue


        pagesoup = BeautifulSoup(onePersonPage, from_encoding='utf8')
        #divList = pagesoup.find_all('div', class_='dFix')
        try:
            totalPicSection = pagesoup.find_all('ul', id="vlightbox")[0]
        except Exception as ep:
            print 'cannot find pic section,%s' % compPersonUrl
            continue

        picSectionList = totalPicSection.find_all('li')
        if len(picSectionList) < 5:
            print 'there are %s pics found, not enough,%s' % (len(picSectionList), compPersonUrl)
            continue

        #get directory name
        personIdPattern = re.compile(r'/([^/]+?)\.html')
        try:
            personId = personIdPattern.findall(personUrl)[0]
        except Exception as ep:
            print 'cannot find personId in %s' % (compPersonUrl)
            continue
        #print 'person id is %s and personUrl is %s' % (personId, personUrl)
        #sys.exit()

        agePattern = re.compile(r'<th>年龄：</th><td>(\d+)岁</th></tr>')
        try:
            age = agePattern.findall(onePersonPage)[0]
        except Exception as ep:
            print 'cannot find age info in %s' % compPersonUrl
            continue

        print 'dir name is %s_%s_m' % (personId, age)
        if os.path.exists('%s_%s_m' % (personId, age)): 
            continue
        os.makedirs('%s_%s_m' % (personId, age))

        for j in range(len(picSectionList)):
            try:
                picurl = 'http://99xiehou.lvbjp.com' +  picSectionList[j].img.get('src')
                #print 'fetch pic %s' % picurl
            except Exception as ep:
                print 'cannot find pic url in page,%s' % compPersonUrl 
                continue
            picPath = os.path.join('%s_%s_m' % (personId, age), '%s.jpg' % j)
            try:
                urllib.urlretrieve(picurl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (picurl, compPersonUrl))





