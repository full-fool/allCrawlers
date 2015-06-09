#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import os
import socket
import threading 
import time
import base64  
import cookielib
import rsa  
import binascii 
from bs4 import BeautifulSoup
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3
writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()



userName = '593980756@qq.com'
passWord = 'cyq591208cyq'
enableProxy = False
serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1379834957683"
#loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)"
loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)"
postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}

 
  
cookie_jar = cookielib.MozillaCookieJar()  
cookies = open('cookie.txt').read()  
for cookie in json.loads(cookies):  
    #print cookie['name']  
    cookie_jar.set_cookie(cookielib.Cookie(version=0, name=cookie['name'], value=cookie['value'], port=None, port_specified=False, domain=cookie['domain'], domain_specified=False, domain_initial_dot=False, path=cookie['path'], path_specified=True, secure=cookie['secure'], expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False))      




headers = ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
opener.addheaders = [headers]
urllib2.install_opener(opener)

#pageContent = getPageWithSpecTimes(0, 'http://weibo.com/p/1003063952070245/album?from=page_100306&mod=TAB#place')
# pageContent = urllib2.urlopen('http://weibo.com/p/1003063952070245/album?from=page_100306&mod=TAB#place').read()
# filehandler  = open('testweibo.html', 'w')
# filehandler.write(pageContent)
# filehandler.close()
# sys.exit()



#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    global tryTimes
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
            if alreadyTriedTimes < tryTimes - 1:
                alreadyTriedTimes += 1
                pass
            else:
                return None
    return html

def writeMapping(url, path):
    writeLock.acquire()

    filehandler = open('Mapping_baidu.csv','a')
    filehandler.write(url+','+path+'\n')
    filehandler.close()

    writeLock.release()


def writeProcess(processPath, content):
    filehandler = open(processPath, 'w')
    filehandler.write(content)
    filehandler.close()

def writeToLog(content):
    filehandler = open('log.txt', 'a')
    filehandler.write(content)
    filehandler.close()



class DownloadOneName(threading.Thread):
    #三个参数分别为start，eachlen，totallen
    def __init__(self, name, albumId, pageUrl):
        threading.Thread.__init__(self)
        self.name = name
        self.albumId = albumId
        self.pageUrl = pageUrl

    def run(self):
        name = self.name
        albumId  = self.albumId
        pageUrl = self.pageUrl
        resultJson = getPageWithSpecTimes(0, pageUrl)
        if resultJson == None:
            writeToLog('cannot open json page for catId,%s,%s,%s\n' % (name, albumId, pageUrl))
            return
        if not os.path.exists(os.path.join(name.decode('utf8'), albumId)):
            try:
                os.makedirs(os.path.join(name.decode('utf8'), albumId))
            except Exception as ep:
                print 'cannot makedirs,%s,%s' % (name.decode('utf8'), albumId)

        picIdPattern = re.compile(r'"pic_id":"([0-9a-zA-Z]+?)"') 
        picIdList = picIdPattern.findall(resultJson)
        filehandler = open(os.path.join(name.decode('utf8'), albumId, 'picsUrlList.txt'), 'w')
        for eachId in picIdList:
            filehandler.write('http://imgsrc.baidu.com/forum/pic/item/%s.jpg\n' % eachId)
        filehandler.close()
        writeDoneWork('%s,%s\n' % (name, albumId))



        


def processOnePerson(name):
    encodedName = urllib.quote(name.encode('gbk'))
    url = 'http://tieba.baidu.com/photo/g?kw=%s&ie=utf-8' % encodedName
    pageContent = getPageWithSpecTimes(3, url)
    if pageContent == None:
        writeToLog('cannot open page for person,%s\n' % name)
        return None
    if '还没有创建图册' in pageContent:
        writeToLog('no photo for person,%s\n' % name)
        return []
    
    pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
    try:
        albumsSection = pagesoup.find_all("div", attrs={"id": 'op_move_to_catalogs'})[0]
    except Exception as ep:
        writeToLog('no photo for person,%s\n' % name)
        return []
    catIDPattern = re.compile(r'<li cat-id="([0-9a-zA-Z]+?)">')
    catIDList = catIDPattern.findall(str(albumsSection))
    allAlbumsIdList = []
    for catID in catIDList:
        catIDUrl = 'http://tieba.baidu.com/photo/g?kw=%s&cat_id=%s' % (encodedName, catID)
        pageContent = getPageWithSpecTimes(3, catIDUrl)
        if pageContent == None:
            writeToLog('cannot open for person and catID,%s,%s\n' % (name, catID))
            continue
        albumUrlPattern = re.compile(r'<a class="grbm_ele_a grbm_ele_big" hidefocus="true" target="_blank" href="/p/(\d+)">')
        allAlbumsIdList += albumUrlPattern.findall(pageContent)
        pageNum = 1
        while '下一页' in pageContent:
            pageNum += 1
            catIDUrl = 'http://tieba.baidu.com/photo/g?kw=%s&cat_id=%s&pn=%s' % (encodedName, catID, pageNum)
            pageContent = getPageWithSpecTimes(3, catIDUrl)
            if pageContent == None:
                writeToLog('cannot open for person and catID and page,%s,%s\n' % (name, catID, pageNum))
                continue
            albumUrlPattern = re.compile(r'<a class="grbm_ele_a grbm_ele_big" hidefocus="true" target="_blank" href="/p/(\d+)">')
            allAlbumsIdList += albumUrlPattern.findall(pageContent)


    return allAlbumsIdList

    #print allAlbumsIdList
    #print len(allAlbumsIdList)

#processOnePerson('范冰冰')
#sys.exit()



def writeDoneWork(name):
    writeDoneWorkLock.acquire()
    
    filehandler = open('doneWork_downloadPicsUrlTieba.txt', 'a')
    filehandler.write(name)
    filehandler.close()
    
    writeDoneWorkLock.release()

def loadDoneWork():
    try: 
        #doneWorkListPath = os.path.join(doneWorkPath, 'doneWork_downloadPicsUrlTieba.txt')
        return open('doneWork_downloadPicsUrlTieba.txt').read().split('\n')
    except Exception as ep:
        return []


def getListFromFile(fileName):
    namelist = []
    for line in open(fileName):
        for line2 in line.split('\r'):
            line2 = re.sub(r'\n', '', line2)
            if line2 != '':
                namelist.append(line2)

    return namelist



#李晨 1259193624
getAlbumIdUrl = 'http://photo.weibo.com/albums/get_all?uid=1259193624&page=1&count=1000'
albumListJson = getPageWithSpecTimes(0, getAlbumIdUrl)

print albumListJson
sys.exit()
pageContent = getPageWithSpecTimes(0, 'http://s.weibo.com/weibo/%25E6%259D%258E%25E6%2599%25A8&Refer=STopic_box')   
filehandler  = open('testweibo.html', 'w')
filehandler.write(pageContent)
filehandler.close()
uidPattern = re.compile(r'uid=(\d+)&name')
#linkPattern = re.compile(r'<div class=\\"star_pic\\"><a href=\\"([^"]+?)" target=')
#uid = uidPattern.findall(pageContent)[0]
uid = '1259193624'
#albumsListUrl = 'http://photo.weibo.com/%s/albums/index?from=profile_wb' % uid
#albumListPage = getPageWithSpecTimes(0, albumsListUrl)
#getAlbumIdUrl = 'http://photo.weibo.com/albums/get_all?uid=%s&page=1&count=1000' % uid
time.sleep(2)
getAlbumIdUrl = 'http://photo.weibo.com/albums/get_all?uid=1259193624&page=1&count=1000'
albumListJson = getPageWithSpecTimes(0, getAlbumIdUrl)

print albumListJson
albumIdPattern = re.compile(r'"album_id":"(\d+)"')

albumIdList = albumIdPattern.findall(albumListJson)
print 'there are %s albums' % len(albumIdList)
#albumUrl = 'http://photo.weibo.com/%s/photos/detail/photo_id/3789240839318665/album_id/4913832'
for eachAlbumId in albumIdList:
    albumPicsJsonUrl = 'http://photo.weibo.com/photos/get_all?uid=%s&album_id=%s&count=10000&page=1' % (uid, eachAlbumId)
    albumPicsJson = getPageWithSpecTimes(0, getAlbumIdUrl)
    picNamePattern = re.compile(r'"pic_name":"([^"]+?)"')
    picNameListForAlbum = picNamePattern.findall(albumPicsJson)
    dirPath = os.path.join(uid, eachAlbumId)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    picsUrlListFilePath = os.path.join(dirPath, 'picsUrlList.txt')
    filehandler = open(picsUrlListFilePath, 'w')
    for eachPicName in picNameListForAlbum:
        filehandler.write('http://ww1.sinaimg.cn/mw690/%s\n' % eachPicName)
    filehandler.close()
    print 'album %s has done' % eachAlbumId


#print link
#pagesoup = BeautifulSoup(pageContent, from_encoding='utf8')
#outfits_gridSection = pagesoup.find_all("p", attrs={"class": "star_card"})[0]
#print outfits_gridSection
sys.exit()




threadNumPool = {}
totalNameList = getListFromFile('namelist.txt')
namelist = totalNameList[startPoint:startPoint+peopleNum]
if not os.path.exists('%s-%s' % (startPoint+1, startPoint+peopleNum)):
    os.makedirs('%s-%s' % (startPoint+1, startPoint+peopleNum))
os.chdir('%s-%s' % (startPoint+1, startPoint+peopleNum))


doneWorkList = loadDoneWork()


for i in range(len(namelist)):
    print 'processing %s/%s' % (i, peopleNum)
    name = namelist[i]
    if name in doneWorkList:
        print 'alrady process %s, has no pics' % name
        continue
    tempIdList = processOnePerson(name)
    if tempIdList == None:
        continue

    print 'fetch all %s url for %s' % (len(tempIdList), name)
    if len(tempIdList) == 0:
        writeDoneWork(name+'\n')
        continue
    for eachId in tempIdList:
        #pageUrl = 'http://tieba.baidu.com%s' % eachId
        if '%s,%s' % (name, eachId) in doneWorkList:
            print 'done for %s,%s' % (name, eachId)
            continue
        
        encodedName = urllib.quote(name.encode('gbk'))

        picPageUrl = 'http://tieba.baidu.com/photo/g/bw/picture/list?kw=%s&tid=%s&pn=1&pe=10000' % (encodedName, eachId)

        findThread = False
        while findThread == False:
            for j in range(threadNum):
                if not threadNumPool.has_key(j):
                    threadNumPool[j] = DownloadOneName(name, eachId, picPageUrl)
                    threadNumPool[j].start()
                    findThread = True
                    break
                else:
                    if not threadNumPool[j].isAlive():
                        threadNumPool[j] = DownloadOneName(name, eachId, picPageUrl)
                        threadNumPool[j].start()
                        findThread = True
                        break
            if findThread == False: 
                time.sleep(5)






