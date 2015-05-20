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
writeDoneWorkLock = threading.Lock()

def getListFromFile(fileName):
    fileContentList = open(fileName).read().split('\n')
    resultList = []
    for eachLine in fileContentList:
        if eachLine == '' or eachLine == '\n' or eachLine == '\r':
            continue
        resultList.append(eachLine)

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
    
    filehandler = open('doneWork_downloadInfo.txt', 'a')
    filehandler.write(name+'\n')
    filehandler.close()
    
    writeDoneWorkLock.release()


def loadDoneWork():
    if not os.path.exists('doneWork_downloadInfo.txt'):
        return []
    doneWorkList = open('doneWork_downloadInfo.txt').read().split('\n')
    return doneWorkList

def processForEachOutfit(fatherDir, sceneNum, url):
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open out fit main page,%s,%s,%s' % (fatherDir, sceneNum, url))
        return None
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    mainPicSection = pagesoup.find_all("div", attrs={"class": 'ui portrait image relative'})[0]
    mainPicUrl = mainPicSection.div.img.get('src')

    #print 'mainPicUrl is ' + mainPicUrl


    resultInfoDict = {}
    resultInfoDict['url'] = url
    resultInfoDict['info'] = {}
    resultInfoDict['info']['url'] = mainPicUrl
    resultInfoDict['info']['name'] = 'scene_%s.jpg' % sceneNum
    resultInfoDict['items'] = []

    

    itemSectionList = pagesoup.find_all("div", attrs={"class": 'ui border thumb product_item'})
    itemInfoList = []
    for i in range(len(itemSectionList)):
    #for eachSection in itemSectionList:
        #print eachSection
        #break
        eachSection = itemSectionList[i]
        itemPicUrlPattern = re.compile(r'class="hover lazy" data-lazy="([^"]+?)"')
        #<img alt='Outfit worn by Avinash Dagavi "Nash" in Betas!' class="hover lazy" data-lazy="http://static.spylight.com/product_images/avatars/000/044/543/square/jpeg.jpg?1421993736" src="http://assets.spylight.com/assets/blank-1c297739ab576637029e12e2cc2bf792.gif"/>
        itemPicUrl = itemPicUrlPattern.findall(str(eachSection))[0]

        bigPicUrl = itemPicUrl.replace('/square/', '/mobile_full/')
        descriptionHeadPattern = re.compile(r'<div class="ui secondary ellipsis text">\s?(.+?)\s?</div>', re.S)
        description = str(descriptionHeadPattern.findall(str(eachSection))[0])
        descriptionPattern = re.compile(r'<div class="small ellipsis text">\s?(.+?)\s?</div>', re.S)
        descriptionList = descriptionPattern.findall(str(eachSection))
        for eachDescription in descriptionList:
            description += ',' + eachDescription
        description = description.replace('\n', ',')
        itemInfoList.append((itemPicUrl, description))
        itemDict = {}
        itemDict['url'] = bigPicUrl
        itemDict['name'] = 'scene_%s_item_%s.jpg' % (sceneNum, i+1)
        itemDict['description'] = description
        resultInfoDict['items'].append(itemDict)

    targetDir = os.path.join(fatherDir, 'Scene_%s' % sceneNum)
    if not os.path.exists(targetDir):
        os.makedirs(targetDir)

    filehandler = open(os.path.join(targetDir, 'info.json'), 'w')
    filehandler.write(json.dumps(resultInfoDict, indent=4, ensure_ascii=False))
    filehandler.close()
    mainPicPath = os.path.join(targetDir, 'scene_%s.jpg' % sceneNum)
    try:
        urllib.urlretrieve(mainPicUrl, mainPicPath)
    except Exception as ep:
        print 'cannot download pic for scene,%s,%s,%s' % (fatherDir, sceneNum, mainPicUrl)

    for eachItemPic in resultInfoDict['items']:
        picUrl = eachItemPic['url']
        picName = eachItemPic['name']
        picPath = os.path.join(targetDir, picName)
        try:
            urllib.urlretrieve(picUrl, picPath)
        except Exception as ep:
            print 'cannot download pic for item,%s,%s,%s,%s' % (fatherDir, sceneNum, picName, picUrl)


    writeDoneWork('%s,%s' % (fatherDir, sceneNum))
    print 'done for %s, %s' % (fatherDir, sceneNum)









#processForEachOutfit('.', 0, 'http://www.spylight.com/outfits/38327')
#sys.exit()


class processOutfit(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, fatherDir, sceneNum, url):
        threading.Thread.__init__(self)
        self.fatherDir = fatherDir
        self.sceneNum = sceneNum
        self.url = url


    def run(self):
        fatherDir = self.fatherDir
        sceneNum = self.sceneNum
        url = self.url
        
        processForEachOutfit(fatherDir, sceneNum, url)
      
        

threadNum = 100
threadNumPool = {}


doneWorkList = loadDoneWork()


for filePart in os.walk('.'):
    if 'outfitsUrlList.txt' in filePart[2]:
        print 'outfitsUrlList.txt in ' + filePart[0]
        
        filePath = os.path.join(filePart[0], 'outfitsUrlList.txt')
        outfitList = getListFromFile(filePath)
        for i in range(len(outfitList)):
            fatherDir = filePart[0]
            sceneNum = i + 1
            if '%s,%s' % (fatherDir, i) in doneWorkList:
                print '%s,%s already done' % (fatherDir, sceneNum)
                continue
            
            findThread = False
            while findThread == False:
                for j in range(threadNum):
                    if not threadNumPool.has_key(j):
                        threadNumPool[j] = processOutfit(fatherDir, sceneNum, outfitList[i])
                        threadNumPool[j].start()
                        findThread = True
                        break
                    else:
                        if not threadNumPool[j].isAlive():
                            threadNumPool[j] = processOutfit(fatherDir, sceneNum, outfitList[i])
                            threadNumPool[j].start()
                            findThread = True
                            break
                if findThread == False: 
                    time.sleep(5)









