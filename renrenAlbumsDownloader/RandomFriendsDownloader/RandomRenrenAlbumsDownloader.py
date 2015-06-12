#coding=utf-8
#usage: python faceQuery.py paramA paramB 
#       paramA  ---     the username of www.renren.com
#       paramB  ---     the password of www.renern.com
#       Warning ---     make sure that these two params are nested in '', e.g.: python login.py 'chengli.thu@gmail.com' 'THUcst)('
#                       All folders and log will be created in the current directory!
#        
# 每次结束时会记录下没有查询其朋友列表的人的id               

import urllib2, urllib
import sys
import re
import socket
import os
import threading
import getpass
import cookielib
import time
from bs4 import BeautifulSoup


socket.setdefaulttimeout(10)

reload(sys)

sys.setdefaultencoding('utf8')

#global variables list
opener = 0
userid = 0
requestToken = 0 
_rtk = 0
LoginUrl = 'http://www.renren.com/Login.do'
WriteLock = threading.Lock()
writeDoneWorkLock = threading.Lock()
writeTodoIdLock = threading.Lock()
donePicsWorkListLock = threading.Lock()




'''
print 'please input your renren account username'
username = raw_input()
print 'please input your renren account password' 
#password = raw_input()
password = getpass.getpass('password: ')
#print pwd

print 'please input the absolute path of the directory in which you want to put the photos'
rootDirectory = 0
while 1:
    rootDirectory = raw_input()
    if not os.path.exists(rootDirectory):
        print 'please input the right path'
    else:
        break
os.chdir(rootDirectory)

'''
username = 'cyq2210@gmail.com'
password = 'THUcst2014!'
rootDirectory = '.'






cookies = 'cookies.txt'
cj = cookielib.LWPCookieJar(cookies)
cj.save()


headers = ('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36')

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [headers]
urllib2.install_opener(opener)



def writeDoneWork(doneWork):
    writeDoneWorkLock.acquire()

    # state 1 means has searched the friend list for one, 2 means has download the pics
    filehandler = open('doneWork_renren.txt', 'a')
    filehandler.write(doneWork + '\n')
    filehandler.close()

    writeDoneWorkLock.release()


def loadDoneWork():

    try:
        return open('doneWork_renren.txt').read().split('\n')
    except Exception: 
        return []

def writeToDoId(personId):
    writeTodoIdLock.acquire()

    filehandler = open('todoPersonIdList.txt', 'a')
    filehandler.write(personId+'\n')
    filehandler.close()

    writeTodoIdLock.release()


def loadToDoId():
    try:
        fileLines = open('todoPersonIdList.txt').read().split('\n')
        resultLines = []
        for eachLine in fileLines:
            if eachLine != '':
                resultLines.append(eachLine)
        filehandler = open('todoPersonIdList.txt', 'w')
        filehandler.close()
        return resultLines
    except Exception:
        return []

def addDonePicsWorkList(personId):
    global donePicsWorkList
    donePicsWorkListLock.acquire()
    donePicsWorkList.append(personId)
    donePicsWorkListLock.release()


#type 0,justopen, 1,gb2312, 2,gbk, 3,GBK, 4,utf-8
def getPageWithSpecTimes(decodeType, url):
    tryTimes = 4
    alreadyTriedTimes = 0
    html = None
    while alreadyTriedTimes < tryTimes:
        try:
            if decodeType == 0:
                html = urllib2.urlopen(url).read()                
            elif decodeType == 1:
                html = urllib2.urlopen(url).read().decode('gb2312', 'ignore').encode('utf8')
            elif decodeType == 2:
                html = urllib2.urlopen(url).read().decode('gbk', 'ignore').encode('utf8')
            elif decodeType == 3:
                html = urllib2.urlopen(url).read().decode('GBK', 'ignore').encode('utf8')
            else:
                html = urllib2.urlopen(url).read()
            break
        except Exception as ep:
            alreadyTriedTimes += 1
            print 'cannot open page %s for %s times' % (url, alreadyTriedTimes)
            if alreadyTriedTimes == 1:
                time.sleep(1)
            elif alreadyTriedTimes == 2:
                time.sleep(60)
            elif alreadyTriedTimes == 3: 
                time.sleep(300)
            else:
                return None
    return html


#define the downloading thread, one thread download 20 friends's albums
class fetchPicsForOnePerson(threading.Thread):
    def __init__(self, friendId):
        threading.Thread.__init__(self)
        self.friendId = friendId

    def run(self):
        friendId = self.friendId
        print 'downloading pics for %s' % friendId
        if not os.path.exists('renren_'+friendId):
            os.makedirs('renren_'+friendId)
        albumsList, albumNamesList= GetAlbumListForId(friendId) 
        if len(albumsList) == 0:
            return   
        for album in albumsList:
            photosList = GetPhotosForAlbum(album, friendId) 
            picsUrlListPath = os.path.join('renren_%s' % friendId, album)
            if not os.path.exists(picsUrlListPath):
                os.makedirs(picsUrlListPath)
            filehandler = open(os.path.join(picsUrlListPath, 'picsUrlList.txt'), 'w')
            for eachPhotoUrl in photosList:
                validPhotoUrl = eachPhotoUrl.replace('\\', '')
                filehandler.write(validPhotoUrl + '\n')
            filehandler.close()

            #DownloadAlbum(friendId, photosList, album)
            #print 'album processed for,%s,%s' % (friendId, album)
        print 'done for person,%s' % friendId
        writeDoneWork('%s,%s' % (friendId, 2))
        addDonePicsWorkList(friendId)
           

class GetSomeFriend(threading.Thread):
    def __init__(self, personId):
        threading.Thread.__init__(self)
        self.personId = personId

    def run(self):
        personId = self.personId
        GetSomeFriend(personId)

            




def loginWithUsernameAndPassword(username, password):
    username = username
    password = password
    print "Trying to login using username %s" % username
    loginData = urllib.urlencode([('email', username), 
                ('password', password), 
                ('origURL', 'http://www.renren.com'), 
                ('formName', ''), 
                ('method', ''),
                ('isplogin', 'true'),
                ('submit', '登录')])

    #postData = urllib.urlencode(loginData)
    LoginUrl = 'http://www.renren.com/Login.do'

    req = urllib2.Request(LoginUrl)

    resultHtml = urllib2.urlopen(req, loginData).read()

    return resultHtml



def FindInfoWhenLogin(rawHtml):
    global userid, requestToken, _rtk
    try:
    #userid = userIdPattern.search(rawHtml).group(1)
        userIdPattern = re.compile(r'id : \"(\d+?)\"')
        userid = userIdPattern.findall(rawHtml)[0]
        TokenPattern = re.compile(r'requestToken : \'(-?\d+?)\'')
        requestToken = TokenPattern.findall(rawHtml)[0]
        RtkPattern = re.compile(r'_rtk : \'(.*?)\'')
        _rtk = RtkPattern.findall(rawHtml)[0]
        #print "userid: %s, token: %s, rtk: %s" % (userid, requestToken, _rtk)
        isLogin = True      
        return isLogin
    except Exception as ep:
        print ep.message
        print 'Failed...'
        return False


#返回id和人名的tuple的list
def GetSomeFriend(personId):
    global friendIdList, doneFriendsWorkList, fetchFriendsExceed,
    url = 'http://www.renren.com/%s/profile' % personId
    personMainPage = getPageWithSpecTimes(0, url)
    if personMainPage == None:
        print 'cannot open main page for person,%s' % personId
        return
    if '验证码' in personMainPage:
        fetchFriendsExceed = True
        print 'cannot find more friends info now'
        doneFriendsWorkList.append(personId)
        return
    pagesoup = BeautifulSoup(personMainPage, from_encoding='utf8')
    try:
        someFriendSection = pagesoup.find_all("div", attrs={"class": 'has-friend'})[0]
        allLiList = someFriendSection.find_all('li')
        for eachLi in allLiList:
            friendId = eachLi.a.get('namecard')
            friendIdList.append(friendId)
        writeDoneWork('%s,%s' % (personId, 1))
    except Exception as ep:
        writeToDoId(personId)
        print 'cannot find has-friend section for person,%s' % personId

    doneFriendsWorkList.append(personId)







def GetAlbumListForId(friendId):
    #'http://photo.renren.com/photo/60525895/albumlist/v7'
    url =  'http://photo.renren.com/photo/%s/albumlist/v7' % friendId
    try: 
        req = urllib2.Request(url)
        result = opener.open(req)
        rawHtml = result.read()
        getAlbumIdListPattern = re.compile(r'"albumId":"(\d+?)","ownerId"')
        AlbumList = getAlbumIdListPattern.findall(rawHtml)
        getAlbumNameListPattern = re.compile(r'"albumName":(.+?)","albumId"', re.S)
        AlbumNamesList = getAlbumNameListPattern.findall(rawHtml)
        return AlbumList, AlbumNamesList
    except Exception as ep:
        print ep.message
        return [],[]

def GetPhotosForAlbum(albumId, friendId):
    try:
        url = 'http://photo.renren.com/photo/%s/album-%s/v7' % (friendId, albumId)
        req = urllib2.Request(url)
        result = opener.open(req)
        rawHtml = result.read()
        #'"url":"http://fmn.rrfmn.com/fmn061/20140615/0255/original_R1Ge_57c600015322118c.jpg"}'
        #reg = r'"objURL":"(.+?\.[Jj][Pp][Ee]?[Gg])'
        photoUrlPattern = re.compile(r'"url":"(.+?)"')
        photoUrlsList = photoUrlPattern.findall(rawHtml)
        return photoUrlsList
    except Exception as ep:
        print ep.message
        return []




def DownloadAlbum(friendId, photosList, albumId):
    count = 0

    for item in photosList:
        count += 1
        DatePattern = re.compile(r'/(\d{8})/')
        dateList = DatePattern.findall(item)
        date = 0


        if len(dateList) != 0:
            date = dateList[0]
        else:
            date = 'nodate'

        #print friendId, albumId
        newPath = os.path.join('renren_%s'%friendId, albumId)
        if not os.path.exists(newPath):
            os.makedirs(newPath)
            print 'make directory %s' % str(newPath)


        if not os.path.exists(os.path.join(newPath, '%s_%s.jpg'%(date, str(count)))):
            try:
                filePath = os.path.join(newPath, '%s_%s.jpg'%(date, str(count)))
                urllib.urlretrieve(item, filePath)
            except Exception as ep:
                print ep.message
                WriteLock.acquire()
                filehandler = open('errorlog.txt', 'a')
                filehandler.write(item+','+friendId+','+albumId+','+date+','+str(count)+',\n')
                filehandler.close()
                WriteLock.release()
  





friendIdList = loadToDoId()
#friendIdList = ['395403453', '464455179', '281413186', '540254451', '407714102', '229421625', '283145120']
alreadyDoneWork = loadDoneWork()
doneFriendsWorkList = []
donePicsWorkList = []
fetchFriendsExceed = False


# login
rawHtml = loginWithUsernameAndPassword(username, password)
if not FindInfoWhenLogin(rawHtml):
    print 'cannot login, please try again'
    sys.exit()
print 'login successfully'




threadNum = 100
threadNumPool = {}
friendIdListTimes = 0
while len(donePicsWorkList) < 1000:
    if len(friendIdList) == 0:
        friendIdListTimes += 1
        if friendIdListTimes == 10:
            print 'cannot find more friendId now'
            for eachFriendId in friendIdList:
                writeToDoId(eachFriendId)
            sys.exit()
        time.sleep(1)
        continue


    processId = friendIdList[0]
    friendIdList.remove(friendIdList[0])
    

    if fetchFriendsExceed == False:

        if not ('%s,%s' % (processId,1) in alreadyDoneWork or processId in doneFriendsWorkList):
            print 'fetching friends info for %s' % processId
            GetSomeFriend(processId)
        else:
            print 'already find friends for %s' % processId


    if '%s,%s' % (processId, 2) in alreadyDoneWork or processId in donePicsWorkList:
        print 'already done pics for %s' % processId
        continue

    findThread = False
    while findThread == False:
        for j in range(threadNum):
            if not threadNumPool.has_key(j):
                threadNumPool[j] = fetchPicsForOnePerson(processId)
                threadNumPool[j].start()
                findThread = True
                break
            else:
                if not threadNumPool[j].isAlive():
                    threadNumPool[j] = fetchPicsForOnePerson(processId)
                    threadNumPool[j].start()
                    findThread = True
                    break
        if findThread == False: 
            time.sleep(5)












