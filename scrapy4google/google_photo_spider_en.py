import urllib
import os
import threading
import socket

from scrapy.spider import Spider
from scrapy.selector import HtmlXPathSelector

class GooglePhotoSpider(Spider):
    name = "google_photo_kimi"
    allowed_domains = ["google.com.hk"]
    url_prefix = "https://www.google.com.hk/search?safe=strict&tbm=isch&"
    #"https://www.google.com.hk/search?safe=strict&tbm=isch&q=summer&ijn=1&start=100"

    input_filename = "G:/myProject/Image_tag/list-3.txt"
    output_filename = "list-3.csv"
    output_path = "G:/myProject/Image_tag/photo"

    start_urls = []

    # number * 100
    number = 2
    download_delay = 2 

    id_count = 0

    socket.setdefaulttimeout(0.01)

    input_file = open(input_filename, 'r')
    for line in input_file.readlines():
        for j in range(number):
            start_urls.append(url_prefix + "ijn=" + str(j) + "&start=" + str((j)*100) + "&q=" + str(line))
                              
    #print start_urls

    def __init__(self):
        self.output_file = open(self.output_filename, "w")
        pass

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        print response
        print hxs
        #self.output_file.write(str(response))
        #self.output_file.write('\n\n')
        self.id_count = 0
        name = response.url.split('&q=')[-1].split('%')[0]

        for images in hxs.select("//div[@class='rg_di rg_el']"):
            try:
                url = images.select("a/@href").extract()[0]

                img_url = url.split('imgurl=')[1].split('&imgrefurl=')[0]
                suffix = img_url.split('.')[-1]
                description = images.select("div[@class='rg_meta']").extract()[0]
                pt = description.split('"pt":"')[-1].split('","')[0]
                pid = description.split('"id":"')[-1].split('","')[0]
                print '******************************************'
                print name
                print str(self.id_count) + ': ' + pid[:-1]
                

                #url = image.select("@m").extract()[0].split(',')[4].split('"')[1]
                #thumbnail = image.select("img/@src2").extract()[0]
                #print thumbnail
                #pid = thumbnail.split('&')[0].split('.')[-1]
                #print pid
                #suffix = url.split('.')[-1]
                path = self.output_path + '/' + name
                filename = path + '/' + pid[:-1] + '.' + suffix
                if not os.path.isdir(path):
                    os.makedirs(path)
                    
                self.id_count += 1
                print '******************************************'
                print str(self.id_count) + ': ' + pt
                self.output_file.write(str(self.id_count) + ',' + filename + ',' + pt + ',' + img_url + '\n')
                print '******************************************\n'
                if self.id_count >= 200:
                    break
            except Exception, e:
                pass

        return

def downjpg(url, filename):
    try:
        urllib.urlretrieve(url, filename)
    except Exception, e:
        pass
