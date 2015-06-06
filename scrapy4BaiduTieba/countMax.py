#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import threading
import time
import os
import socket
import shutil
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')




lines = 0
MaxNum = 0
MaxName = ''
resultDict = {}
for filePart in os.walk('.'):
    if 'picsUrlList.txt' in filePart[2]:
        filePath = os.path.join(filePart[0], 'picsUrlList.txt')
        fatherDir, albumNum = os.path.split(filePart[0])
        fatherDir, personName = os.path.split(fatherDir)
        tempNum = len(open(filePath).read().split('\n')) - 1
        if resultDict.has_key(personName):
        	resultDict[personName] += tempNum
        else:
        	resultDict[personName] = tempNum

print 'start sorting'
sortedDict = sorted(resultDict.iteritems(), key=lambda d:d[1], reverse=True)
print sortedDict[0]
print sortedDict[1]
print sortedDict[2]
print sortedDict[0][0]
print sortedDict[1][0]
print sortedDict[2][0]




