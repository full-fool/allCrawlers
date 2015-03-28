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
from bs4 import BeautifulSoup
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3
writeLock = threading.Lock()


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

    filehandler = open('Mapping_bing.csv','a')
    filehandler.write(url+','+path+'\n')
    filehandler.close()

    writeLock.release()

class DownloadOnePage(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, subnamelist, picsNumForPerson):
        threading.Thread.__init__(self)
        self.namelist = subnamelist
        self.picsNumForPerson = picsNumForPerson


    def run(self):
        for i in range(len(self.namelist)):
            if not os.path.exists(self.namelist[i].decode('utf8')):
                os.makedirs(self.namelist[i].decode('utf8'))
            PicsList = os.listdir(self.namelist[i].decode('utf8'))
            bingPicsNum = 0
            for pics in PicsList:
                if '_bing' in pics:
                    bingPicsNum += 1
            if bingPicsNum > 100:
                continue
            picsNum = 0   
            pageNum = (self.picsNumForPerson-1) / 35 + 1
            print 'page num is %s' % pageNum
            for j in range(pageNum):
                queryUrl = 'http://cn.bing.com/images/async?first=%s&count=35&q=%s' % (35*j, self.namelist[i])
                picsPage = getPageWithSpecTimes(0, queryUrl)
                if picsPage == None:
                    continue
                pagesoup = BeautifulSoup(picsPage, from_encoding='utf8')
                iList = pagesoup.find_all("div", attrs={"class": 'dg_u'})
                for item in iList:
                    trash = item.a.get('m')
                    if trash == None:
                        continue
                    try:
                        url = trash.split(',')[4].split('"')[1]
                    except Exception as ep:
                        print ep.message
                    picsNum += 1
                    newPath = os.path.join(self.namelist[i].decode('utf8'), '%s_bing.jpg' % picsNum)

                    alreadyTriedTimes = 0
                    while alreadyTriedTimes < 3:
                        try:
                            urllib.urlretrieve(url, newPath)
                            writeMapping(url, newPath)
                            try:
                                print 'download one pic for %s' % self.namelist[i].decode('utf8')
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
                                    print 'cannot download pic,%s,%s' % (self.namelist[i].decode('utf8'), url)
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


totalNameList = getListFromFile('namelist_all.txt')
namelist = totalNameList[startPoint:startPoint+1000]
if not os.path.exists('%s-%s' % (startPoint+1, startPoint+1000)):
    os.makedirs('%s-%s' % (startPoint+1, startPoint+1000))
os.chdir('%s-%s' % (startPoint+1, startPoint+1000))
totalLen = len(namelist)
eachLen = totalLen/ threadNum

for i in range(threadNum):
    if i < threadNum - 1:
        DownloadOnePage(namelist[i*eachLen:min(i*eachLen+eachLen, totalLen)], picsNumPerPerson).start()
    else:
        DownloadOnePage(namelist[i*eachLen:totalLen], picsNumPerPerson).start()

