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

def getListFromFile(fileName):
    picsUrlList = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            if line2 != '':
                picsUrlList.append(line2)

    return picsUrlList






allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile):
        allDirsList.append(eachFile)








for i in range(len(allDirsList)):
    picsUrlList = getListFromFile(os.path.join(allDirsList[i], 'picsUrlList.txt'))
    if len(picsUrlList) < 5:
        print '%s is deleted, it has %s pics' % (allDirsList[i], len(picsUrlList))
        shutil.rmtree(allDirsList[i])
