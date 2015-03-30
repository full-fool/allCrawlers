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
import time
from bs4 import BeautifulSoup
import uuid
socket.setdefaulttimeout(50)
reload(sys)
sys.setdefaultencoding('utf8')

tryTimes = 3

string = \
'''
<div class="area_box province_box" style="z-index: 9999999; left: 559.375px; top: 164px;"><div class="pleasechoosebox">请选择省/直辖市</div><ul class="area_box_tr"><li><a href="javascript:void(0)" v="10102000">北京</a></li><li><a href="javascript:void(0)" v="10103000">上海</a></li><li><a href="javascript:void(0)" v="10101002">广州</a></li><li><a href="javascript:void(0)" v="10101201">深圳</a></li><li><a href="javascript:void(0)" v="10105000">重庆</a></li><li><a href="javascript:void(0)" v="10104000">天津</a></li></ul><ul class="area_box_tr"><li><a href="javascript:void(0)" v="10101000" class="select">广东</a></li><li><a href="javascript:void(0)" v="10118000">江苏</a></li><li><a href="javascript:void(0)" v="10131000">浙江</a></li><li><a href="javascript:void(0)" v="10127000">四川</a></li><li><a href="javascript:void(0)" v="10107000">福建</a></li><li><a href="javascript:void(0)" v="10124000">山东</a></li><li><a href="javascript:void(0)" v="10115000">湖北</a></li><li><a href="javascript:void(0)" v="10112000">河北</a></li><li><a href="javascript:void(0)" v="10125000">山西</a></li><li><a href="javascript:void(0)" v="10121000">内蒙古</a></li><li><a href="javascript:void(0)" v="10120000">辽宁</a></li><li><a href="javascript:void(0)" v="10117000">吉林</a></li><li><a href="javascript:void(0)" v="10114000">黑龙江</a></li><li><a href="javascript:void(0)" v="10106000">安徽</a></li><li><a href="javascript:void(0)" v="10119000">江西</a></li><li><a href="javascript:void(0)" v="10113000">河南</a></li><li><a href="javascript:void(0)" v="10116000">湖南</a></li><li><a href="javascript:void(0)" v="10109000">广西</a></li><li><a href="javascript:void(0)" v="10111000">海南</a></li><li><a href="javascript:void(0)" v="10110000">贵州</a></li><li><a href="javascript:void(0)" v="10130000">云南</a></li><li><a href="javascript:void(0)" v="10128000">西藏</a></li><li><a href="javascript:void(0)" v="10126000">陕西</a></li><li><a href="javascript:void(0)" v="10108000">甘肃</a></li><li><a href="javascript:void(0)" v="10123000">青海</a></li><li><a href="javascript:void(0)" v="10122000">宁夏</a></li><li><a href="javascript:void(0)" v="10129000">新疆</a></li></ul><ul class="area_box_tr2"><li><a href="javascript:void(0)" v="10133000">香港</a></li><li><a href="javascript:void(0)" v="10132000">澳门</a></li><li><a href="javascript:void(0)" v="10134000">台湾</a></li><li><a href="javascript:void(0)" v="10200000">国外</a></li><li><a href="javascript:void(0)" v="-1">不限</a></li></ul></div>
'''
filehandler = open('provinceinfo.txt','a')
provinceCodePattern = re.compile(r'v="(\d+)"')
provinceList = provinceCodePattern.findall(string)
for provinceCode in provinceList:
	queryUrl = 'http://i0.zastatic.com/zhenai3/js/syscode2014/district/c%s.js' % provinceCode
	pageContent = urllib.urlopen(queryUrl).read()
	districtCodePattern = re.compile(r'"c(\d+)":{n:')
	districtCodeList = districtCodePattern.findall(pageContent)
	for districtCode in districtCodeList:
		filehandler.write(provinceCode+','+districtCode+'\n')

