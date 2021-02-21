# '''run in windows cmd window (no admin needed)
#         SET PATH=%PATH%;"C:\Program Files\7-Zip"
#         python d:\skylinesC\production\utilities\updateZipped.py
#
#         '''

import os,sys,time
import py7zr
import shutil

def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def sevenzip(tempPath,landPath):
    os.system('7z a -t7z "{}" "{}"'.format(tempPath,landPath)) #quotes to handle spaces in windows file names
#     with py7zr.SevenZipFile(tempPath, 'w') as archive:
#                     archive.writeall(landPath, 'base')  #This seems slow, but uses threads well

mainDir = 'Z:\\Condor\\Landscapes'
otherDir1 = 'E:\\landscapes_for_symlinks'  #py7zr does not follow symlinks
otherDir2 = 'F:\\landscapes_for_symlinks2'
iniOnlyDir1 = 'E:\\landscapes_ini_only'
iniOnlyDir2 = 'F:\\landscapes_ini_only2'
zipDir = 'S:\\Skylines-C\landscapes-zip'

#remove extra files from ini_only dirs:
for dir in [iniOnlyDir1,iniOnlyDir2]:
    for landscape in os.listdir(dir):
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                print ('Removing all but .ini in {}'.format(landscape))
                break
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:   
                if os.path.isdir(os.path.join(dir,landscape,item)):
#                     shutil.rmtree(os.path.join(dir,landscape,item))
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir,landscape,item)))
                else:
                    os.remove(os.path.join(dir,landscape,item))

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []

#update symbolic links
mainList = os.listdir(mainDir)
otherList1 = os.listdir(otherDir1)
otherList2 = os.listdir(otherDir2)

for dir in [otherDir1, otherDir2,iniOnlyDir1,iniOnlyDir2]:
    for item in os.listdir(dir) :
        if item not in mainList:
            print ('Updated symlink for {}.'.format(item))
            mainPath = '{}\\{}'.format(mainDir,item)
            otherPath = '{}\\{}'.format(dir,item)
            os.system('mklink /D "{}" "{}"'.format(mainPath,otherPath))

#landscapes are all represented in mainDir now.
for item in os.listdir(mainDir):
    if 'WestGermany3' not in item:
        allLands.append(item)
        allLandPaths.append('{}\\{}'.format(mainDir,item))

#zips
for item in os.listdir(zipDir):
    if item.split('.')[-1] =='7z':
        allZips.append('{}\{}'.format(zipDir,item))

#remove old temp zip files
for item in os.listdir(mainDir):
    if 'temp' in item:
        tempPath = mainDir+'\\{}'.format(item)
        os.remove(tempPath)

#remove extra files, dirs from ini_only landscapes


#create zips
count = 0
for i, landPath, in enumerate(allLandPaths):
    land = allLands[i]
#     print (land)
    iniPath = os.path.join(landPath,'{}.ini'.format(land))
    if os.path.exists(iniPath):
        lines = readfile(iniPath)
        if len(lines) > 1:
            version = lines[1].split('=')[1].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
            print ('lines', lines)
            sys.exit('Stop1: version line does not exist')
        zipName = '{}.v{}.7z'.format(land.replace(' ','_'),version) #no zips will have spaces, but landscapes folders might
        zipPath = '{}\\{}'.format(zipDir,zipName) #no zips will have spaces, but landscapes folders might
        if zipPath not in allZips:
            print()
            print('----------------------------------------------------------')
            print(zipPath,)
            try:
                #create new zip
                landZip = zipPath.split('.')[0].split('\\')[-1]
                tempPathZip = mainDir+'\\temp_{}.7z'.format(landZip)
                print ('***Creating {}***'.format(zipName))
                sevenzip(tempPathZip,landPath)
                print('Moving to zip directory')
                shutil.move(tempPathZip,zipPath)
                count += 1
            except:
                print ('Error creating {}'.format(zipPath))
    else:
        print ('lines', lines)
        sys.exit('Stop2: version line does not exist for {}'.format(landPath))
if count>0:
    print ('Moved {} zip files to {}'.format(count, zipDir))
else:
    print ('No new landscapes to zip'.format(count, zipDir))
# time.sleep(60)

print ("Done")


