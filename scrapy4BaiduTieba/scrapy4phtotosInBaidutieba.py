#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
import threading 
import time
from bs4 import BeautifulSoup
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3
writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()


def decodeUrl(rawUrl):
    mappingDict = {'a': "0",'b': "8",'c': "5",'d': "2",'e': "v",'f': "s",'g': "n",'h': "k",'i': "h",\
        'j': "e",'k': "b",'l': "9",'m': "6",'n': "3",'o': "w",'p': "t",'q': "q",'r': "p",'s': "l",\
        't': "i",'u': "f",'v': "c",'w': "a","0": "7",'1': "d",'2': "g",'3': "j",'4': "m","5": "o",\
        "6": "r","7": "u","8": "1","9": "4"}
    resultUrl = rawUrl.replace('_z2C$q', ':')
    resultUrl = resultUrl.replace('_z&e3B', '.')
    resultUrl = resultUrl.replace('AzdH3F', '/')
    returnUrl=''
    for letter in resultUrl:
        if letter in mappingDict.keys():
            returnUrl += mappingDict[letter]
        else:
            returnUrl += letter
    #print returnUrl
    return returnUrl


#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    global tryTimes
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

def writeMapping(url, path):
    writeLock.acquire()

    filehandler = open('Mapping_baidu.csv','a')
    filehandler.write(url+','+path+'\n')
    filehandler.close()

    writeLock.release()


def writeProcess(processPath, content):
    filehandler = open(processPath, 'w')
    filehandler.write(content)
    filehandler.close()

def writeToLog(content):
    filehandler = open('log.txt', 'a')
    filehandler.write(content)
    filehandler.close()



class DownloadOneName(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, name, albumId, pageUrl):
        threading.Thread.__init__(self)
        self.name = name
        self.albumId = albumId
        self.pageUrl = pageUrl

    def run(self):
        name = self.name
        albumId  = self.albumId
        pageUrl = self.pageUrl
        resultJson = getPageWithSpecTimes(0, pageUrl)
        if resultJson == None:
            writeToLog('cannot open json page for catId,%s,%s,%s\n' % (name, albumId, pageUrl))
            return
        if not os.path.exists(os.path.join(name.decode('utf8'), albumId)):
            try:
                os.makedirs(os.path.join(name.decode('utf8'), albumId))
            except Exception as ep:
                print 'cannot makedirs,%s,%s' % (name.decode('utf8'), albumId)

        picIdPattern = re.compile(r'"pic_id":"([0-9a-zA-Z]+?)"') 
        picIdList = picIdPattern.findall(resultJson)
        filehandler = open(os.path.join(name.decode('utf8'), albumId, 'picsUrlList.txt'), 'w')
        for eachId in picIdList:
            filehandler.write('http://imgsrc.baidu.com/forum/pic/item/%s.jpg\n' % eachId)
        filehandler.close()
        writeDoneWork('%s,%s\n' % (name, albumId))



        


def processOnePerson(name):
    encodedName = urllib.quote(name.encode('gbk'))
    url = 'http://tieba.baidu.com/photo/g?kw=%s&ie=utf-8' % encodedName
    pageContent = getPageWithSpecTimes(3, url)
    if pageContent == None:
        writeToLog('cannot open page for person,%s\n' % name)
        return None
    if '还没有创建图册' in pageContent:
        writeToLog('no photo for person,%s\n' % name)
        return []
    
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    try:
        albumsSection = pagesoup.find_all("div", attrs={"id": 'op_move_to_catalogs'})[0]
    except Exception as ep:
        writeToLog('no photo for person,%s\n' % name)
        return []
    catIDPattern = re.compile(r'<li cat-id="([0-9a-zA-Z]+?)">')
    catIDList = catIDPattern.findall(str(albumsSection))
    allAlbumsIdList = []
    for catID in catIDList:
        catIDUrl = 'http://tieba.baidu.com/photo/g?kw=%s&cat_id=%s' % (encodedName, catID)
        pageContent = getPageWithSpecTimes(3, catIDUrl)
        if pageContent == None:
            writeToLog('cannot open for person and catID,%s,%s\n' % (name, catID))
            continue
        albumUrlPattern = re.compile(r'<a class="grbm_ele_a grbm_ele_big" hidefocus="true" target="_blank" href="/p/(\d+)">')
        allAlbumsIdList += albumUrlPattern.findall(pageContent)
        pageNum = 1
        while '下一页' in pageContent:
            pageNum += 1
            catIDUrl = 'http://tieba.baidu.com/photo/g?kw=%s&cat_id=%s&pn=%s' % (encodedName, catID, pageNum)
            pageContent = getPageWithSpecTimes(3, catIDUrl)
            if pageContent == None:
                writeToLog('cannot open for person and catID and page,%s,%s\n' % (name, catID, pageNum))
                continue
            albumUrlPattern = re.compile(r'<a class="grbm_ele_a grbm_ele_big" hidefocus="true" target="_blank" href="/p/(\d+)">')
            allAlbumsIdList += albumUrlPattern.findall(pageContent)


    return allAlbumsIdList

    #print allAlbumsIdList
    #print len(allAlbumsIdList)

#processOnePerson('范冰冰')
#sys.exit()



def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork_downloadPicsUrlTieba.txt', 'a')
    filehandler.write(name)
    filehandler.close()
    
    writeDoneWorkLock.release()

def loadDoneWork():
    try: 
        #doneWorkListPath = os.path.join(doneWorkPath, 'doneWork_downloadPicsUrlTieba.txt')
        return open('doneWork_downloadPicsUrlTieba.txt').read().split('\n')
    except Exception as ep:
        return []


def getListFromFile(fileName):
    namelist = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            if line2 != '':
                namelist.append(line2)

    return namelist

print 'input the start point'
try:
    startPoint = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()


print 'input the people number'
try:
    peopleNum = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()



threadNum = 1
print 'input the thread number'
try:
    threadNum = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()    


threadNumPool = {}
totalNameList = getListFromFile('namelist.txt')
namelist = totalNameList[startPoint:startPoint+peopleNum]
if not os.path.exists('%s-%s' % (startPoint+1, startPoint+peopleNum)):
    os.makedirs('%s-%s' % (startPoint+1, startPoint+peopleNum))
os.chdir('%s-%s' % (startPoint+1, startPoint+peopleNum))


doneWorkList = loadDoneWork()


for i in range(len(namelist)):
    name = namelist[i]
    tempIdList = processOnePerson(name)
    if tempIdList == None:
        continue

    print 'fetch all %s url for %s' % (len(tempIdList), name)
    for eachId in tempIdList:
        #pageUrl = 'http://tieba.baidu.com%s' % eachId
        if '%s,%s' % (name, eachId) in doneWorkList:
            print 'done for %s,%s' % (name, eachId)
            continue
        
        encodedName = urllib.quote(name.encode('gbk'))

        picPageUrl = 'http://tieba.baidu.com/photo/g/bw/picture/list?kw=%s&tid=%s&pn=1&pe=10000' % (encodedName, eachId)

        findThread = False
        while findThread == False:
            for j in range(threadNum):
                if not threadNumPool.has_key(j):
                    threadNumPool[j] = DownloadOneName(name, eachId, picPageUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
                else:
                    if not threadNumPool[j].isAlive():
                        threadNumPool[j] = DownloadOneName(name, eachId, picPageUrl)
                        threadNumPool[j].start()
                        findThread = True
                        break
            if findThread == False: 
                time.sleep(5)





