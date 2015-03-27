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
            carYearDict[carYear] = picsUrlList
        carTypeDict[carType] = carYearDict
    carBrandDict[carBrand] = carTypeDict


filehandler = open('result.json','w')
filehandler.write(json.dumps(carBrandDict, indent=4, ensure_ascii=False))
filehandler.close()


