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
	return int(open('process_male.txt').read())

def writeProcess(process):
	filehandler = open('process_male.txt', 'w')
	filehandler.write('%s' % process)
	filehandler.close()


cookies = 'cookies.txt'
cj = LWPCookieJar(cookies)
cj.save()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)


#小图：http://p1.jyimg.com/6a/b7/de98c445350afd1185e488a21e7a/57093610t.jpg
#大图：http://p1.jyimg.com/6a/b7/de98c445350afd1185e488a21e7a/57093610d.jpg

# cookieFile = urllib2.HTTPCookieProcessor()
# opener = urllib2.build_opener(cookieFile)
# opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.92 Safari/537.4')]
# #opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36')]
# #opener.addheaders=[('User-agent', 'User-Agent	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/600.4.10 (KHTML, like Gecko) Version/8.0.4 Safari/600.4.10')]
# urllib2.install_opener(opener)



username = 'snomhow@gmail.com'
password = '26743021'

#password = 'sss2228797'
#hashedpwd = '832399fced8a1abb8eca3247940c13c2'
#hashedpwd = '832399fced8a1abb8eca3247940c13c2'
#page = urllib2.urlopen('http://www.nonobank.com/').read()
requestData = urllib.urlencode([('channel', 200), ('position', 201), ('name', username), ('password', password)])
req = urllib2.Request('https://passport.jiayuan.com/dologin.php?host=www.jiayuan.com&new_header=1&channel=index')
page = urllib2.urlopen(req, requestData).read()
# page = urllib2.urlopen('http://photo.jiayuan.com/showphoto.php?uid_hash=3cd7558bd4d153d62ac8d6f434740320').read()
# filehandler = open('test.html', 'w')
# filehandler.write(page)
# filehandler.close()
# sys.exit()



#requestData = urllib.urlencode([('sex', 'f'), ('stc', '23:1'), ('p', 10000000), ('lifeStyle', 'bigPhoto')])
#req = urllib2.Request('http://search.jiayuan.com/v2/search_v2.php')
#page = urllib2.urlopen(req, requestData).read()
#page = str(urllib2.urlopen(req, requestData).read())[11:-13]

#startPoint = loadProcess()

def getPicsForOneRound():
	for i in range(0, 1000):
		writeProcess(str(i))
		print 'processing page %s' % i
		
		req = urllib2.Request('http://search.jiayuan.com/v2/search_v2.php')
		requestData = urllib.urlencode([('sex', 'm'), ('stc', '23:1'), ('sn', 'default'), ('sv', 1), ('p', i), ('f','select'),\
			('lifeStyle', 'bigPhoto'), ('pri_uid', 0), ('jsversion', 'v5')])
		page = str(urllib2.urlopen(req, requestData).read())[11:-13]

		#此处的url为女性，如果男性的话就在后面加上&sex=m
		#jsonUrl = 'http://search.jiayuan.com/v2/search_v2.php?p=%s' % i
		
		#page = urllib2.urlopen(jsonUrl).read()
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
			if os.path.exists(str(personId)):
				print 'folder %s is already exists\n' % personId
				continue

			picsMainPageUrl = 'http://photo.jiayuan.com/showphoto.php?uid_hash=%s' % uhash
			try:
				picsMainPage = urllib2.urlopen(picsMainPageUrl).read()
			except Exception as ep:
				writeToLog('cannot open pics page for,%s' % picsMainPageUrl)
				continue

			picsUrlPattern = re.compile(r'<img style="[^"]+?" src="([^"]+?)" alt=""/>')
			picsUrlList = picsUrlPattern.findall(picsMainPage)
			print 'there are %s pics for %s\n' % (len(picsUrlList), personId)
			if len(picsUrlList) < 5:
				continue
			#print 'personid is %s' % personId

			os.makedirs(str(personId))
			print 'add one more dir %s' % personId
			filehandler = open(os.path.join(str(personId), 'data.txt'), 'w')
			filehandler.write('uid:%s\nage:%s\ngender:%s\nlocation:%s\npicsPage:%s' % (str(personId), str(age), str(gender), str(location), picsMainPageUrl))
			filehandler.close()
			for k in range(len(picsUrlList)):
				picsPath = os.path.join(str(personId), '%s.jpg'%k)
				try:
					urllib.urlretrieve(picsUrlList[k], picsPath)
				except Exception as ep:
					writeToLog('cannot download pics,%s,%s' % (personId, picsUrlList[k]))


while 1:
	getPicsForOneRound()
	time.sleep(600)
