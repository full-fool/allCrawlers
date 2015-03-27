#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
import time
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

#print 'please input the absolute of the directory which contains the .csv file'
#os.chdir('E:\cyq\'s document\data\CarData\Sina\sinajustforlink')
try:
	CarInfoFile = open('allbrandinfo.csv').read().split('\n')
except Exception as ep:
	print 'open file error'
	sys.exit()
if '\n' in CarInfoFile:
	CarInfoFile.remove('\n')
TypesNum = len(CarInfoFile)

#carinfo stores series of tuples, there are brand id, brand name, type id, type name in each tuple 
carinfo = []
for i in range(TypesNum):
	templist = CarInfoFile[i].split(',')
	temptuple = (templist[0], templist[1], templist[2], templist[3])
	carinfo.append(temptuple)

def loadProcess():
    try:
       carBrandNum = int(open('process.txt').read())
       return carBrandNum
    except Exception as ep:
        print 'wrong with the process.txt'
        sys.exit()

def setProcess(process):
    filehandler = open('process.txt', 'w')
    filehandler.write(process)
    filehandler.close()



def writeToLog(content):
	filehandler = open('log.txt', 'a')
	filehandler.write(content + '\n')
	filehandler.close()


#type 0,just read, 1,gb2312, 2,gbk, 3,GBK
def getPageWithSpecTimes(decodeType, url):
    global tryTimes
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
            	html = urllib2.urlopen(url)
            elif decodeType == 1:
                html = urllib2.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib2.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            elif decodeType == 3:
                html = urllib2.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else :
            	html = urllib2.urlopen(url).read()
            break
        except Exception as ep:
            alreadyTriedTimes += 1
            if alreadyTriedTimes < tryTimes:
                time.sleep(200 * alreadyTriedTimes)
                print 'sleeping for %s secs now for %s' % (200*alreadyTriedTimes, url) 
                pass
            else:
                return None
    return html



	

alreadyDoneCarBrand = loadProcess()
#for i in range(len(carinfo)):
for i in range(alreadyDoneCarBrand, len(carinfo)):
	setProcess(str(i))
	print carinfo[i][1], carinfo[i][3]
	#外观图中pic_type=1, 官方图pic_type=7
	queryUrl = 'http://photo.auto.sina.com.cn/interface/v2/general/get_car_photo.php?subid=%s&pic_type=7&page=1&limit=10000' % carinfo[i][2]
	mainPage = getPageWithSpecTimes(0, queryUrl)
	jsonresult = json.load(mainPage)

	try:
		img_list = jsonresult['result']['data']['type_data'][0]['img_list']
	except Exception as ep:
		print 'cannot find img_list for %s,%s,%s' % (carinfo[i][1], carinfo[i][3], queryUrl)
		continue
	picsNum = len(img_list)
	if picsNum == 0:
		continue
	for j in range(picsNum):
		yearPattern = re.compile(r'([\d]{4})款')
		if len(yearPattern.findall(img_list[j]['title'].encode('utf8'))) == 0:
			continue
		year = yearPattern.findall(img_list[j]['title'].encode('utf8'))[0]
		#print 'year is %s' % year
		newPath = os.path.join(carinfo[i][1], carinfo[i][3], year)
		if not os.path.exists(newPath):
			os.makedirs(newPath)
		filePath = os.path.join(newPath, 'picsUrlList.txt')
		filehandler = open(filePath, 'a')
		imgUrl = img_list[j]['img_340']
		bigImgUrl = imgUrl.replace('_340', '_950')
		filehandler.write(bigImgUrl + '\n')
		filehandler.close()



