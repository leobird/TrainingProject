#!/usr/bin/python
# coding=utf-8

import os
import re
import urllib

import shutil
from bs4 import BeautifulSoup
from urlparse import urlsplit
from FileManager import FileManager

class BeautyPicsManager:

    def __init__(self):
        try:
            shutil.rmtree('resultImg')
        except:
            pass
        os.mkdir('resultImg')

    def getBeautyPic(self,url):
          content = urllib.urlopen(url)
          bs = BeautifulSoup(content, 'lxml')
          urlsResultSet=bs.find_all('a', {"target": "_blank"})
          for beautyUrlResultSet in urlsResultSet:
              beautyUrl=beautyUrlResultSet['href']
              beautyUrlParts=beautyUrl.split('/')
              urlParts = urlsplit(url)
              domainUrl = urlParts[0] + '://' + urlParts[1]
              catchUrl=domainUrl+'/'+beautyUrlParts[1]+'/'+beautyUrlParts[2]+'.htm'
              try:
                  self.catchPics(catchUrl)
              except Exception,e:
                  FileManager.writeToFile('ErrorPhotoUrl',catchUrl+'    ErrorInfo=[' + str(e) + ']')
                  print catchUrl+'are abnormal'

    def checkPicsUrl(self,url):
          urlMatchResult=re.match(r'^((https|http|ftp|rtsp|mms)?:\/\/)[^\s]+\/[^\s]+\/[^\s]+\.htm',url)
          if (urlMatchResult != None):return True
          else:return False

    def catchPics(self,html):
          bs = BeautifulSoup(html, 'lxml')
          photoNum=0
          for picsboxContent in bs.find_all('div', {"class": "picsbox"})[0]:
              imgSrc=picsboxContent.contents[0]['src']
              photoNum+=1
              self.downloadPic(imgSrc, photoNum)
              FileManager.writeToFile('PhotoSrc',imgSrc)

    def downloadPic(self,url,photoNum):
          image_content = urllib.urlopen(url).read()
          beautyNum = os.path.basename(urlsplit(url)[2]).split('-')[0]
          file_name = beautyNum+'-'+str(photoNum)+'.jpg'
          output = open("resultImg/"+file_name, 'wb')
          output.write(image_content)
          output.close()
