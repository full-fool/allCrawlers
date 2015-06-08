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
import rsa  
import binascii 
from bs4 import BeautifulSoup
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3
writeLock = threading.Lock()
writeDoneWorkLock = threading.Lock()


class WeiboLogin:
    def __init__(self, user, pwd, enableProxy = False):
        "初始化WeiboLogin，enableProxy表示是否使用代理服务器，默认关闭"
        print "Initializing WeiboLogin..."
        self.userName = user
        self.passWord = pwd
        self.enableProxy = enableProxy

        self.serverUrl = "http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.11)&_=1379834957683"
        self.loginUrl = "http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.11)"
        self.postHeader = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:24.0) Gecko/20100101 Firefox/24.0'}


    def Login(self):
        "登陆程序"  
        self.EnableCookie(self.enableProxy)#cookie或代理服务器配置

        serverTime, nonce, pubkey, rsakv = self.GetServerTime()#登陆的第一步
        postData = WeiboEncode.PostEncode(self.userName, self.passWord, serverTime, nonce, pubkey, rsakv)#加密用户和密码
        print "Post data length:\n", len(postData)
        req = urllib2.Request(self.loginUrl, postData, self.postHeader)
        print "Posting request..."
        result = urllib2.urlopen(req)#登陆的第二步——解析新浪微博的登录过程中3
        text = result.read()
        try:
            loginUrl = WeiboSearch.sRedirectData(text)#解析重定位结果
            urllib2.urlopen(loginUrl)
        except:
            print 'Login error!'
            return False

        print 'Login sucess!'
        return True





    def EnableCookie(self, enableProxy):
        "Enable cookie & proxy (if needed)."
        cookiejar = cookielib.LWPCookieJar()#建立cookie
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':'http://xxxxx.pac'})#使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print "Proxy enabled"
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)#构建cookie对应的opener




        #EnableCookie函数比较简单  
    def GetServerTime(self):  
        "Get server time and nonce, which are used to encode the password"  
      
        print "Getting server time and nonce..."  
        #得到网页内容  
        serverData = urllib2.urlopen(self.serverUrl).read()  
        print serverData  
        try:  
            #解析得到serverTime，nonce等  
            serverTime, nonce, pubkey, rsakv = WeiboSearch.sServerData(serverData)  
            return serverTime, nonce, pubkey, rsakv  
        except:  
            print 'Get server time & nonce error!'  
        return None 


    def sServerData(serverData):  
        "Search the server time & nonce from server data"  
      
        p = re.compile('\((.*)\)')  
        jsonData = p.search(serverData).group(1)  
        data = json.loads(jsonData)  
        serverTime = str(data['servertime'])  
        nonce = data['nonce']  
        pubkey = data['pubkey']#  
        rsakv = data['rsakv']#  
        print "Server time is:", serverTime  
        print "Nonce is:", nonce  
        return serverTime, nonce, pubkey, rsakv 


    def sRedirectData(text):  
        p = re.compile('location\.replace\([\'"](.*?)[\'"]\)')  
        loginUrl = p.search(text).group(1)  
        print 'loginUrl:',loginUrl  
        return loginUrl 


 
    def PostEncode(userName, passWord, serverTime, nonce, pubkey, rsakv):  
        "Used to generate POST data"  
      
        #用户名使用base64加密  
        encodedUserName = GetUserName(userName)  
        #目前密码采用rsa加密  
        encodedPassWord = get_pwd(passWord, serverTime, nonce, pubkey)  
        postPara = {  
            'entry': 'weibo',  
            'gateway': '1',  
            'from': '',  
            'savestate': '7',  
            'userticket': '1',  
            'ssosimplelogin': '1',  
            'vsnf': '1',  
            'vsnval': '',  
            'su': encodedUserName,  
            'service': 'miniblog',  
            'servertime': serverTime,  
            'nonce': nonce,  
            'pwencode': 'rsa2',  
            'sp': encodedPassWord,  
            'encoding': 'UTF-8',  
            'prelt': '115',  
            'rsakv': rsakv,       
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',  
            'returntype': 'META'  
        }  
        #网络编码  
        postData = urllib.urlencode(postPara)  
        return postData 


    def GetUserName(userName):  
        "Used to encode user name"  
      
        userNameTemp = urllib.quote(userName)  
        userNameEncoded = base64.encodestring(userNameTemp)[:-1]  
        return userNameEncoded  
  
    def get_pwd(password, servertime, nonce, pubkey):  
        rsaPublickey = int(pubkey, 16)  
        #创建公钥  
        key = rsa.PublicKey(rsaPublickey, 65537)   
        #拼接明文js加密文件中得到  
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)   
        #加密  
        passwd = rsa.encrypt(message, key)   
        #将加密信息转换为16进制。  
        passwd = binascii.b2a_hex(passwd)   
        return passwd  




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

print 'input the start point'
try:
    startPoint = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()


print 'input the people number'
try:
    peopleNum = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
    sys.exit()



threadNum = 1
print 'input the thread number'
try:
    threadNum = int(raw_input())
except Exception as ep:
    print ep.message
    print 'wrong input'
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






