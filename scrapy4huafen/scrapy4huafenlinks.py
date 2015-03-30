#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import threading
import time
import os
import socket
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
makeDirLock = threading.Lock()


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

    writeLock.release()


class DownloadOnePageTheme(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, themeUrl):
        threading.Thread.__init__(self)
        self.themeUrl = themeUrl

    def run(self):
        url = 'http://cn.club.vmall.com/' + self.themeUrl
        #<a href="thread-3564472-1-2.html" onclick="atarget(this)" class="s xst">我的快乐，与您分享！</a>
        try:
            oneThemePage = urllib2.urlopen(url).read()
        except Exception as ep:
            writeToLog('cannot open page for one theme,%s' % url)
            return
        print 'successfull get theme,%s' % url
        #<a href="space-uid-8994548.html" target="_blank" class="xi2">远离人山人海  匹配出来的第0个就是坐作者
        authorIdPattern = re.compile(r'<a href="space-uid-(\d+)\.html" target="_blank" class="xi2">')
        try:
            authorId = authorIdPattern.findall(oneThemePage)[0]
        except Exception as ep:
            writeToLog('cannot find author id info,%s' % url)
            return
        
        allPicsLinkPattern = re.compile(r'window\.shareUrl = "([^"]+?)"')
        try:
            allPicsListString = allPicsLinkPattern.findall(oneThemePage)[0]
        except Exception as ep:
            writeToLog('cannot find pics in theme,%s' % url)
            return

        allPicsList = allPicsListString.split('||')
        print 'there are %s pics found in theme,%s' % (len(allPicsList),url)
        if len(allPicsList) > 0:
            makeDirLock.acquire()

            if not os.path.exists(authorId):
                os.makedirs(authorId)
            filePath = os.path.join(authorId, 'picsUrlList.txt')
            filehandler = open(filePath, 'a')
            for eachPicUrl in allPicsList:
                filehandler.write(eachPicUrl+'\n')
            filehandler.close()

            makeDirLock.release()

        print 'successfully write pics url in theme,%s' % url



def testThread(url):

    try:
        oneThemePage = urllib2.urlopen(url).read()
    except Exception as ep:
        writeToLog('cannot open page for one theme,%s' % url)
        return
    #<a href="space-uid-8994548.html" target="_blank" class="xi2">远离人山人海  匹配出来的第0个就是坐作者
    authorIdPattern = re.compile(r'<a href="space-uid-(\d+)\.html" target="_blank" class="xi2">')
    try:
        authorId = authorIdPattern.findall(oneThemePage)[0]
    except Exception as ep:
        writeToLog('cannot find author id info,%s' % url)
    #print 'authorId is %s' % authorId
    allPicsLinkPattern = re.compile(r'window\.shareUrl = "([^"]+?)"')
    try:
        allPicsListString = allPicsLinkPattern.findall(oneThemePage)[0]
    except Exception as ep:
        writeToLog('cannot find pics in theme,%s' % url)
        return

    allPicsList = allPicsListString.split('||')
    if len(allPicsList) > 0:
        makeDirLock.acquire()

        if not os.path.exists(authorId):
            os.makedirs(authorId)
        filePath = os.path.join(authorId, 'picsUrlList.txt')
        filehandler = open(filePath, 'a')
        for eachPicUrl in allPicsList:
            filehandler.write(eachPicUrl+'\n')
        filehandler.close()

        makeDirLock.release()
        


#testThread('http://cn.club.vmall.com/thread-3558482-1-1.html')
#sys.exit()



#花粉链接一直从 http://cn.club.vmall.com/forum-141-1.html 到
#            http://cn.club.vmall.com/forum-141-2000.html

# mainPage = urllib2.urlopen('http://cn.club.vmall.com/forum-141-1234.html').read()
# print mainPage
# sys.exit()

threadNum = 100
threadNumPool = {}

startPoint = loadProcess()
for i in range(startPoint, 2000+1):
    setProcess(str(i))
    print 'processing page %s' % i
    
    pageUrl = 'http://cn.club.vmall.com/forum-141-%s.html' % i
    try:
        mainPage = urllib2.urlopen(pageUrl).read()
    except Exception as ep:
        print ep.message
        writeToLog('cannot open page,%s' % pageUrl)
        continue

    themePageUrlPattern = re.compile(r'<a href="(.+?)" onclick="atarget\(this\)"')
    themePageUrlList = themePageUrlPattern.findall(mainPage)
    print '%s themes found in page %s' % (len(themePageUrlList), i)
    for themePageUrl in themePageUrlList:
        findThread = False
        while findThread == False:
            for j in range(threadNum):
                if not threadNumPool.has_key(j):
                    threadNumPool[j] = DownloadOnePageTheme(themePageUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
                else:
                    if not threadNumPool[j].isAlive():
                        threadNumPool[j] = DownloadOnePageTheme(themePageUrl)
                        threadNumPool[j].start()
                        findThread = True
                        break
            if findThread == False: 
                time.sleep(5)

    #print themePageUrlList
    #print len(themePageUrlList)

sys.exit()


startPage = loadProcess()
for i in range(startPage, 13871):
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









