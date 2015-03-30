#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
import cookielib
import time
import threading
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()


def loadProcess():
    try:
        infoList = open('process.txt').read().split(',')
        #carBrandNum = int(open('process.txt').read())
        return int(infoList[0]), int(infoList[1]), int(infoList[2])
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(firstArg, secondArg, thirdArg):
    filehandler = open('process.txt', 'w')
    filehandler.write(firstArg+','+secondArg+','+thirdArg)
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
            if alreadyTriedTimes < tryTimes - 1:
                alreadyTriedTimes += 1
                pass
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

    writeLock.close()

def getProvinceAndDistrictCouple():
    filelines = open('provinceinfo.txt').read().split('\n')
    infoList = []
    for line in filelines:
        infoList.append((line.split(',')[0], line.split(',')[1]))
    return infoList




class DownloadPicsForOnePerson(threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        compPersonUrl = self.url
        print 'compPersonUrl is %s' % compPersonUrl
        onePersonPage = urllib2.urlopen(compPersonUrl).read().decode('GBk', 'ignore').encode('utf8')
        time.sleep(1)
        onePersonPage = urllib2.urlopen(compPersonUrl).read().decode('GBk', 'ignore').encode('utf8')
        if '珍爱网注册' in onePersonPage:
            print 'force to sign in'
            sys.exit()

        picUrlPattern = re.compile(r'<img class="hidden" src="(.+?)">')
        picUrlList = picUrlPattern.findall(onePersonPage)
        print 'there are %s pics for person %s' % (len(picUrlList), compPersonUrl)

        if len(picUrlList) < 5:
            print 'no enough pics for one person,%s' % compPersonUrl
            return

        memberIdPattern = re.compile(r'memberid=(\d+)')
        memberId = memberIdPattern.findall(compPersonUrl)[0]

        agePattern = re.compile(r'今年<strong class="c_01">(\d+)岁</strong>')
        age = agePattern.findall(onePersonPage)[0]

        print 'dir name is %s_%s_f' % (memberId, age)

        if not os.path.exists('%s_%s_f' % (memberId, age)):
            os.makedirs('%s_%s_f' % (memberId, age))

        picPath = os.path.join('%s_%s_f' % (memberId, age), 'picsUrlList.txt')
        filehandler = open(picPath, 'a')
        for eachPicUrl in picUrlList:
            picurl = eachPicUrl.replace('_3', '_6')
            filehandler.write(picurl+'\n')
        filehandler.close()

        #print 'pics done for person %s\n' % compPersonUrl




cookies = 'cookies.txt'
cj = cookielib.LWPCookieJar(cookies)
cj.save()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)



threadNum = 100
threadNumPool = {}

startPoint, lastAge, lastPageNum = loadProcess()

# print startPoint
# print lastAge
# print lastPageNum
# sys.exit()
provinceAndDistrictCodeList = getProvinceAndDistrictCouple()
for i in range(startPoint, len(provinceAndDistrictCodeList)):
    for age in range(lastAge, 80):
        for pageNum in range(lastPageNum, 51):
            setProcess(str(i), str(age), str(pageNum))
            queryUrl = 'http://search.zhenai.com/search/getfastmdata.jsps?gender=1&agebegin=%s\
                &ageend=%s&workcityprovince=%s&workcitycity=%s&photo=1&currentpage=%s' % (age, age, \
                provinceAndDistrictCodeList[i][0], provinceAndDistrictCodeList[i][1], pageNum)

            onePage = getPageWithSpecTimes(3, queryUrl)
            if onePage == None:
                print 'cannot open page,%s' % (queryUrl)
                writeToLog('cannot open page,%s'%(queryUrl))
                continue
            if '非常抱歉' in onePage:
                break
            print 'successfully get page %s' % (i+1)
            onePersonUrlPatten = re.compile(r'<a class="search_user_name" href="([^"]+?)" title="')
            personUrlList = onePersonUrlPatten.findall(onePage)
            for compPersonUrl in personUrlList:                
                findThread = False
                while findThread == False:
                    for j in range(threadNum):
                        if not threadNumPool.has_key(j):
                            threadNumPool[j] = DownloadPicsForOnePerson(compPersonUrl)
                            threadNumPool[j].start()
                            findThread = True
                            break
                        else:
                            if not threadNumPool[j].isAlive():
                                #threadNumPool[j].stop()
                                threadNumPool[j] = DownloadPicsForOnePerson(compPersonUrl)
                                threadNumPool[j].start()
                                findThread = True
                                break
                    if findThread == False: 
                        time.sleep(5)



sys.exit()







startPage = loadProcess()
for i in range(startPage, 3000):
    setProcess(str(i))
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOnePagePeople(i)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadOnePagePeople(i)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)











#一共159种品牌
startPage = loadProcess()
for i in range(startPage, 50):
    setProcess(str(i))
    print 'start to process %s' % i
    #0是男，1是女
    queryUrl = 'http://search.zhenai.com/search/getfastmdata.jsps?gender=1&agebegin=0&ageend=99&photo=1&currentpage=%s' % (i+1)
    #onePage = getPageWithSpecTimes(0, queryUrl)
    onePage = getPageWithSpecTimes(3, queryUrl)


    if onePage == None:
        print 'cannot open page %s' % (i+1)
        writeToLog('cannot open page %s'%(i+1))
        continue
    print 'successfully get page %s' % (i+1)
    onePersonUrlPatten = re.compile(r'<a class="search_user_name" href="([^"]+?)" title="')
    personUrlList = onePersonUrlPatten.findall(onePage)

    print 'there are %s people found' % len(personUrlList)  

    for compPersonUrl in personUrlList:
        print 'compPersonUrl is %s' % compPersonUrl
        #onePersonPage = urllib.urlopen(compPersonUrl).read()
        #onePersonPage = getPageWithSpecTimes(3, compPersonUrl)
        onePersonPage = urllib2.urlopen(compPersonUrl).read().decode('GBk', 'ignore').encode('utf8')
        time.sleep(1)
        onePersonPage = urllib2.urlopen(compPersonUrl).read().decode('GBk', 'ignore').encode('utf8')
        if '珍爱网注册' in onePersonPage:
            print 'force to sign in'
            sys.exit()

        picUrlPattern = re.compile(r'<img class="hidden" src="(.+?)">')
        picUrlList = picUrlPattern.findall(onePersonPage)
        print 'there are %s pics for person %s' % (len(picUrlList), compPersonUrl)

        if len(picUrlList) < 5:
            print 'no enough pics for one person,%s' % compPersonUrl
            continue

        memberIdPattern = re.compile(r'memberid=(\d+)')
        memberId = memberIdPattern.findall(compPersonUrl)[0]

        agePattern = re.compile(r'今年<strong class="c_01">(\d+)岁</strong>')
        age = agePattern.findall(onePersonPage)[0]

        print 'dir name is %s_%s_m' % (memberId, age)

        if not os.path.exists('%s_%s_m' % (memberId, age)):
            os.makedirs('%s_%s_m' % (memberId, age))

        for i in range(len(picUrlList)):
            picurl = picUrlList[i].replace('_3', '_6')
            picPath = os.path.join('%s_%s_m' % (memberId, age), '%s.jpg' % i)
            try:
                urllib.urlretrieve(picurl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (picurl, compPersonUrl))
        print 'pics done for person %s\n' % compPersonUrl




