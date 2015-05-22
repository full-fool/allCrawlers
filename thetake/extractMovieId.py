#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import threading
import time
import cookielib
import os
import socket
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()




url = 'https://thetake.com/movies/listMovies?limit=300&start=&actorId=:actorId&sortOrder=desc&productCategory=:categoryId&sortParam=trendingScore'
resultJson = json.load(urllib2.urlopen(url))
filehandler = open('allMovie.txt', 'w')
for i in range(len(resultJson)):
    movieId = resultJson[i]['id']
    movieName = resultJson[i]['name'].strip(' ')
    filehandler.write('%s,%s\n' % (movieId, movieName))
filehandler.close()




