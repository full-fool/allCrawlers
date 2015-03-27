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


#requestData = urllib.urlencode([('sex', 'f'), ('stc', '23:1'), ('sn', 'default'), ('sv', 1), ('p', 10000000), ('f','select'),\
#	('lifeStyle', 'bigPhoto'), ('pri_uid', 0), ('jsversion', 'v5')])
#requestData = urllib.urlencode([('sex', 'f'), ('stc', '23:1'), ('p', 10000000), ('lifeStyle', 'bigPhoto')])
#req = urllib2.Request('http://search.jiayuan.com/v2/search_v2.php')
#page = urllib2.urlopen(req, requestData).read()
#page = str(urllib2.urlopen(req, requestData).read())[11:-13]

startPoint = loadProcess()


for i in range(0, 10):
	writeProcess(str(i))
	print 'processing page %s' % i
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

sys.exit()


print len(resultjson['userInfo'])
print resultjson['userInfo'][8]['uid']
sys.exit()
print resultjson['userInfo'][0]['income']
sys.exit()
#print page



print page
if '"result":1' in page:
	print 'login successfully'
else:
	print 'cannot login'
	sys.exit()

cj.save()


for i in range(pageNum, 46):
	#url  = 'http://www.nonobank.com/Lend/GetLendList/8/%s' % i
	#pageJson =  json.load(urllib2.urlopen(url))
	#filehandler = open('%s.json' % i, 'w')
	#filehandler.write(page)
	#filehandler.close()
	time.sleep(2)
	pageJson = json.load(open('%s.json' % i))
	peopleNumPerPage = len(pageJson['members'])
	print 'page %s has %s ' % (i, peopleNumPerPage)
	#for j in range(1):
	for j in range(peopleNum, peopleNumPerPage):
		writeProcess(str(i), str(j))
		
		print 'people %s is processing ' % j
		personInfo = pageJson['members'][j]
		pageId = personInfo['bo_id']

		# if pageId == '73764':
		# 	print '73764 is %s,%s' % (i,j)
		# 	sys.exit()


		borrowId = personInfo['bo_extno']
		guaranteeSituation = personInfo['bidding_cat']
		timeLimit = personInfo['bo_expect']
		bidNum = personInfo['bidding_count']
		bidTime = str(personInfo['bo_agree_time'])
		bidTime = re.sub(r'\s+', '-', bidTime)
		print 'pageId is %s' % pageId
		
		#'https://www.nonobank.com/Lend/View/90138'
		personUrl = 'https://www.nonobank.com/Lend/View/%s' % pageId
		print 'opening url %s' % personUrl
		#personMainPage = getPageWithSpecTimes(0, personUrl)
		personMainPage = None
		try:
			personMainPage = urllib2.urlopen(personUrl).read()
		except Exception as ep:
			writeToLog('cannot open page %s' % personUrl)
			continue			

		cj.save()
		# 借入信用:<span>0</span>分</a>
		if '点此登录' in personMainPage:
			print 'cannot log in'
			filehandler = open('firast.json', 'w')
			filehandler.write(personMainPage)
			filehandler.close()
			sys.exit()
		print 'success get page %s' % personUrl

		jiekuanyongtuPattern = re.compile(r'<div><span>借款用途：</span>(.+?)</div>')
		try:
			jiekuanyongtu = jiekuanyongtuPattern.findall(personMainPage)[0]
		except Exception as ep:
			jiekuanyongtu = 'null'



		borrowCreditPattern = re.compile(r'借入信用:<span>(.+?)</span>分</a>') 
		try:
			borrowCredit = borrowCreditPattern.findall(personMainPage)[0]
		except Exception as ep:
			borrowCredit = 'null'
		#print 'borrowCredit is ', borrowCredit
		
		#<li><span>年利率</span>：11.88%</li>
		yearRatePattern = re.compile(r'<li><span>年利率</span>：(.+?)</li>')
		try:
			yearRate = yearRatePattern.findall(personMainPage)[0]
		except Exception as ep:
			yearRate = 'null'
		#print 'yearRate is ', yearRate

		#<li><span>借款金额</span>：￥800</li>
		moneyPattern = re.compile(r'<li><span>借款金额</span>：(.+?)</li>')
		try:
			money = moneyPattern.findall(personMainPage)[0]
			money = re.sub(',','',money)
		except Exception as ep:
			money = 'null'


		ensureTypePattern = re.compile(r'<li>保障方式：<a href=".+?" target="_blank">(.+?)</a></li>')
		try:
			ensureType = ensureTypePattern.findall(personMainPage)[0]
		except Exception as ep:
			ensureType = 'null'

		totalBorrowPattern = re.compile(r'<div>共记借入：(.+?)</div>')
		try:
			totalBorrow = totalBorrowPattern.findall(personMainPage)[0]
			totalBorrow = re.sub(',', '', totalBorrow)
		except Exception as ep:
			totalBorrow ='null'

		toReturnMoneyPattern = re.compile(r'<div>待还本金：(.+?)</div>')
		try:
			toReturnMoney = toReturnMoneyPattern.findall(personMainPage)[0]
			toReturnMoney = re.sub(',','',toReturnMoney)
		except Exception as ep:
			toReturnMoney = 'null'

		normalReturnPattern = re.compile(r'<div>正常还清：(.+?)</div>')
		try:
			normalReturn = normalReturnPattern.findall(personMainPage)[0]
			normalReturn = re.sub(',','',normalReturn)
		except Exception as ep:
			normalReturn = 'null'

		exceedReturnPattern = re.compile(r'<div>逾期还清：(.+?)</div>')
		try:
			exceedReturn = exceedReturnPattern.findall(personMainPage)[0]
			exceedReturn = re.sub(',','',exceedReturn)
		except Exception as ep:
			exceedReturn = 'null'

		exceedNotReturnPattern = re.compile(r'<div>逾期未还：(.+?)</div>')
		try:
			exceedNotReturn = exceedNotReturnPattern.findall(personMainPage)[0]
			exceedNotReturn = re.sub(',','',exceedNotReturn)
		except Exception as ep:
			exceedNotReturn = 'null'

		fabiaoPattern = re.compile(r'<div>发标：(.+?)</div>')
		try:
			fabiao = fabiaoPattern.findall(personMainPage)[0]
		except Exception as ep:
			fabiao = 'null'		

		successPattern = re.compile(r'<div>成功：(.+?)</div>')
		try:
			success = successPattern.findall(personMainPage)[0]
		except Exception as ep:
			success = 'null'

		liubiaoPattern = re.compile(r'<div>流标：(.+?)</div>')
		try:
			liubiao = liubiaoPattern.findall(personMainPage)[0]
		except Exception as ep:
			liubiao = 'null'		

		alreadyReturnedMoneyPattern = re.compile(r'<div>已还总额(.+?)</div>')
		try:
			alreadyReturnedMoney = alreadyReturnedMoneyPattern.findall(personMainPage)[0]
			alreadyReturnedMoney = re.sub(',','',alreadyReturnedMoney)
		except Exception as ep:
			alreadyReturnedMoney = 'null'	

		tobeReturnedMoneyPattern = re.compile(r'<div>待还总额(.+?)</div>')
		try:
			tobeReturnedMoney = tobeReturnedMoneyPattern.findall(personMainPage)[0]
			tobeReturnedMoney = re.sub(',','',tobeReturnedMoney)
		except Exception as ep:
			tobeReturnedMoney = 'null'

		rechargeMoneyPattern = re.compile(r'<div>充值总额：(.+?)</div>')
		try:
			rechargeMoney = rechargeMoneyPattern.findall(personMainPage)[0]
			rechargeMoney = re.sub(',','',rechargeMoney)
		except Exception as ep:
			rechargeMoney = 'null'

		cashPattern = re.compile(r'<div>提现总额：(.+?)</div>')
		try:
			cash = cashPattern.findall(personMainPage)[0]
			cash = re.sub(',','', cash)
		except Exception as ep:
			cash = 'null'

		jiekuanmudiPattern = re.compile(r'<strong>借款目的：(.+?)</strong>')
		try:
			jiekuanmudi = jiekuanmudiPattern.findall(personMainPage)[0]
		except Exception as ep:
			jiekuanmudi = 'null'

		filehandler = open('result.csv', 'a')
		filehandler.write('%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,\n'%(borrowId,\
			jiekuanyongtu, borrowCredit,  yearRate,  money, guaranteeSituation, timeLimit, bidNum, ensureType, totalBorrow, \
			toReturnMoney, normalReturn, exceedReturn, exceedNotReturn, fabiao, success, liubiao, alreadyReturnedMoney, \
			tobeReturnedMoney, rechargeMoney, cash, jiekuanmudi ))
		filehandler.close()
		print 'successfully fetch info from page %s\n' % personUrl


