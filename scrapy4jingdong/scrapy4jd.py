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
import time
import threading
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
logLock = threading.Lock()

doneWorkList = []
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
    try:
        print content
    except Exception as ep:
        print ep.message

    logLock.acquire()
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()
    logLock.release()



def getListFromFile(fileName):
    namelist = []
    contentList = open(fileName).read().split('\n')
    for eachLine in contentList:
        namelist.append((eachLine.split('$')[0], eachLine.split('$')[1]))
    return namelist

def loadDoneWork():
    contentList = open('donework.txt').read().split('\n')
    return contentList







def getTypeAndStyle(furniture, url):
    global doneWorkList
    print furniture
    pageContent = getPageWithSpecTimes(0, url)
    if pageContent == None:
        writeToLog('cannot open page for,%s,%s' % (furniture, url))
        return None
    typePattern = re.compile(r'<a href="([^"]+?_类别_[^"]+?)" rel="nofollow"><i></i>(.+?)</a>')
    TypeList = typePattern.findall(pageContent)

    stylePattern = re.compile(r'<a href="([^"]+?_风格_[^"]+?)" rel="nofollow"><i></i>(.+?)</a>')
    StyleList = stylePattern.findall(pageContent)





    if len(StyleList) == 0:
        stylePattern = re.compile(r'<a href="([^"]+?_家装风格_[^"]+?)" rel="nofollow"><i></i>(.+?)</a>')
        StyleList = stylePattern.findall(pageContent)        


    typeList = []
    styleList = []
    for eachType in TypeList:
        typeList.append(('http://list.jd.com' + eachType[0], re.sub('/','|', eachType[1])))
    for eachStyle in StyleList:
        styleList.append(('http://list.jd.com' + eachStyle[0], re.sub('/','|', eachStyle[1])))



    if len(typeList) == 0 and len(styleList) == 0:
        print '%s has no type and style' % furniture
        if not os.path.exists(furniture):
            os.makedirs(furniture)
        if str(os.path.exists(furniture)) in doneWorkList:
            return
        itemPattern = re.compile(r'<a target="_blank" href="http://item\.jd\.com/(\d+?).html" onclick="')
        itemIDList = itemPattern.findall(pageContent)
        for pageNum in range(2, 10):
            pageUrl = url + '&page=%s' % pageNum
            pageContent = getPageWithSpecTimes(0, pageUrl)
            if pageContent == None:
                writeToLog('cannot open furniture for some page,%s,%s,%s' % (furniture, pageNum, pageUrl))
                continue
            addedItemIdList = itemPattern.findall(pageContent)
            if pageNum == 9:
                itemIDList += addedItemIdList[:20]
            else:
                itemIDList += addedItemIdList
            if len(addedItemIdList) < 60:
                break
        filehandler = open(os.path.join(furniture, 'itemList.txt'), 'w')
        for eachId in itemIDList:
            filehandler.write(eachId + '\n')
        filehandler.close()


        filehandler = open('donework.txt', 'a')
        filehandler.write(furniture + '\n')
        filehandler.close()

    elif len(typeList) == 0 and len(styleList) != 0:
        print '%s only has style' % furniture
        for eachStyle in styleList:
            #print eachStyle[1]
            if not os.path.exists(os.path.join(furniture, eachStyle[1])):
                os.makedirs(os.path.join(furniture, eachStyle[1]))
            if str(os.path.join(furniture, eachStyle[1])) in doneWorkList:
                return

            itemIDList = []
            for pageNum in range(1,10):
                pageUrl = eachStyle[0].replace('&page=1', '&page=%s' % pageNum)
                pageContent = getPageWithSpecTimes(0, pageUrl)
                if pageContent == None:
                    writeToLog('cannot open furniture for some style and page,%s,%s,%s,%s' % (furniture, eachStyle[1], pageNum, pageUrl))
                    continue
                itemPattern = re.compile(r'<a target="_blank" href="http://item\.jd\.com/(\d+?).html" onclick="')
                addedItemIdList = itemPattern.findall(pageContent)
                if pageNum == 9:
                    itemIDList += addedItemIdList[:20]
                else:
                    itemIDList += addedItemIdList
                if len(addedItemIdList) < 60:
                    break
            filehandler = open(os.path.join(furniture, eachStyle[1], 'itemList.txt'), 'w')
            for eachId in itemIDList:
                filehandler.write(eachId + '\n')
            filehandler.close()
            filehandler = open('donework.txt', 'a')
            filehandler.write(str(os.path.join(furniture, eachStyle[1])) + '\n')
            filehandler.close()

    elif len(typeList) != 0 and len(styleList) == 0:
        print '%s only has type' % furniture
        for eachType in typeList:
            if not os.path.exists(os.path.join(furniture, eachType[1])):
                os.makedirs(os.path.join(furniture, eachType[1]))
            if str(os.path.join(furniture, eachType[1])) in doneWorkList:
                return

            itemIDList = []
            for pageNum in range(1,10):
                pageUrl = eachType[0].replace('&page=1', '&page=%s' % pageNum)
                pageContent = getPageWithSpecTimes(0, pageUrl)
                if pageContent == None:
                    writeToLog('cannot open furniture for some type and page,%s,%s,%s,%s' % (furniture, eachType[1], pageNum, pageUrl))
                    continue
                itemPattern = re.compile(r'<a target="_blank" href="http://item\.jd\.com/(\d+?).html" onclick="')
                addedItemIdList = itemPattern.findall(pageContent)
                if pageNum == 9:
                    itemIDList += addedItemIdList[:20]
                else:
                    itemIDList += addedItemIdList
                if len(addedItemIdList) < 60:
                    break
            filehandler = open(os.path.join(furniture, eachType[1], 'itemList.txt'), 'w')
            for eachId in itemIDList:
                filehandler.write(eachId + '\n')
            filehandler.close()
            filehandler = open('donework.txt', 'a')
            filehandler.write(str(os.path.join(furniture, eachType[1])) + '\n')
            filehandler.close()




    else:
        print '%s has both' % furniture
        for eachType in typeList:
            for eachStyle in styleList:
                #print eachStyle[1]
                print eachType[1], eachStyle[1]
                if not os.path.exists(os.path.join(furniture, eachType[1], eachStyle[1])):
                    os.makedirs(os.path.join(furniture, eachType[1], eachStyle[1]))
                if str(os.path.join(furniture, eachType[1], eachStyle[1])) in doneWorkList:
                    return
                envPattern = re.compile(r'ev=(\d+?_\d+?)[\D]')
                typeEnv = envPattern.findall(eachType[0])[0]                
                styleEnv = envPattern.findall(eachStyle[0])[0]
                catPattern = re.compile(r'cat=(\d+?,\d+?,\d+)')
                #print 'url is ' + url
                category = catPattern.findall(url)[0]
                itemIDList = []
                for pageNum in range(1,10):
                    pageUrl = 'http://list.jd.com/list.html?cat=%s&ev=%s@%s@&page=%s' % (category, typeEnv, styleEnv, pageNum)
                    print 'pageurl is ' + pageUrl
                    pageContent = getPageWithSpecTimes(0, pageUrl)
                    if pageContent == None:
                        writeToLog('cannot open furniture page for type and style,%s,%s,%s,%s,%s' % (furniture, eachType[1], eachStyle[1], pageNum, pageUrl))
                        continue
                    itemPattern = re.compile(r'<a target="_blank" href="http://item\.jd\.com/(\d+?).html" onclick="')
                    addedItemIdList = itemPattern.findall(pageContent)
                    if pageNum == 9:
                        itemIDList += addedItemIdList[:20]
                    else:
                        itemIDList += addedItemIdList
                    if len(addedItemIdList) < 60:
                        break
                filehandler = open(os.path.join(furniture, eachType[1], eachStyle[1], 'itemList.txt'), 'w')
                for eachId in itemIDList:
                    filehandler.write(eachId + '\n')
                filehandler.close()
                filehandler = open('donework.txt', 'a')
                filehandler.write(str(os.path.join(furniture, eachType[1], eachStyle[1])) + '\n')
                filehandler.close()

doneWorkList = loadDoneWork()
furnitureList = getListFromFile('typelist.txt')
for eachFurniture in furnitureList:
    getTypeAndStyle(eachFurniture[0], eachFurniture[1])
