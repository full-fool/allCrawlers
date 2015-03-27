#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
import cookielib
import threading
import time
from cookielib import LWPCookieJar


socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')




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
			alreadyTriedTimes += 1
			if alreadyTriedTimes < tryTimes:
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
	filehandler.write(content + '\n')
	filehandler.close()



def loadProcess():
	namelist = []
	return int(open('process.txt').read())

def writeProcess(process):
	filehandler = open('process.txt', 'w')
	filehandler.write('%s' % process)
	filehandler.close()

#set cookie
cookies = 'cookies.txt'
cj = LWPCookieJar(cookies)
cj.save()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)


#login to sjjy
username = 'snomhow@gmail.com'
password = '26743021'
requestData = urllib.urlencode([('channel', 200), ('position', 201), ('name', username), ('password', password)])
req = urllib2.Request('https://passport.jiayuan.com/dologin.php?host=www.jiayuan.com&new_header=1&channel=index')
page = urllib2.urlopen(req, requestData).read()


#load process
startPoint = loadProcess()
for i in range(startPoint, 200000):
	writeProcess(str(i))
	print 'processing page %s' % i
	#此链接用来爬取女性图片，如果为男性，则加入&sex=m
	jsonUrl = 'http://search.jiayuan.com/v2/search_v2.php?p=%s' % i
	page = urllib2.urlopen(jsonUrl).read()
	resultjson = json.loads(page)
	userInfoList = resultjson['userInfo']
	for j in range(len(userInfoList)):
		personId = userInfoList[j]['uid']
		gender = userInfoList[j]['sexValue']
		age = userInfoList[j]['age']
		location = userInfoList[j]['work_location']
		helloUrl = userInfoList[j]['helloUrl']
		uhashPattern = re.compile(r'uhash=([a-zA-Z0-9]+)')
		try:
			uhash = uhashPattern.findall(helloUrl)[0]
		except Exception as ep:
			print 'cannot find uhash in helloUrl,%s' % helloUrl
			continue
		picsMainPageUrl = 'http://photo.jiayuan.com/showphoto.php?uid_hash=%s' % uhash
		try:
			picsMainPage = urllib2.urlopen(picsMainPageUrl).read()
		except Exception as ep:
			writeToLog('cannot open pics page for,%s' % picsMainPageUrl)
			continue

		picsUrlPattern = re.compile(r'<img style="[^"]+?" src="([^"]+?)" alt=""/>')
		picsUrlList = picsUrlPattern.findall(picsMainPage)
		print 'there are %s pics for %s' % (len(picsUrlList), picsMainPageUrl)
		if len(picsUrlList) < 5:
			continue
		print 'personid is %s' % personId
		if os.path.exists(str(personId)):
			continue
		os.makedirs(str(personId))
		filehandler = open(os.path.join(str(personId), 'data.txt'), 'w')
		filehandler.write('uid:%s\nage:%s\ngender:%s\nlocation:%s\npicsPage:%s' % (str(personId), str(age), str(gender), str(location), picsMainPageUrl))
		filehandler.close()
		for k in range(len(picsUrlList)):
			picsPath = os.path.join(str(personId), '%s.jpg'%k)
			try:
				urllib.urlretrieve(picsUrlList[k], picsPath)
			except Exception as ep:
				writeToLog('cannot download pics,%s,%s' % (personId, picsUrlList[k]))



