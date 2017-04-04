# coding:utf-8
import os
import re
import urllib2
import time
import Queue
import thread
import urlparse
import chardet
import shutil
from bs4 import BeautifulSoup
from FileManager import FileManager
from BeautyPicsManager import  BeautyPicsManager


class UrlManager:
    urlList = []
    urlQueue = Queue.Queue()
    domainUrl = ''
    sourceUrl = ''
    # 1:running 0:waiting -1:ending
    threadStatus = [1, 0, 0, 0, 0, 0, 0, 0, 0]

    def __init__(self, sourceUrl):
        try:
            shutil.rmtree('result')
        except:
            pass
        os.mkdir('result')
        self.sourceUrl = sourceUrl
        urlParts = urlparse.urlsplit(sourceUrl)
        self.domainUrl = urlParts[0] + '://' + urlParts[1]
        self.urlQueue.put(self.sourceUrl)

    def getPageUrl(self, html):
        bs = BeautifulSoup(html, 'lxml')
        urlsResultSet = bs.find_all('a')
        for urlResultSet in urlsResultSet:
            try:
                url = urlResultSet['href']
            except:
                continue
            if (self.urlList.count(url) > 0):
                continue
            self.urlList.append(url)
            urlMatchResult = re.match(r'^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+', url)
            if (urlMatchResult != None):
                self.urlQueue.put(url)
                continue
            urlMatchResult = re.match(r'^(\/\/)[^\s]+', url)
            if (urlMatchResult != None):
                url = self.domainUrl.split('//')[0] + url
                if (self.urlCheck(url)):
                    self.urlQueue.put(url)
                continue
            urlMatchResult = re.match(r'^(\/)[^\s]*', url)
            if (urlMatchResult != None):
                url = self.domainUrl + url
                if (self.urlCheck(url)):
                    self.urlQueue.put(url)
                continue

    def urlCheck(self, url):
        if (self.urlList.count(url) == 0):
            self.urlList.append(url)
            return True
        else:
            return False

    def getContents(self, url):
        try:
            url = urllib2.quote(url.split('#')[0].encode('utf-8'), safe="%/:=&?~#+!$,;'@()*[]")
            req = urllib2.urlopen(url)
            res = req.read()
            code = chardet.detect(res)['encoding']
            # print
            # print code
            res = res.decode(str(code), 'ignore')
            res = res.encode('gb2312', 'ignore')
            FileManager.writeToFile('AccessUrl', url)
            return res
        except urllib2.HTTPError, e:
            FileManager.writeToFile('ErrorUrl', url+ '    HTTPErrorInfo=[' + str(e) + ']')
            return None
        except urllib2.URLError, e:
            FileManager.writeToFile('ErrorUrl', url+ '    URLErrorInfo=[' + str(e) + ']')
            return None
        except Exception, e:
            FileManager.writeToFile('ErrorUrl', url+ '    ErrorInfo=[' + str(e) + ']')
            return None

    def do(self, threadNo,beautyPicsManager):
        while max(self.threadStatus) == 1:
            if self.urlQueue.empty() == False:
                url = self.urlQueue.get()
                html = self.getContents(url)
                if (html != None):
                    self.getPageUrl(html)
                    try:
                        if(beautyPicsManager.checkPicsUrl(url)):
                            beautyPicsManager.catchPics(html)
                    except Exception,e:
                        FileManager.writeToFile('ErrorUrl', url+ '    PictureErrorInfo=[' + str(e) + ']')
                print 'Thread ' + str(threadNo) + ' is running.Running Url :' + url + '\n'
                self.threadStatus[threadNo - 1] = 1
            else:
                print 'Thread ' + str(threadNo) + ' is waiting.\n'
                self.threadStatus[threadNo - 1] = 0
                time.sleep(1)
        self.threadStatus[threadNo - 1] = -1

    def start(self):
        try:
            pics=BeautyPicsManager()
            for i in range(1, 10):
                thread.start_new_thread(self.do, (i,pics))
            while True:
                if max(self.threadStatus) == -1:
                    break
        except Exception, e:
            print "Error: unable to start thread.Exception:" + str(e)


if __name__ == '__main__':
    urlIssue = UrlManager('https://www.4493.com/star/zfyh/')
    urlIssue.start()
