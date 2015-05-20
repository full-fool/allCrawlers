#coding=utf-8
from bs4 import BeautifulSoup
import re
import urllib
import urllib2
import os
import socket
import sys
import time
import threading

socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')


writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()

def getListFromFile(fileName):
    fileContentList = open(fileName).read().split('\n')
    resultList = []
    for eachLine in fileContentList:
        if eachLine == '' or eachLine == '\n' or eachLine == '\r':
            continue
        if len(eachLine.split(',')) == 2:
            resultList.append((eachLine.split(',')[0], eachLine.split(',')[1]))
        else:
            resultList.append((eachLine.split(',')[0], eachLine.split(',')[1], eachLine.split(',')[2]))

    return resultList

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
            print ep.message
            print 'wrong with fetch url %s for %s times' % (url, alreadyTriedTimes+1)
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

    print content
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

    writeLock.release()


def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()


def loadProcess():
    process = int(open('process.txt').read())
    return process

def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()


def loadDoneWork():
    if not os.path.exists('doneWork.txt'):
        return []
    doneWorkList = open('doneWork.txt').read().split('\n')
    return doneWorkList


def processForOneShow(fatherDir, url):
    # 获取所有outfits的链接 url + ?active_page=outfits&switch=1
    firstPageUrl = url + '?active_page=outfits&outfit_page=1'
    firstPageContent = getPageWithSpecTimes(0, firstPageUrl)
    if firstPageContent == None:
        writeToLog('cannot open first page for show,%s,%s\n' % (fatherDir, firstPageUrl))
        return None

    #pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    #outfits_gridSection = pagesoup.find_all("div", attrs={"id": "outfits_grid"})[0]
    allOutfitNumPattern = re.compile(r'<div id=\'showing-outfits\'>\s+\((\d+)\)\s+</div>')
    allOutfitNum = int(allOutfitNumPattern.findall(firstPageContent)[0])
    #print allOutfitNum
    
    pagesoup = BeautifulSoup(firstPageContent, from_encoding='utf8')
    outfits_gridSection = pagesoup.find_all("div", attrs={"id": "outfits_grid"})[0]
    linkPattern = re.compile(r'<a href="(/outfits/\d+)">')
    linkList = linkPattern.findall(str(outfits_gridSection))

    pageNum = (allOutfitNum - 1) / 12 + 1
    for  i in range(2, pageNum + 1):
        pageUrl = url + '?active_page=outfits&outfit_page=%s' % i
        pageContent = getPageWithSpecTimes(0, pageUrl)
        if pageContent == None:
            writeToLog('cannot open page for show,%s,%s,%s' % (fatherDir, pageNum, pageUrl))
            return None
        pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
        outfits_gridSection = pagesoup.find_all("div", attrs={"id": "outfits_grid"})[0]
        linkList += linkPattern.findall(str(outfits_gridSection))
    
    filehandler = open(os.path.join(fatherDir, 'outfitsUrlList.txt'), 'w')
    for eachLink in linkList:
        filehandler.write('http://www.spylight.com' + eachLink + '\n')
    filehandler.close()
    print 'done for %s' % fatherDir
    writeDoneWork(fatherDir)

    #print linkList
    #print len(linkList)



class fetchAllOutfits(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, fatherDir, url):
        threading.Thread.__init__(self)
        self.fatherDir = fatherDir
        self.url = url

    def run(self):
        fatherDir = self.fatherDir
        url = self.url
        #print 'thread is running for %s,%s' % (furnitureType, url)
        processForOneShow(fatherDir, url)







#processForOneShow('.', 'http://www.spylight.com/movies/104-atonement')
#sys.exit()


totalList = getListFromFile('allLinkList.txt')

doneWorkList = loadDoneWork()



threadNum = 100
threadNumPool = {}


for i in range(len(totalList)):
    fatherDir = None
    if len(totalList[i]) == 3:
        TVName = totalList[i][0].strip(' ')
        episodeName = totalList[i][1].strip(' ')
        #url = totalList[i][2]
        fatherDir = os.path.join(TVName, episodeName)
    else:
        movieName = totalList[i][0].strip(' ')
        fatherDir = movieName
    url = totalList[i][-1]
    if fatherDir in doneWorkList:
        print 'already done %s' % fatherDir
        continue

    if not os.path.exists(fatherDir):
        os.makedirs(fatherDir)

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = fetchAllOutfits(fatherDir, url)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = fetchAllOutfits(fatherDir, url)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)


