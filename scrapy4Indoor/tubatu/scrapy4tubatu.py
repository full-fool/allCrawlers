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




def getInfoFromFile(fileName):
    citiesList = open(fileName).read().split('\n')
    resultList = []
    for eachCity in citiesList:
        resultList.append((eachCity.split(',')[0], eachCity.split(',')[1]))
    return resultList


class ProcessOnePage(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, space, part, style, color, url):
        threading.Thread.__init__(self)
        self.space = space
        self.part = part
        self.style = style
        self.color = color
        self.url = url

    def run(self):
        space = self.space
        part = self.part
        style = self.style
        color = self.color
        url = self.url
        pageUrl = url
        print pageUrl

        #pageUrl = 'http://xiaoguotu.to8to.com/list.php?a1=0&a2=1&a3=&a4=1&a5=336&a6=13&a7=1&a8=&a9=0'
        currentPageNum = 1
        pageContent = getPageWithSpecTimes(0, pageUrl)
        if pageContent == None:
            writeToLog('cannot open page,%s,%s,%s,%s' %(space.decode('utf8'), part.decode('utf8'),\
                style.decode('utf8'), color.decode('utf8')))
            return
        #print pageContent
        #有两种图片的html格式
        #src="http://pic1.to8to.com/smallcase/2013/05/08/20130508155332-af1bf9c6_284.jpg" alt="家装最新客厅瓷砖电视墙效果图"
        #data-original="http://pic.to8to.com/smallcase/2013/07/05/20130705100634-17f14ba0_284.jpg" src="http://img.to8to.com/decorate_gallery/images/confirm/default.jpg?v=1408467009"alt="简欧客厅沙发电视背景墙效果图"
        #data-original="http://pic1.to8to.com/smallcase/1209/24/20120924_a1998e7efc19416bc200tzaE0U7DHpRf_284.jpg" src="http://img.to8to.com/decorate_gallery/images/confirm/default.jpg?v=1408467009"alt="简约装修效果图   客厅电视背景墙简约装修效果图" />

        picPattern1 = re.compile(r'src="([^"]+284\.jpg)" alt="([^"]+?)"')
        picInfoList = picPattern1.findall(pageContent)
        picPattern2 = re.compile(r'data-original="([^"]+284\.jpg)" src="[^"]+?"alt="([^"]+?)"')
        picInfoList += picPattern2.findall(pageContent)
        while '下一页' in pageContent:
            currentPageNum += 1
            pageUrl = url +  '&p=%s' % currentPageNum
            pageContent = getPageWithSpecTimes(0, pageUrl)
            if pageContent == None:
                writeToLog('cannot open page for page,%s,%s,%s,%s,%s' %(space.decode('utf8'), part.decode('utf8'),\
                    style.decode('utf8'), color.decode('utf8'), currentPageNum))
                break
            picInfoList += picPattern1.findall(pageContent)
            picInfoList += picPattern2.findall(pageContent)
        if len(picInfoList) == 0:
            return
        resultPicList = []
        for each in picInfoList:
            tempUrl = each[0].replace('smallcase', 'case')
            tempUrl = tempUrl.replace('_284', '')
            resultPicList.append((tempUrl, each[1]))

        dirName = os.path.join(space.decode('utf8'), part.decode('utf8'), style.decode('utf8'), color.decode('utf8'))

        if not os.path.exists(dirName):
            os.makedirs(dirName)

        filehandler = open(os.path.join(dirName, 'picsUrlList.txt'), 'w')
        for eachPic in resultPicList:
            filehandler.write('%s,%s\n' % (eachPic[0], eachPic[1]))
        filehandler.close()




 
threadNum = 100
threadNumPool = {}

 



spaceList = getInfoFromFile('space.txt')
partList = getInfoFromFile('part.txt')
styleList = getInfoFromFile('style.txt')
colorList = getInfoFromFile('color.txt')
process1, process2, process3, process4 = loadProcess()

for i in range(process1, len(spaceList)):
    if i == process1:
        jStartPoint = process2
    else:
        jStartPoint = 0
    for j in range(jStartPoint, len(partList)):
        if i == process1 and j == process2:
            kStartPoint = process3
        else:
            kStartPoint = 0
        for k in range(kStartPoint, len(styleList)):
            if i == process1 and j == process2 and k == process3:
                zStartPoint = process4
            else:
                zStartPoint = 0
            for z in range(zStartPoint, len(colorList)):
                pageUrl = 'http://xiaoguotu.to8to.com/list.php?a1=0&a2=1&a3=&a4=%s&a5=%s&a6=%s&a7=%s&a8=&a9=0' % \
                (spaceList[i][0], partList[j][0], styleList[k][0], colorList[z][0])
                

                findThread = False
                while findThread == False:
                    for threadIter in range(threadNum):
                        if not threadNumPool.has_key(threadIter):
                            threadNumPool[threadIter] = ProcessOnePage(spaceList[i][1], partList[j][1], styleList[k][1], colorList[z][1], pageUrl)
                            threadNumPool[threadIter].start()
                            findThread = True
                            break
                        else:
                            if not threadNumPool[threadIter].isAlive():
                                threadNumPool[threadIter] = ProcessOnePage(spaceList[i][1], partList[j][1], styleList[k][1], colorList[z][1], pageUrl)
                                threadNumPool[threadIter].start()
                                findThread = True
                                break
                    if findThread == False: 
                        time.sleep(5)
                setProcess('%s,%s,%s,%s' % (i,j,k,z))

