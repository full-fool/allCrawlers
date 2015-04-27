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

content = urllib.urlopen('http://bbs.pku.edu.cn/bbs/main0.php').read().decode('gb2312', 'ignore').encode('utf8')
#print content
#sys.exit()
topTenInfoPatten = re.compile(r'<span class=".+?">◇ <span class=\'hidden\'>.+?</span><a href=\'(.+?)\'>(.+?)</a><br /></span>')
topTenInfoList = topTenInfoPatten.findall(content)
resultList = []
print len(topTenInfoList)
#for item in topTenInfoList:
for i in range(len(topTenInfoList)):
    resultList.append(('http://bbs.pku.edu.cn/bbs/' + topTenInfoList[i][0], topTenInfoList[i][1]))

for i in range(len(resultList)):
    print resultList[i][0], resultList[i][1]



