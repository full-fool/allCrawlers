#encoding=utf-8
import re
def getListFromFile(fileName):
    resultList = []
    for line in open(fileName):
        resultList.append((line.split(',')[0], line.split(',')[1]))
    return resultList

faceCountPerFolderList = getListFromFile('FaceCountPerFolder.txt')
facePercentageList = getListFromFile('FacePercentageForFolder.txt')
#print len(faceCountPerFolderList)
#print len(facePercentageList)
resultList = []
for i in range(20):
    while 1:
        tempFolder = faceCountPerFolderList[0]
        faceCountPerFolderList.remove(tempFolder)
        folderName = tempFolder[0]
        for eachFolder in facePercentageList:
            if folderName == eachFolder[0]:
                number = eachFolder[1].strip('\n')
                number = number.strip('\r')
                if float(str(number)) >= 1.8:
                    resultList.append((folderName, tempFolder[1], eachFolder[1]))
                break
        break

filehandler = open('result_folder.txt', 'w')
for item in resultList:
    filehandler.write(item[0]+'\n')
filehandler.close()

