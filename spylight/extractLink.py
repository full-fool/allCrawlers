#coding=utf-8
from bs4 import BeautifulSoup
import re
import urllib
import urllib2
import socket
import sys
import time

socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')



def getListFromFile(fileName):
    fileContentList = open(fileName).read().split('\n')
    resultList = []
    for eachLine in fileContentList:
        if eachLine == '' or eachLine == '\n' or eachLine == '\r':
            continue
        resultList.append((eachLine.split(',')[0], eachLine.split(',')[1]))
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
    filehandler  = open('log.txt', 'a')
    filehandler.write(content)
    filehandler.close()


def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()


def loadProcess():
    process = int(open('process.txt').read())
    return process


filehandler = open('allTVEpisodeList.txt', 'a')



TVList = getListFromFile('allTVLink.txt')
process = loadProcess()
for i in range(process+1, len(TVList)):
#for eachTV in TVList:
    TVName = TVList[i][0]
    TVUrl = TVList[i][1]
    #pageContent = urllib2.urlopen(TVUrl).read()
    pageContent = getPageWithSpecTimes(0, TVUrl)
    if pageContent == None:
        writeToLog(TVUrl+'\n')
        print 'TVName has issues\n'
        setProcess(str(i))
        continue
    #pageContent = getPageWithSpecTimes(0,TVUrl)

    episodesPattern = re.compile(r'<a class="hover" href="([^"]+?)"><div class=\'mask loading holder\'>')
    episodesList =  episodesPattern.findall(pageContent)
    for eachEpisode in episodesList:
        episodeName = eachEpisode.split('/')[-1]
        filehandler.write('%s,%s,%s,\n' % (TVName, episodeName, 'http://www.spylight.com' + eachEpisode))
    print 'show ' + TVName + ' is done'
    setProcess(str(i))




filehandler.close()
