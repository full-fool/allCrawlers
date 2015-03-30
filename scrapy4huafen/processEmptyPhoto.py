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
from bs4 import BeautifulSoup



allDirsList = []
allFilesList = os.listdir('.')
for eachFile in allFilesList:
    if os.path.isdir(eachFile) and 'huafen_' in eachFile:
        allDirsList.append(eachFile)








for i in range(len(allDirsList)):
    subFileList = os.listdir(allDirsList[i])
    for fileName in subFileList:
        if '.jpg' in fileName:
            filePath = os.path.join(allDirsList[i], fileName)
            content = open(filePath).read()
            if 'file not found' in content:
                print 'dir is %s and picName is %s' % (allDirsList[i], fileName)
                os.rename(allDirsList[i], allDirsList[i].split('_')[1])
                print '%s has empty photo' % allDirsList[i]
                break