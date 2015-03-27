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
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3




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
    try:
        print content
    except Exception as ep:
        print ep.message
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()


#一共159种品牌
startPage = loadProcess()
for i in range(startPage, 13871):
    
    setProcess(str(i))
    
    print 'start to process %s' % i
    
    queryUrl = 'http://www.bf99.com/User/List_search____2______%s.htm' % i
    
    try:
        onePage = urllib.urlopen(queryUrl).read().decode('gb2312', 'ignore').encode('utf8')
    except Exception as ep :
        print ep.message
        writeToLog('cannot open page,%s'%queryUrl)
        continue


    print 'successfully get page %s' % (i)


    onePersonUrlPatten = re.compile(r'<a href="(.+?)" title=".+?" target="_blank" class="lnk_01"><b>')
    personUrlList = onePersonUrlPatten.findall(onePage)

    for j in range(14, len(personUrlList)):
    #for personUrl in personUrlList:
        compPersonUrl = 'http://www.bf99.com' + personUrlList[j]
        #onePersonPage = getPageWithSpecTimes(0, compPersonUrl)
        try:
            onePersonPage = urllib.urlopen(compPersonUrl).read().decode('gb2312', 'ignore').encode('utf8')
        except Exception as ep:
            writeToLog('cannot open page for person,%s' % compPersonUrl)
            continue

        filehandler = open('test.html', 'w')
        filehandler.write(onePersonPage)
        filehandler.close()


        picNumberPattern = re.compile(r'照片\(<font color="#000000">(\d+)</font>\)')
        try:
            picNumber = int(picNumberPattern.findall(onePersonPage)[0])
        except Exception as ep:
            print 'cannot find pics in,%s' % compPersonUrl
            continue

            
        if picNumber < 5:
            print 'there are %s pics in all, not enough' % picNumber
            continue

        agePattern = re.compile(r'<td class="nav2-25 friend_view_typecontent"><font color="#FF0000">(\d+)<')
        try:
            age = agePattern.findall(onePersonPage)[0]
        except Exception as ep:
            print ep.message
            print 'cannot find age info for,%s' % compPersonUrl
            continue

        personIdPattern = re.compile(r'/User/(.+?)\.htm')
        personId = personIdPattern.findall(compPersonUrl)[0]

   
        print 'dir name is %s_%s_m' % (personId, age)

        if not os.path.exists('%s_%s_m' % (personId, age)):
            os.makedirs('%s_%s_m' % (personId, age))




        picsPageUrl = 'http://www.bf99.com' + personUrlList[j][:7] + '4' + personUrlList[j][8:]
        try:
            picsPage = urllib2.urlopen(picsPageUrl).read().decode('gb2312', 'ignore').encode('utf8')
        except Exception as ep:
            print ep.message
            writeToLog('cannot open page,%s,%s,%s'%(personId, age, picsPageUrl))
            continue

        picsUrlPattern = re.compile(r'<td width="120" height="90"><img src="(.+?)" width="120" height="90"')
        picsUrlList = picsUrlPattern.findall(picsPage)




        for k in range(len(picsUrlList)):
            picurl = 'http://www.bf99.com' + picsUrlList[k].replace('_s', '_b')

            picPath = os.path.join('%s_%s_m' % (personId, age), '%s.jpg' % k)
            try:
                urllib.urlretrieve(picurl, picPath)
            except Exception as ep:
                writeToLog('cannot download pic,%s,%s' % (picurl, compPersonUrl))





