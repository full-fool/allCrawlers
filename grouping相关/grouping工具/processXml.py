#coding=utf-8
import random
import os
import sys
import re
import uuid
from bs4 import BeautifulSoup


reload(sys)   
sys.setdefaultencoding('utf8')  


uuidList = []
def genUUID():
	global uuidList
	newUUID = None
	while 1:
		newUUID = uuid.uuid4()
		if not str(newUUID) in uuidList:
			uuidList.append(str(newUUID))
			break
	return str(newUUID)


print 'input the prefix of pictures'
prefix = str(raw_input())



filehandler = open('result_%s.csv' % prefix, 'w')
filehandler.write('picName,personName,faceId,left,top,right,bottom\n')
fileContent = open('index.xml').read()
pagesoup = BeautifulSoup(fileContent, from_encoding='utf8')
folderList = pagesoup.find_all('folder')
for eachFolder in folderList:
	totalFolderName = str(eachFolder.get('name'))
	#print 'folder name is %s' % totalFolderName
	shorterForlderName = totalFolderName.split('\\')[-2]
	fileList = eachFolder.find_all('file')
	
	for eachFile in fileList:
		picName = str(os.path.join(shorterForlderName ,str(eachFile.get('name')))) 
		#print 'shorterForlderName is %s and fileName is %s' % (shorterForlderName, str(eachFile.get('name')))

		#<face contact_name="m1" rect_left="0.626383" rect_top="0.387503" rect_right="0.768063" rect_bottom="0.643748"/>
	#	personInfoPattern = re.compile(r'<face contact_name="(.+?)" rect_left="(.+?)" rect_top="(.+?)" rect_right="(.+?)" rect_bottom="(.+?)"/>')
		personInfoPattern = re.compile(r'<face contact_name="(.+?)" rect_bottom="(.+?)" rect_left="(.+?)" rect_right="(.+?)" rect_top="(.+?)"')

		personInfoList = personInfoPattern.findall(str(eachFile))
		#if len(personInfoList) == 0:
		#	print str(eachFile) + '\n\n'
		#print len(personInfoList)
		#continue
		for eachPerson in personInfoList:
			personName = eachPerson[0]
			left = eachPerson[2]
			top = eachPerson[4]
			right = eachPerson[3]
			bottom = eachPerson[1]
			faceuuid = genUUID()
			filehandler.write('%s,%s,%s,%s,%s,%s,%s\n' % (picName,personName,faceuuid,left,top,right,bottom))

