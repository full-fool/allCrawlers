#coding=utf-8
import json
import sys
import urllib2, urllib
import re
import codecs
import json
import os
import socket
from bs4 import BeautifulSoup
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3




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

def writeToLog(content):
    filehandler = open('log.txt', 'a')
    filehandler.write(content+'\n')
    filehandler.close()

def writeMapping(url, path):

    filehandler = open('Mapping.csv', 'a')
    filehandler.write(url+','+path+',\n')
    filehandler.close()

#一共159种品牌

def getAllCarBrandAndLink():
    carlistLink = 'http://product.auto.163.com/brand/'
    page = getPageWithSpecTimes(1, carlistLink)
    #<a href='/brand/w/#q=g3' title="查看沃尔沃全部车系">
    linkAndBrandPattern = re.compile(r'<a href="(/brand/.+?)" title="进入(.+?)品牌频道">')
    linkAndBrand = linkAndBrandPattern.findall(page)
    
    filehandler = open('carBrand.txt', 'a')
    for item in linkAndBrand:
        filehandler.write('http://product.auto.163.com' + item[0]+','+item[1].decode('utf8')+'\n')
    filehandler.close()
    #print len(linkAndBrand)

#包含开始，也包含结束，表示行号
def loadCarBrandAndLink():
    CarInfoFile = open('carBrand.txt').read().split('\n')
    if '\n' in CarInfoFile:
        CarInfoFile.remove('\n')
    carInfoList=[]
    for i in range(len(CarInfoFile)):
        CarInfoPair = CarInfoFile[i].split(',')
        carInfoList.append((CarInfoPair[0], CarInfoPair[1]))
    #for item in carInfoList:
    #    print item[0], item[1].decode('utf8')
    
    #第一个存链接，第二个存品牌
    return carInfoList

#没有处理返回为空的情况，因此返回的可能是一个空列表，列表中的url是完整的.返回的列表中第一项是某一种车型的主页的url，第二项是车型名称
def getAllTypesFromLink(brand, url):
    #print brand
    #品牌的主页有两种布局，如'http://product.auto.163.com/brand/1738.html#DQ0001'和'http://product.auto.163.com/brand/1703.html'
    brand = brand.strip(' ')
    brandMainPage = getPageWithSpecTimes(1, url)
    if brandMainPage == None:
        print 'cannot open main page for one brand,%s,%s' % (brand, url)
        writeToLog('cannot open main page for one brand,%s,%s' % (brand, url))
        return None

    #第一种主页

    if '全部车系' in brandMainPage:
        #<a title="进入丰田RAV4频道" href="/series/2223.html#0008F08">RAV4</a>
        typeAndLinkPattern = re.compile(r'<a title="进入.+?频道" href="(.+?)">(.+?)</a>')
        typeAndLinkList = typeAndLinkPattern.findall(brandMainPage)
        returnList = []
        for item in typeAndLinkList:
            print 'http://product.auto.163.com'+item[0], item[1].decode('utf8')
            returnList.append(('http://product.auto.163.com' + item[0], item[1].decode('utf8')))
        return returnList
    
    #第二种主页
    else:
        brandMainPage = getPageWithSpecTimes(4, url)

        #<a href="/brand/1738/series.html#pp1001" title="三菱车型" target="_self">品牌车型</a>
        allTypesPageUrlPattern = re.compile(r'<a href="(.+?)" title=".+?" target="_self">品牌车型</a>')
        allTypesPageUrlList = allTypesPageUrlPattern.findall(brandMainPage)
        if len(allTypesPageUrlList) == 0:
            print 'cannot find all types of one brand,%s,%s' % (brand, url)
            writeToLog('cannot find all types of one brand,%s,%s' % (brand, url))
            return None
        allTypesPageUrl = allTypesPageUrlList[0]
        allTypesPage = getPageWithSpecTimes(4, 'http://product.auto.163.com' + allTypesPageUrl)
        if allTypesPage == None:
            print 'cannot open all types for brand,%s,%s' % (brand, allTypesPageUrl)
            writeToLog('cannot open all types for brand,%s,%s' % (brand, allTypesPageUrl))
            return None
        #<h3><a href="/series/2029.html#pp3001">XC90(进口)</a></h3>
        typeAndLinkPattern = re.compile(r'><a href="([^ ]+?)">(.+?)</a></h3>')
        typeAndLinkList =  typeAndLinkPattern.findall(allTypesPage)
        returnList = []
        for item in typeAndLinkList:
            print 'http://product.auto.163.com'+item[0], item[1].decode('utf8')
            returnList.append(('http://product.auto.163.com' + item[0], item[1].decode('utf8')))
        return returnList



        #print brandMainPage


def getAllYearInfo(brand, carType, url):
    typeMainPage = getPageWithSpecTimes(2, url)
    if typeMainPage == None:
        print 'cannot open type main page for car,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url)
        writeToLog('cannot open type main page for car,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url))
        return None
    #product_id:'000BMONE',price:'31.98万',product_name:'2012款 2.5 Royal'
    #yearInfoPattern = re.compile(r'product_id:\'.+?\',price:\'.+?\',product_name:\'(\d+)款.+?\'')
    yearInfoPattern = re.compile(r'([\d]{4})款')
    yearInfoFoundList = yearInfoPattern.findall(typeMainPage)
    yearInfoList = []
    for year in yearInfoFoundList:
        if not year in yearInfoList:
            yearInfoList.append(year)
    #print yearInfoList
    return yearInfoList
         

def downloadPicsForList(brand, carType, productIdAndYearAndSetidList):
    #item中分别为id，年份，setid

    #print len(productIdAndYearAndSetidList)
    for item in productIdAndYearAndSetidList:
        allPicsUrlList = []
        print item
        url = 'http://product.auto.163.com/series/photo/%s_%s_outlook.html' % (item[0], item[2])
        pageForYear = getPageWithSpecTimes(1, url)
        if pageForYear == None:
            print 'cannot open pic page for one year,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url)
            writeToLog('cannot open pic page for one year,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url))
            continue

        #找到随便一个图片入口
        #<a tg_id="wg002" title="皇冠 左前45度" href="http://auto.163.com/photoview/29BK0008/174724/AI18GNVH29BK0008.html">

        entrancePattern = re.compile(r'<a tg_id=".+?" title=".+?"   href="(.+?)">')
        entranceList = entrancePattern.findall(pageForYear)
        if len(entranceList) == 0:
            print 'cannot find entrance pic link,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], url)
            writeToLog('cannot find entrance pic link,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], url))
            continue
        entranceLink = entranceList[0]
        pageForAllPicsForYear = getPageWithSpecTimes(1, entranceLink)
        if pageForAllPicsForYear == None:
            print 'cannot open entrance pic link,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], url)
            writeToLog('cannot open entrance pic link,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], url))
            continue
        #>车身外观<span>(<strong>24</strong>)
        outPicsNumPattern = re.compile(r'<strong>(\d+)</strong>')
        outPicsNumList = outPicsNumPattern.findall(pageForAllPicsForYear)
        #print pageForAllPicsForYear

        #print outPicsNumList
        if len(outPicsNumList) == 0:
            print 'cannot find all out pics in page,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], entranceLink)
            writeToLog('cannot find all out pics in page,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], entranceLink))
            continue
        outPicsNum = int(outPicsNumList[0])
        print 'out pics num is ', outPicsNum

        
        #先把本页下载下来
        #<div class="nph_cnt" id="photoView"><i></i><img src="http://img4.cache.netease.com/photo/0008/2015-02-09/AI18GNVH29BK0008.jpg" alt="丰田皇冠 2015款 2.5L AT尊享版 ——左前" id="photo" /></div>
        thisPagePicUrlPattern = re.compile(r'<div class="nph_cnt" id="photoView"><i></i><img src="(.+?)" alt')
        thisPagePicUrlList = thisPagePicUrlPattern.findall(pageForAllPicsForYear)
        if len(thisPagePicUrlList) == 0:
            print 'cannot find first pic of car,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], entranceLink)
            writeToLog('cannot find first pic of car,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], entranceLink))
        else:
            #print thisPagePicUrlList[0]
            allPicsUrlList.append(thisPagePicUrlList[0])
        alreadHadPicsNum = 1
        
        #再把其他页面的图片下载下来
        while alreadHadPicsNum < outPicsNum:
            alreadHadPicsNum += 1
            #<div class="nph_photo_next"><a href="/photoview/29BK0008/174724/AI18GNCH29BK0008.html" target="_self" class="nph_btn_nphoto" id="photoNext"></a></div>
            nextPagePicUrlPattern = re.compile(r'<div class="nph_photo_next"><a href="(.+?)" target')
            nextPagePicUrlList = nextPagePicUrlPattern.findall(pageForAllPicsForYear)
            if len(nextPagePicUrlList) == 0:
                break
            nextPagePicUrl = 'http://auto.163.com' + nextPagePicUrlList[0]
            pageForAllPicsForYear = getPageWithSpecTimes(1, nextPagePicUrl)
            if pageForAllPicsForYear == None:
                print 'cannot open next page,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], nextPagePicUrl)
                writeToLog('cannot open next page,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], nextPagePicUrl))
                break
            thisPagePicUrlPattern = re.compile(r'<div class="nph_cnt" id="photoView"><i></i><img src="(.+?)" alt')
            thisPagePicUrlList = thisPagePicUrlPattern.findall(pageForAllPicsForYear)
            if len(thisPagePicUrlList) == 0:
                print 'cannot find first pic of car,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], nextPagePicUrl)
                writeToLog('cannot find first pic of car,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), item[1], nextPagePicUrl))
            else:
                #print thisPagePicUrlList[0]
                allPicsUrlList.append(thisPagePicUrlList[0])
        #print 'this item is done ', allPicsUrlList

        if len(allPicsUrlList) > 0:
            newPath = os.path.join(brand.decode('utf8'), carType.decode('utf8'), item[1])
            if not os.path.exists(newPath):
                os.makedirs(newPath)
            filehandler = open(os.path.join(newPath, 'picsUrlList.txt'), 'a')
            for singlePicUrl in allPicsUrlList:
                filehandler.write(singlePicUrl+'\n')
            filehandler.close()



def getAllPicsFromPicUrl(brand, carType, url, yearInfoList):
    #此处的网页也有两种布局，一种如'http://product.auto.163.com/series/2021.html#pp3001'，另一种如'http://product.auto.163.com/series/2225.html'
    #两种界面使用'>车关系<'作为区分
    #http://product.auto.163.com/series/2021.html#pp3001
    IdPattern = re.compile(r'.+?/series/(\d+)\.')
    IdList = IdPattern.findall(url)
    if len(IdList) == 0:
        print 'cannot find car id for car,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url)
        writeToLog('cannot find car id for car,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), url))
        return None
    CarId = IdList[0]
    returnProductIdAndYearAndSetidList=[]
    for year in yearInfoList:
        queryUrl = 'http://product.auto.163.com/auto/json/year_photo/%s_%s.js' % (CarId, year)
        
        page = None
        try:
            page = urllib2.urlopen(queryUrl).read()
        except urllib2.HTTPError:
            print 'httperror for url,%s,%s' % (year, queryUrl)
            continue
        except Exception as ep:
            print ep.message
            print 'cannot get query result,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), year, queryUrl)
            writeToLog('cannot get query result,%s,%s,%s,%s' % (brand.decode('utf8'), carType.decode('utf8'), year, queryUrl))
            continue
        #"productid":"000BKAdY","name":"2009款 冠军1.3MT标准型","createdate":"2012-11-06","setid":"151881"
        productIdAndYearAndSetidPattern = re.compile(r'"productid":"(.+?)","name":"([\d]{4}).+?","createdate":".+?","setid":"(\d+)"')
        productIdAndYearAndSetidList = productIdAndYearAndSetidPattern.findall(page)
        returnProductIdAndYearAndSetidList += productIdAndYearAndSetidList
    #print returnProductIdAndYearAndSetidList
    return returnProductIdAndYearAndSetidList

        #carPicsInfoList = []

#carBrandList中第一个是链接，第二项的.decode('utf8')是品牌名
#carBrandList = getAllCarBrandAndLink()

#getAllCarBrandAndLink()
#loadCarBrandAndLink(1,78)
#listlist = getAllTypesFromLink('丰田', 'http://product.auto.163.com/brand/1686.html#DQ0001')

#alreadDoneCarBrandNum = loadProcess()
#getAllTypesFromLink('丰田', 'http://product.auto.163.com/brand/1747.html#DQ0001')

#allCarBrandLinkList = loadCarBrandAndLink()
#getAllYearInfoAndLink('brand', 'type', 'http://product.auto.163.com/series/2225.html')
#getAllYearInfo('brand', 'type', 'http://product.auto.163.com/series/2225.html')
#getAllYearInfoAndLink('力帆', '320', 'http://product.auto.163.com/series/2148.html')
#getAllPicsFromPicUrl('brand', 'type', 'http://product.auto.163.com/series/2225.html#0008H33', [2010,2012,2013,2015])



#downloadPicsForList('brand','type','2015',[("000BVGUF",'2015',"174724")])
#pageForAllPicsForYear = getPageWithSpecTimes(1, 'http://auto.163.com/photoview/29BK0008/174724/AI18GNVH29BK0008.html')

#print str(urllib2.urlopen('http://auto.163.com/photoview/29BK0008/174724/AI18GNVH29BK0008.html').info())#.decode('gb2312','ignore').encode('utf8')



# try:
#     print urllib2.urlopen('http://product.auto.163.com/auto/json/year_photo/2148_2007.js').read()

# except urllib2.HTTPError:
#     print 'httperror'
# except Exception as ep:
#     print 'other error'



carBrandList = loadCarBrandAndLink()
carBrandNum = loadProcess()

for i in range(carBrandNum, len(carBrandList)):
    print carBrandList[i][1].decode('utf8') 
    carTypeList = getAllTypesFromLink(carBrandList[i][1].decode('utf8'), carBrandList[i][0])
    if carTypeList == None:
        continue
    for carType in carTypeList:
        print carType[1].decode('utf8')
        #tempCarType = carType[1].decode('utf8')
        yearInfoList = getAllYearInfo(carBrandList[i][1].decode('utf8'), carType[1].decode('utf8'), carType[0])
        if yearInfoList == None:
            continue
        productIdAndYearAndSetidList = getAllPicsFromPicUrl(carBrandList[i][1].decode('utf8'), carType[1].decode('utf8'), carType[0], yearInfoList)
        if productIdAndYearAndSetidList == None:
            continue
        downloadPicsForList(carBrandList[i][1].decode('utf8'), carType[1].decode('utf8'), productIdAndYearAndSetidList)
    setProcess(str(i))