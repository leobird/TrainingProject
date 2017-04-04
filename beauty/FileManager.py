#!/usr/bin/python
# coding=utf-8

class FileManager:
    def __init__(self):
        pass

    @classmethod
    def writeToFile(cls,filename, fileContent):
        fp = file('result/' + filename + '.txt', 'a')
        fp.write(fileContent + '\n')
        fp.close()
