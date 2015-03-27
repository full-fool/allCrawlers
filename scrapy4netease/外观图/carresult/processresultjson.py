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
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')



def getListFromFile(fileName):
    i = 0
    returnList = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            if line2 == '':
                continue
            returnList.append(line2)
            i += 1
    return returnList

keywordList = ['左前45度', '左后45度', '右前45度','右后45度','车前正视', '车侧正视', '车后45度', '车后正视'\
                , '左前','正前','正侧','左后','正后','右后','右前' ]

curDirList = os.listdir('.')
carDirList = []
for name in curDirList:
    if os.path.isdir(name):
        carDirList.append(name)
carBrandDict = {}
for carBrand in carDirList:
    if carBrand == '.DS_Store':
        continue


    carTypeList = os.listdir(carBrand)
    carTypeDict = {}
    for carType in carTypeList:
        if carType == '.DS_Store':
            continue
        typePath = os.path.join(carBrand, carType)
        carYearList = os.listdir(typePath)
        carYearDict = {}
        for carYear in carYearList:
            if carYear == '.DS_Store':
                continue
            filePath = os.path.join(carBrand, carType, carYear, 'picsUrlList.txt')
            if not os.path.exists(filePath):
                continue

            picsUrlList = getListFromFile(filePath)
            #resultPicsUrlList=[]
            for singlePic in picsUrlList:
                yearPattern = re.compile(r'([\d]{4})款')
                if len(yearPattern.findall(singlePic.encode('utf8'))) != 0:
                    year = yearPattern.findall(singlePic.encode('utf8'))[0]
                    carYearKeys = carYearDict.keys()


                    keywordPattern = re.compile(r'\((.+?)\)')
                    if len(keywordPattern.findall(singlePic)) == 0:
                        #print 'do not have keyword', singlePic, carYear
                        continue
                    keyword = keywordPattern.findall(singlePic)[-1]
                    if keyword in keywordList:
                        #resultPicsUrlList.append(singlePic.split(',')[0])
                        #resultPicsUrlList.append(singlePic)
                        #print 'keyword is ' , keyword,
                        if year in carYearKeys:
                            carYearDict[year].append(singlePic.split(',')[0])
                        else:
                            carYearDict[year] = []
                            carYearDict[year].append(singlePic.split(',')[0])
                    else:
                        #print 'keyword is not in list, %s,%s' % (singlePic, keyword)
                        continue
                else:
                    #print 'cannot find year for %s' % singlePic, carYear
                    continue


            #carYearDict[carYear] = resultPicsUrlList
        carTypeDict[carType] = carYearDict
    carBrandDict[carBrand] = carTypeDict


filehandler = open('cleanResult2.json','w')
filehandler.write(json.dumps(carBrandDict, indent=4, ensure_ascii=False))
filehandler.close()







#keyword is not in list, http://img3.cache.netease.com/photo/0008/2010-01-31/5UC8RTPJ29LM0008.jpg,霸锐2008款3.8L豪华版(国IV)(全部车门打开车后正视)