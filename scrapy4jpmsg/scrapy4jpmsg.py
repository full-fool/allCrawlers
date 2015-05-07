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



def loadProcess():
    try:
        content = open('process.txt').read()
        process1 = int(content.split(',')[0])
        process2 = int(content.split(',')[1])
        return process1, process2
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(process1, process2):
    filehandler = open('process.txt', 'w')
    filehandler.write(str(process1)+','+str(process2))
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


class DownloadOnePageForPerson(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, pageNum):
        threading.Thread.__init__(self)
        self.pageNum = pageNum

    def run(self):
        pageNum = self.pageNum
        print 'start to process %s' % pageNum
        
        queryUrl = 'http://www.jpmsg.com/meinv/jpmeinv_%s.html' % (78-pageNum)
        try:
            onePage = urllib.urlopen(queryUrl).read().decode('gb2312', 'ignore').encode('utf8')
        except Exception as ep :
            print ep.message
            writeToLog('cannot open page,%s'%queryUrl)
            return


        print 'successfully get page %s' % (pageNum)


        onePersonUrlPatten = re.compile(r'<a href="([^"]+?)" target="_blank"><img src="[^"]+?" width="120" height="160" alt="(.+?)" /></a><br /><a href=')
        personUrlList = onePersonUrlPatten.findall(onePage)


        for j in range(len(personUrlList)):
        #for personUrl in personUrlList:
            compPersonUrl = personUrlList[j][0]
            desp = personUrlList[j][1]
            #onePersonPage = getPageWithSpecTimes(0, compPersonUrl)
            try:
                onePersonPage = urllib.urlopen(compPersonUrl).read().decode('gb2312', 'ignore').encode('utf8')
            except Exception as ep:
                writeToLog('cannot open page for person,%s' % compPersonUrl)
                continue

            dirName = '%s_%s' % (desp, compPersonUrl[-9:-5])
            print 'dir name is %s' % dirName

            if not os.path.exists(dirName):
                os.makedirs(dirName)


            picsUrlPattern = re.compile(r'<img src="(.+?)" alt="[^"]+?"  border="0" style="')
            picsUrlList = picsUrlPattern.findall(onePersonPage)
            #print 'len of pics is %s' % len(picsUrlList)
            for k in range(len(picsUrlList)):
                filehandler = open(os.path.join(dirName, 'picsUrlList.txt'), 'a')
                filehandler.write(picsUrlList[k]+'\n')
                filehandler.close()







threadNum = 77
threadNumPool = {}


#startPage = loadProcess()
startPage = 0
for i in range(1, 78):
    #setProcess(str(i))
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOnePageForPerson(i)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    #threadNumPool[j].stop()
                    threadNumPool[j] = DownloadOnePageForPerson(i)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)









