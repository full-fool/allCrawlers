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
        return int(open('process.txt').read())
        #carBrandNum = int(open('process.txt').read())
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(firstArg):
    filehandler = open('process.txt', 'w')
    filehandler.write(firstArg)
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
    #writeLock.acquire()

    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    #writeLock.close()

def getProvinceAndDistrictCouple():
    filelines = open('newprovinceinfo.txt').read().split('\n')
    infoList = []
    for line in filelines:
        infoList.append((line.split(',')[0], line.split(',')[1], line.split(',')[2]))
    return infoList



'''
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

'''


cookies = 'cookies.txt'
cj = cookielib.LWPCookieJar(cookies)
cj.save()
headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [headers]
urllib2.install_opener(opener)




startPoint = loadProcess()

provinceAndDistrictCodeList = getProvinceAndDistrictCouple()

for i in range(startPoint, len(provinceAndDistrictCodeList)):
    provinceArg1 = provinceAndDistrictCodeList[i][0]
    provinceArg2 = provinceAndDistrictCodeList[i][1]
    age = provinceAndDistrictCodeList[i][2]

    setProcess(str(i))
    print 'processing process %s' % i
    for pageNum in range(1,51):
        queryUrl = 'http://search.zhenai.com/search/getfastmdata.jsps?gender=1&agebegin=%s&ageend=%s&workcityprovince=%s&workcitycity=%s&photo=1&currentpage=%s' % (age, age, provinceArg1, provinceArg2, pageNum)

        onePage = getPageWithSpecTimes(3, queryUrl)
        if onePage == None:
            print 'cannot open page,%s' % (queryUrl)
            writeToLog('cannot open page,%s'%(queryUrl))
            continue
        if '非常抱歉' in onePage:
            print 'no people found in page,%s' % queryUrl
            break
        if '......' in onePage:
            print 'cannot fetch today'
            sys.exit()
        onePersonUrlPatten = re.compile(r'<a class="search_user_name" href="([^"]+?)" title="')
        personUrlList = onePersonUrlPatten.findall(onePage)
        print '%s people found in page,%s' % (len(personUrlList), queryUrl)
        for compPersonUrl in personUrlList:                
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
                continue

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


