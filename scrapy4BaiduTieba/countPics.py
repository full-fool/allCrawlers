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

for filePart in os.walk('.'):
    if 'picsUrlList.txt' in filePart[2]:
        #print 'picsUrlList.txt in ' + filePart[0]
        filePath = os.path.join(filePart[0], 'picsUrlList.txt')
        lines += len(open(filePath).read().split('\n')) - 1
        print lines
print lines



