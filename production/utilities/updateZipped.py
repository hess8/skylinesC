# '''

# RUN AS ADMIN
# 1. run on either machine (anaconda "conda activate bchenv") as ADMIN
# 2. conda activate bch39
# 3. !!!!Add to windows path:  "C:\Program Files\7-Zip!!!!"
# 4. confirmation that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
# link target eg C:\Users\Bret\AppData\Local\qBittorrent\logs\qbittorrent.log
#   sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.
#
# Add "-" to the beginning of the landscape dir name to remove all but .ini files and move to lowVini
# xxx-legacy (kept in code commented out). Add "." to the beginning of the landscape dir name to move landscape to symlink directory,

# ssh access: make sure port 22 is open on U14.  Test ssh connection manually
# '''

import os,sys
# import py7zr #py7zr does not follow symlinks!  So we use C:\Program Files\7-Zip.  See note above
# import win32com.client

# from subprocess import Popen, PIPE
# print(os.path.abspath(os.curdir))
sys.path.append('L:\\condor-related\\skylinesC\\skylines')
from time import sleep
from common import readfileNoStrip, readfile
from uzsubs import *

debugMode = False
if debugMode: #use for pycharm debugging. Can't get paramiko to load in pycharm
    print("\n\nIn **debug mode**...won't run createTorrents on server\n\n")
    sleep(2)
lowVMain = 'P:\\landscapes\\landscapesC2-main'
lowVExt1 = 'L:\\condor-related\\C2LandExt1'
lowVini = 'P:\\landscapes\\landscapesC2-ini'
lowVserver = 'P:\\landscapes\\landscapesC2-server'
highVMain = 'P:\\landscapes\\landscapesC3-main'
highVExt1 = 'L:\\condor-related\\C3LandExt1'
highVini = 'P:\\landscapes\\landscapesC3-ini'
highVserver = 'P:\\landscapes\\landscapesC3-server'
lowerVersionLandDirs = [lowVMain,lowVExt1,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVExt1,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = 'P:\\landscapes\\landscapes-zip'
zipExtras = ['R:\\zipped1']
zipDirs = [zipMain] + zipExtras
zipPathPrior = [zipExtras[0],zipMain] # fill up in this order



#remove broken symbolic links and flag landscapes without .ini file or .ini name not matching landscape
checkLinksIni(lowVMain)
checkLinksIni(highVMain)
checkZipsLinks(zipMain)
lowVListA = os.listdir(lowVMain)
highVListA = os.listdir(highVMain)

# #temp
# print(' removing files without tag')
# for dir in zipDirs:
#     list = os.listdir(dir)
#     for item in list:
#         if '.7z' in item and '_C2.7z' not in item and 'C3' not in item:
#             # renameTry(os.path.join(dir,item), os.path.join(dir,item.replace('.7z','_C2.7z' )))
#             os.remove(os.path.join(dir,item))

# print('adding _C2 back to zip files')
# for dir in zipDirs:
#     list = os.listdir(dir)
#     for item in list:
#         if item.split('.')[-1] == '7z' in item and '_C2.7z' not in item and 'C3' not in item\
#           and not os.path.exists(os.path.join(dir,item.replace('.7z','_C2.7z' ))):
#             renameTry(os.path.join(dir,item), os.path.join(dir,item.replace('.7z','_C2.7z' )))

#temp add C2 back to some names
#
# list = os.listdir(lowVMain)
# tochange = ['Belgium','Atlantide','','','','','',]
# for land in list:
#     landbase = land.replace('_C2','')
#     if landbase not in tochange:
#         continue
#     dirlist = os.listdir(os.path.join(lowVMain,land))
#     newland = land + '_C2'
#     renameTry(os.path.join(lowVMain,land),os.path.join(lowVMain!_newland))
#     for item in dirlist:
#         if land in item:
#             renameTry(os.path.join(lowVMain!_newland, item), os.path.join(lowVMain!_newland, item + '_C2'))
#         if '_C2' in item:
#             newname = item.replace('_C2','')
#             name2 = newname.replace(landbase,landbase+'_C2')
#             renameTry(os.path.join(lowVMain,land,item),os.path.join(lowVMain,land!_name2))


#if dir in main dirs begins with "-", remove all but .ini files and move to ini dirs
print('Start the landscape dir name with "-" to move landscape to ini only directory')
#print('To move landscape to sym link directory, start the landscape dir name with "."')
for list in [lowVListA,highVListA]:
    for item in list:
        if list == lowVListA: mainPath = lowVMain; ini = lowVini
        elif list == highVListA: mainPath = highVMain; ini = highVini
        if item[0] == '-':
            print("handling '-' files needs to be rewritten")
            # path = os.path.join(mainPath,item)
            # for item2 in os.listdir(mainPath):
            #     if not '.ini' in item2:
            #         if os.path.isdir(os.path.join(mainPath,item2)): # note: isdir is true for a link pointing to a dir
            #             os.system('rmdir /S /Q "{}"'.format(os.path.join(mainPath,item2)))
            #         else:
            #             os.remove(os.path.join(mainPath,item2))
            # shutil.move(path,os.path.join(ini,item.replace('-','')))
            # print('Moved {} to {}'.format(path,ini))

        #######
        # elif item[0] == '.':  #legacy to move to symlinks dir...keep in code
        #     path = os.path.join(lowVMain,item)
        #     print('Moving {} to {}'.format(path,symLinksDir))
        #     shutil.move(path,os.path.join(symLinksDir,item.replace('.','')))
        #     print('Moved {} to {}'.format(path,symLinksDir))

#remove extra files from ini-only dirs:
for dir1 in [lowVini,highVini]:
    for landscape in os.listdir(dir1):
        notifiedRemove = False
        for item in os.listdir(os.path.join(dir1,landscape)):
            if not '.ini' in item:
                if not notifiedRemove:
                    print ('Removing all but .ini in {}'.format(landscape))
                    notifiedRemove = True
                if os.path.isdir(os.path.join(dir1,landscape,item)): # note: isdir is true for a link pointing to a dir
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir1,landscape,item)))
                else:
                    os.remove(os.path.join(dir1,landscape,item))

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []
allZipPaths = []
#remove broken symbolic links and flag landscapes without .ini file or .ini name not matching landscape
checkLinksIni(lowVMain)
checkLinksIni(highVMain)
checkZipsLinks(zipMain)
#### update symbolic links to landscape folders

updateSymlinks(landVersionsLists)
## now all landscapes are represented in main folders ##

# get all landscape paths that have textures dir
for dir in [lowVMain,highVMain]:
    items = os.listdir(dir)
    for item in items:
        itemPath = os.path.join(dir, item)
        if os.path.isdir(itemPath) and \
            'Textures' in os.listdir(itemPath) \
            and 'WestGermany3' not in item: # note: isdir is true for a link pointing to a dir
                allLands.append(item)
                allLandPaths.append(os.path.join(dir, item))

#### update symbolic links to zip files
updateSymlinks([zipDirs])
# get all zip paths from zipMain
items = os.listdir(zipMain)
for item in items:
    if item.split('.')[-1] == '7z':
        allZips.append(item)
        allZipPaths.append(os.path.join(zipMain, item))
## now all zips are represented in zipMain ##

# list dirs to be zipped
toZip = []
for i, landPath, in enumerate(allLandPaths):
    if os.path.basename(landPath)[0] == '!':
        break
    land = allLands[i]
    files = os.listdir(landPath)
    iniFilePath = os.path.join(landPath,land+'.ini')
    lines = readfile(iniFilePath)
    if len(lines) > 1:
        version = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
    else:
        print('len lines',len(lines))
        print ('lines', lines)
        sys.exit("Stop: .ini file can't be parsed {}".format(iniFilePath))
    condorVers = versionFromPath(landPath)
    zipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),version,condorVers) #no zips will have spaces, but landscapes folders might
    if zipName not in allZips:
        toZip.append(zipName)
if len(toZip) > 0:
    print("Will create these zips:")
    for name in toZip:
        print(name)

#create new zips
newZipped = []
for newZip in toZip:
    if 'C3' in newZip:
        mainDir = highVMain
    else:
        mainDir = lowVMain
    land2 = newZip.split('.')[0]
    landPath2 = os.path.join(mainDir, land2)
    destination = zipDestDriveByPriority(zipPathPrior,landPath2)
    zipPath = os.path.join(destination, newZip)  # no zips will have spaces, but landscapes folders might
    zipPathTemp = os.path.join(zipPath + '.temp')

    count = 0
    print()
    print('----------------------------------------------------------')
    print('***Creating {} in {}***'.format(newZip, destination))

    try:
        #create new zip
        sevenzip(zipPathTemp,landPath2)
        newZipped.append(zipPath)
        renameTry(zipPathTemp,zipPath)
    except:
        print ('Error creating {}'.format(zipPath))

if len(newZipped) == 0:
    print ('!_no new landscapes to zip')
else:
    updateSymlinks([zipDirs])
# time.sleep(60)

# run createTorrents on skylinesC server
if not debugMode:
    runCreateTorrents(newZipped)

print ("Done")
#check that new torrents have been added to the qbittorrent servers
    # time.sleep(5)
    # shell = win32com.client.Dispatch("WScript.Shell")
    # for logfile in qbtLogLinks:
    #     shortcut = shell.CreateShortCut('{}\\{}'.format(zipMain,logfile))
    #     lines = readfile(shortcut.Targetpath)
    #     for zipped in newZipped:
    #         for line in lines:
    #             if 'added to download list' in line and zipped in line:
    #                 print('New torrent {} found in {}').format(zipped,logfile)
    #                 break
    #         else:
    #             print('Error. {} not found in {}').format(zipped,logfile)
    # time.sleep(5)
