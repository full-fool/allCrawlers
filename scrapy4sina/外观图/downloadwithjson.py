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
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3


def writeToLog(content):
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

def writeMapping(url, path):

    filehandler = open('Mapping.csv', 'a')
    filehandler.write(url+','+path+',\n')
    filehandler.close()

def loadProcess():
    namelist = []
    #filehandler = open('process.txt')
    for line in open('process.txt'):
    #for line in filehandler:
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            namelist.append(line2)
    if len(namelist) != 3:
        print 'process.txt broken, please fix it'
        sys.exit()
    #filehandler.close()
    return int(namelist[0]), int(namelist[1]), int(namelist[2])


def setProcess(brandNum,TypeNum,year):
    filehandler = open('process.txt', 'w')
    filehandler.write('%s\n%s\n%s' % (brandNum, TypeNum, year))
    filehandler.close()




#carBrandList中第一个是链接，第二项的.decode('utf8')是品牌名
#carBrandList = getAllCarBrandAndLink()


brandNum, TypeNum, yearNum = loadProcess()
print 'process is ', brandNum, TypeNum, yearNum
carBrandDict = json.load(open('result.json'))
allCarBrand = carBrandDict.keys()
for i in range(brandNum, len(allCarBrand)):
#for carBrand in allCarBrand:
    print allCarBrand[i].decode('utf8')
    carTypeDict = carBrandDict[allCarBrand[i]]
    allCarTypes = carTypeDict.keys()
    for j in range(TypeNum, len(allCarTypes)):
    #for carType in allCarTypes:
        print allCarTypes[j].decode('utf8')
        carYearDict = carTypeDict[allCarTypes[j]]
        allCarYears = carYearDict.keys()
        for k in range(yearNum, len(allCarYears)):
        #for year in allCarYears:
            print allCarYears[k]
            urlList = carYearDict[allCarYears[k]]
            if len(urlList) == 0:
                continue
            newPath = os.path.join(allCarBrand[i].decode('utf8'), allCarTypes[j].decode('utf8'), allCarYears[k])
            if not os.path.exists(newPath):
                os.makedirs(newPath)
            for url in urlList:
                picNamePattern = re.compile(r'.+?/Img(\d+)_800\.')
                picName = 'sina_' + picNamePattern.findall(url)[0] + '.jpg'
                picPath = os.path.join(allCarBrand[i].decode('utf8'), allCarTypes[j].decode('utf8'), allCarYears[k], str(picName).decode('utf8'))
                if os.path.exists(picPath):
                    continue
                print url
                alreadyTriedTimes = 0
                while alreadyTriedTimes < tryTimes:
                    try:
                        urllib.urlretrieve(url, picPath)
                        writeMapping(url, picPath)
                        break
                    except Exception as ep:
                        alreadyTriedTimes += 1
                        if alreadyTriedTimes < tryTimes:
                            pass
                        else:
                            print ep.message
                            print 'cannot download pic,%s,%s,%s,%s' % (allCarBrand[i].decode('utf8'), allCarTypes[j].decode('utf8'), allCarYears[k], url)
                            writeToLog('cannot download pic,%s,%s,%s,%s' % (allCarBrand[i].decode('utf8'), allCarTypes[j].decode('utf8'), allCarYears[k], url))

            setProcess(str(i), str(j), str(k))


