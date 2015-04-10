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



class DownloadOneName(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, name, picsNumForPerson, alreadyPics):
        threading.Thread.__init__(self)
        self.personName = name
        self.picsNumForPerson = picsNumForPerson
        self.alreadyPics = alreadyPics

    def run(self):
        name = self.personName
        alreadyPics = self.alreadyPics
        pageNum = (self.picsNumForPerson-1) / 60 + 1
        print 'page num is %s' % pageNum

        picsNum = alreadyPics
        startPage = alreadyPics / 60
        startPicNum = alreadyPics % 60
        for j in range(startPage, pageNum):
            encodedName = urllib.quote(name.encode('gbk'))
            queryUrl = 'http://image.baidu.com/i?tn=resultjson_com&word=%s&oe=utf-8&rn=60&pn=%s' % (encodedName, 60*j)
            picsPage = getPageWithSpecTimes(0, queryUrl)
            if picsPage == None:
                continue
            
            picsUrlPattern = re.compile(r'"objURL":"([^"]+?)"')
            picsUrlList = picsUrlPattern.findall(picsPage)
            tempProess = 0
            for pics in picsUrlList:
                tempProess += 1
                if j == startPage and tempProess <= startPicNum:
                    continue
                realUrl = decodeUrl(pics)

                #picsNum += 1
                newPath = os.path.join(name.decode('utf8'), '%s_baidu.jpg' % picsNum)

                alreadyTriedTimes = 0
                while alreadyTriedTimes < 3:
                    try:
                        urllib.urlretrieve(str(realUrl), newPath)

                        writeMapping(str(realUrl), newPath)
                        picsNum += 1
                        try:
                            print '%s download #%s pic for %s' % (self.getName(), picsNum, name.decode('utf8'))
                        except Exception as ep:
                            print ep.message
                       
                        break
                    except Exception as ep:
                        alreadyTriedTimes += 1
                        if alreadyTriedTimes < tryTimes:
                            pass
                        else:
                            print ep.message
                            try:
                                print 'cannot download pic,%s,%s' % (name.decode('utf8'), str(realUrl))
                            except Exception as ep:
                                print ep.message







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
    if startPoint % 1000 != 0:
        print 'the number must be a times of 1000'
        sys.exit()
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()

print 'input the people number'
try:
    peopleNum = int(raw_input())
    if peopleNum % 1000 != 0:
        print 'the number must be a times of 1000'
        sys.exit() 
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()



picsNumPerPerson = 0
print 'input the pics number for each person'
try:
    picsNumPerPerson = int(raw_input())

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
totalNameList = getListFromFile('namelist_all.txt')
namelist = totalNameList[startPoint:startPoint+peopleNum]
if not os.path.exists('%s-%s' % (startPoint+1, startPoint+peopleNum)):
    os.makedirs('%s-%s' % (startPoint+1, startPoint+peopleNum))
os.chdir('%s-%s' % (startPoint+1, startPoint+peopleNum))


for i in range(len(namelist)):
    print 'process: %s/%s' % (i, peopleNum)
    name = namelist[i]
    if not os.path.exists(name.decode('utf8')):
        os.makedirs(name.decode('utf8'))
    PicsList = os.listdir(name.decode('utf8'))
    baiduPicsNum = 0
    for pics in PicsList:
        if '_baidu' in pics:
            baiduPicsNum += 1
    if baiduPicsNum > picsNumPerPerson * 2 / 3:
        try:
            print 'enough baidu pics for %s\n' % name.decode('utf8')
        except Exception as ep:
            print ep.message
        continue


    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOneName(namelist[i], picsNumPerPerson, baiduPicsNum)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadOneName(namelist[i], picsNumPerPerson, baiduPicsNum)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)





