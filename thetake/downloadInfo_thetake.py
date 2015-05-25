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
writeDoneWorkLock = threading.Lock()

def getListFromFile(fileName):
    originalList = open(fileName).read().split('\n')
    resultList = []
    for eachItem in originalList:
        if eachItem != '' and eachItem !='\n' and eachItem != '\r':
            resultList.append((eachItem.split(',')[0], eachItem.split(',')[1]))
    return resultList


def getPageWithSpecTimes(decodeType, url):
    tryTimes = 4
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            #print 'url is %s, try time is %s' % (url, alreadyTriedTimes)
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



def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()

def getDoneWork():
    if not os.path.exists('doneWork.txt'):
        return []
    return open('doneWork.txt').read().split('\n')


def fetchInfoForOneMovie(movieName, movieId, url):
    fatherDir = movieName
    movieUrl = 'https://thetake.com/movie/%s' % movieId
    resultJson = json.load(urllib2.urlopen(url))
    resultDict = {}
    resultDict['url'] = movieUrl
    resultDict['name'] = movieName
    resultDict['frame'] = []
    currentFrameNum = 0
    currentFrameDict = {}
    currentItemNum = 0
    for i in range(len(resultJson)):
        currentItemNum += 1
        eachItemDict = resultJson[i]
        #print eachItemDict
        #sys.exit()
        try:
            positionX = eachItemDict['productX']
            positionY = eachItemDict['productY']

        except Exception as ep:
            #print eachItemDict
            positionX = -1
            positionY = -1
        frameTime = eachItemDict['time']
        productName = eachItemDict['name']
        productBrand = eachItemDict['brand']
        productPrice = eachItemDict['price']
        productDescription = '%s,%s,%s' % (productBrand, productName, productPrice)
        picUrl = eachItemDict['productImageLarge']
        position = [positionX, positionY]
        if len(currentFrameDict) == 0 or currentFrameDict['time'] != frameTime:
            currentFrameNum += 1
            currentItemNum = 1
            if len(currentFrameDict) > 0:
                resultDict['frame'].append(currentFrameDict)
            currentFrameDict = {}
            currentFrameDict['time'] = frameTime
            currentFrameDict['items'] = []
        tempItemDict = {}
        tempItemDict['url'] = picUrl
        tempItemDict['name'] = 'frame_%s_item_%s.jpg' % (currentFrameNum, currentItemNum)
        tempItemDict['position'] = position
        tempItemDict['description'] = productDescription
        currentFrameDict['items'].append(tempItemDict)
        #print 'frame %s, item %s, name is %s' % (currentFrameNum, currentItemNum, productName)


    filehandler = open(os.path.join(fatherDir, 'info.json'), 'w')
    filehandler.write(json.dumps(resultDict, indent=4, ensure_ascii=False))
    filehandler.close()
    writeDoneWork(fatherDir)
    print '%s is done' % fatherDir




class processMovie(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, movieName, movieId, url):
        threading.Thread.__init__(self)
        self.movieName = movieName
        self.movieId = movieId
        self.url = url


    def run(self):
        movieName = self.movieName
        movieId = self.movieId
        url = self.url
        
        fetchInfoForOneMovie(movieName, movieId, url)
      
threadNum = 203
threadNumPool = {}

doneWorkList = getDoneWork()
movieList = getListFromFile('allMovie.txt')
for i in range(len(movieList)):
    movieId = movieList[i][0]
    movieName = movieList[i][1]
    if movieName in doneWorkList:
        print 'already done %s' % movieName
        continue
    url = 'https://thetake.com/movies/listMovieTrailerFrameProducts?movieId=%s' % movieId
    if not os.path.exists(movieName):
        os.makedirs(movieName)
            
    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = processMovie(movieName, movieId, url)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = processMovie(movieName, movieId, url)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)




