#coding=utf-8
#usage: python faceQuery.py paramA paramB 
#       paramA  ---     the username of www.renren.com
#       paramB  ---     the password of www.renern.com
#       Warning ---     make sure that these two params are nested in '', e.g.: python login.py 'chengli.thu@gmail.com' 'THUcst)('
#                       All folders and log will be created in the current directory!
#                       

import urllib2, urllib
import sys
import re
import socket
import os
import threading
import getpass


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

print 'download pics or fill in friends\' persional info? Type in \'d\' or \'f\' to select working mode'
work_mode = 0
while 1:
    work_mode = raw_input()
    if(work_mode == 'd' or work_mode == 'f'):
        break
    else:
        print 'please type in the correct param'



#define the downloading thread, one thread download 20 friends's albums
class DownloadOnePage(threading.Thread):
    def __init__(self, friendlist):
        threading.Thread.__init__(self)
        self.friendlist = friendlist

    def run(self):
        for item in self.friendlist:
            friendId = item[0]
            friendName = item[1]
            if not os.path.exists('renren_'+friendId):
                os.mkdir('renren_'+friendId)
                print 'make directory renren_%s' % friendId

            #writeFriendInfoPage(friendId)   
            #print 'information of %s has been written' % friendId 
            albumsList, albumNamesList= GetAlbumListForId(friendId)    
            for album in albumsList:
                photosList = GetPhotosForAlbum(album, friendId) 
                #print photosList
                #break
                DownloadAlbum(friendId, photosList, album)
                print 'album %s has been downloaded' % album
                

 

def loginWithUsernameAndPassword(username, password):
    global loginurl, opener
    username = username
    password = password
    print "Trying to login using username %s" % username
    loginData = {'email':username,
            'password':password,
            'origURL':'http://www.renren.com',
            'formName':'',
            'method':'',
            'isplogin':'true',
            'submit':'登录'}
    postData = urllib.urlencode(loginData)
    cookieFile = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookieFile)
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.92 Safari/537.4')]
    req = urllib2.Request(LoginUrl, postData)
    result = opener.open(req)
    resultHtml = result.read()
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
def GetFriendList(id):
    global opener
    try:
        url = 'http://friend.renren.com/GetFriendList.do?curpage=%d&id=%s'        
        req = urllib2.Request(url % (0, id))
        result = opener.open(req)
        rawHtml = result.read()
        # print rawHtml
        getPagePattern = re.compile(r'<a title="最后页" href="/GetFriendList.do\?curpage=(\d+?)&amp;',re.S)

        pages = getPagePattern.findall(rawHtml)[0]
        # print pages
        getFriendPattern = re.compile(r'<dd><a href.*?\?id=(\d+?)\">(.*?)</a>')
        friendsList = []
        for i in xrange(0,int(pages)+1):
            req = urllib2.Request(url % (i, id))
            rawHtml = opener.open(req).read()
            onePageFriend = getFriendPattern.findall(rawHtml)
            print 'page %s friends has fetched' % i
            #friendsList.extend(onePageFriend)
            friendsList.append(onePageFriend)
            #for debug
            #break
        return friendsList
    except Exception as ep:
        print ep.message
        print 'GetFriendList failed.'

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


# def writeFriendInfoPage(friendId):
   
#     try:
#         url = 'http://www.renren.com/%s/profile?v=info_timeline' % friendId
#         req = urllib2.Request(url)
#         result = opener.open(req)
#         rawHtml = result.read()
#         if '验证码' in rawHtml:
#             print 'your access to renren.com has reached today\'s limit, please try later'
#             sys.exit()
#         filehandler = open('renren_%s\\info.html' % friendId, 'w')
#         filehandler.write(rawHtml)
#         filehandler.close
#     except Exception as ep:
#         print ep.message



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
  



rawHtml = loginWithUsernameAndPassword(username, password)

if not FindInfoWhenLogin(rawHtml):
    print 'cannot login, please try again'
    sys.exit()
    
friendInfoList = GetFriendList(userid)
if work_mode == 'd':
    for i in range(0, len(friendInfoList)):
        DownloadOnePage(friendInfoList[i]).start()
# else:
#     for i in range(0, len(friendInfoList)):
#         onePageFriendList = friendInfoList[i]
#         for oneFriend in onePageFriendList:
#             friendId = oneFriend[0]
#             if not os.path.exists('renren_'+friendId):
#                 os.mkdir('renren_'+friendId)
#                 print 'make directory renren_' + friendId
#             if not os.path.exists('renren_%s\\info.html' % friendId):
#                 writeFriendInfoPage(friendId)   
           






