#coding=utf-8
import sys
import urllib2, urllib
import re
import os
import socket
import threading 
import time
import requests
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

    filehandler = open('Mapping_google.csv','a')
    filehandler.write(url+','+path+'\n')
    filehandler.close()

    writeLock.release()



class DownloadOneName(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, name, picsNumForPerson):
        threading.Thread.__init__(self)
        self.personName= name
        self.picsNumForPerson = picsNumForPerson

    def run(self):
        name = self.personName

        pageNum = (self.picsNumForPerson - 1) / 100 + 1
        print 'page num is %s' % pageNum

        picsNum = 1
        for j in range(pageNum):
            encodedName = urllib.quote(name.encode('gbk'))
            queryUrl = 'https://www.google.com.hk/search?safe=strict&tbm=isch&ijn=%s&start=%s&q=%s' % (j, 100*j, encodedName)
            try:
                picsPage = requests.get(queryUrl).content
                print 'successfully get page '
            except Exception as ep:
                print ep.message
                continue
            
            picsUrlPattern = re.compile(r'imgurl=(.+?)&amp;imgrefurl')

            picsUrlList = picsUrlPattern.findall(picsPage)
            for pics in picsUrlList:
                #picsNum += 1
                newPath = os.path.join(name.decode('utf8'), '%s_google.jpg' % picsNum)

                alreadyTriedTimes = 0
                while alreadyTriedTimes < 3:
                    try:
                        urllib.urlretrieve(pics, newPath)
                        writeMapping(pics, newPath)
                        try:
                            print 'thread %s download #%s pic for %s' % (self.getName(), picsNum, name.decode('utf8'))
                        except Exception as ep:
                            print ep.message
                        picsNum += 1

                       
                        break
                    except Exception as ep:
                        alreadyTriedTimes += 1
                        if alreadyTriedTimes < tryTimes:
                            pass
                        else:
                            print ep.message
                            try:
                                print 'thread %s cannot download pic,%s,%s' % (self.getName(), name.decode('utf8'), str(realUrl))
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
    print 'process %s/%s' % (i, peopleNum)
    name = namelist[i]
    if not os.path.exists(name.decode('utf8')):
        os.makedirs(name.decode('utf8'))
    PicsList = os.listdir(name.decode('utf8'))
    googlePicsNum = 0
    for pics in PicsList:
        if '_google' in pics:
            googlePicsNum += 1
    if googlePicsNum > picsNumPerPerson * 2 / 3:
        try:
            print 'enough google pics for %s' % name.decode('utf8')
        except Exception as ep:
            print ep.message
        continue



    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = DownloadOneName(namelist[i], picsNumPerPerson)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = DownloadOneName(namelist[i], picsNumPerPerson)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)





