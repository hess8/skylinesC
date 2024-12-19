'''Calls landscapes.py and createTorrents.py'''

# Run with cpulimit -l 90 python3 production/utilities/updateZipped.py

#loop
# 1. checks links and folder size
# 2. creates new zips for folders that are static
# 3. creates new links
# 4. runs createTorrents.py
# 5. runs landscapesPage.py
# 6. can confirm that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
# link target eg C:\Users\Bret\AppData\Local\qBittorrent\logs\qbittorrent.log
#   sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.
#
# Add "-" to the beginning of the landscape dir name to remove all but .ini files and move to lowVini
# xxx-legacy (kept in code, needs updating). Add "." to the beginning of the landscape dir name to move landscape to symlink directory,

# landscapes.py writes the new page locally so we need to make this symbolic link on the skylinesC server:

import os,sys
# import py7zr #py7zr does not follow symlinks!
# import win32com.client

# from subprocess import Popen, PIPE
# print(os.path.abspath(os.curdir))
from time import sleep
from common_util import readfileNoStrip, readfile
from uzsubs import *
from createTorrents import createTorrents
from datetime import datetime
from landscapesPage import landscapesPage
import signal

landSizes = {}
looping = True
loopWaitTime = 0 # min when idle before checking agin
## zipping ##
lowVMain = '/mnt/E/landscapes/landscapesC2-main'
lowVExt1 = None #'/mnt/E/landscapes/landscapesC2-main'
lowVini = '/mnt/E/landscapes/landscapesC2-ini'
lowVserver = '/mnt/E/landscapes/landscapesC2-server'
highVMain = '/mnt/E/landscapes/landscapesC3-main'
highVExt1 = None #'/mnt/E/landscapes/landscapesC3-main'
highVini = '/mnt/E/landscapes/landscapesC3-ini'
highVserver = '/mnt/E/landscapes/landscapesC3-server'
lowerVersionLandDirs = [lowVMain,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = '/mnt/P/landscapes-zip'
zipExtras = None #['/mnt/E/landscapes/zipped1']
zipDirs = [zipMain] #+ zipExtras
zipPathPrior = [zipMain] # [zipExtras[0],zipMain] # fill up in this order
utilitiesDir = '/mnt/L/condor-related/skylinesC/production/utilities'
## Landscapes page ##
forceLandPage = False
landPageDest = os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs')
qbtorrentExeDir = os.path.join(zipMain,'qbt_exe')
slcFilesPath = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/' #only used if can get copying by guest control working again
qbtExeLocal = get_qbtExe(qbtorrentExeDir,slcFilesPath)
qbtExePath = get_qbtExe(qbtorrentExeDir,slcFilesPath)
landHBS = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
slcVMname = 'U14 (SkylinesC server on Z) Current'
# landHBS = '/home/bret/servers/repo-skylinesC/landscapes.test.hbs'
## Torrents ##

trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = os.path.join(zipMain + '/qbtWatch')
makeAllMagnets = False  # needed only occasionally

########

if not os.path.exists(watchDir):
    os.mkdir(watchDir)

#remove broken symbolic links and flag landscapes without .ini file or .ini name not matching landscape
checkLinksIni(lowVMain)
checkLinksIni(highVMain)
checkZipsLinks(zipMain)
lowVList = os.listdir(lowVMain)
highVList = os.listdir(highVMain)

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


for zipDir in zipPathPrior:
    itemslist = os.listdir(zipDir)
    for item in itemslist:
        file_name, extension = os.path.splitext(item)
        if extension == '.temp':
            os.remove(os.path.join(zipDir,item))
print('Write code for:   Start the landscape dir name with "-" to move landscape to ini only directory')
print('Write code for:   Start the landscape dir name with "." to move landscape to other landscapes folder')
go = True
while go:
    #if dir in main dirs begins with "-", remove all but .ini files and move to ini dirs
    # rewrite this!!!!!!!!!!!!!!!!!!!!!!!!!!!
    for list in [lowVList,highVList]:
        for item in list:
            if list == lowVList: mainPath = lowVMain; ini = lowVini
            elif list == highVList: mainPath = highVMain; ini = highVini
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
    createdTorr = []

    def dirSize(path):
        result = subprocess.run(["du", "-s", path], stdout=subprocess.PIPE, text=True)
        strOut = result.stdout
        size = strOut.split('\t')[0]
        print(size)

    def checkGrowthWait(landPath):
        sizeNew = dirSize(landPath)
        if landPath in landSizes:
            sizeStored = landSizes[landPath]
            landSizes[landPath] = sizeNew
            if sizeNew > sizeStored:
                return True
            else:
                return False
        else:
            landSizes[landPath] = sizeNew
            print()
            return True #wait til next loop to check

    for i, landPath, in enumerate(allLandPaths):
        if 'CA' in landPath:
            xx=0
        if os.path.basename(landPath)[0] == '!' or checkGrowthWait(landPath):
            continue
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
            toZip.append({'zipName': zipName, 'landPath': landPath})

    if len(toZip) > 0:
        print("Will create these zips:")
        for name in toZip:
            print(name)
        # create new zips
        newZipped = []
        for newZip in toZip:
            landPath2 = newZip['landPath']
            if 'C3' in landPath2:
                mainDir = highVMain
            else:
                mainDir = lowVMain

            destination = zipDestDriveByPriority(zipPathPrior, landPath2)
            zipPath = os.path.join(destination, newZip['zipName'])  # no zips will have spaces, but landscapes folders might
            zipPathTemp = os.path.join(zipPath + '.temp')

            count = 0
            print()
            print('----------------------------------------------------------')
            print('***Creating {} in {}***'.format(newZip['zipName'], destination))

            if os.path.exists(zipPathTemp):
                os.remove(zipPathTemp)
            sevenzip(zipPathTemp, landPath2)
            renameTry(zipPathTemp, zipPath)
            # except:
            #     print('Error creating {}'.format(zipPath))
        updateSymlinks([zipDirs])
    createdTorr = createTorrents(zipMain,watchDir,makeAllMagnets)

    if forceLandPage or len(createdTorr) > 0 or not os.path.exists(landPageDest):
        landscapesPage(zipDir,landPageDest,landHBS,qbtExeLocal,slcFilesPath,slcVMname,trackerStr)

    if looping:
        for i in range(int(loopWaitTime)):
            print("\r", end='')
            print('Waiting {} min'.format(loopWaitTime - i), flush=True, end='')
            sleep(60)
        print("\r", end='')
    else:
        go = False



print ("Done")
#check that new torrents have been added to the qbittorrent servers
    # time.sleep(5)
    # shell = win32com.client.Dispatch("WScript.Shell")
    # for logfile in qbtLogLinks:
    #     shortcut = shell.CreateShortCut('{}/{}'.format(zipMain,logfile))
    #     lines = readfile(shortcut.Targetpath)
    #     for zipped in newZip['zipName']ped:
    #         for line in lines:
    #             if 'added to download list' in line and zipped in line:
    #                 print('New torrent {} found in {}').format(zipped,logfile)
    #                 break
    #         else:
    #             print('Error. {} not found in {}').format(zipped,logfile)
    # time.sleep(5)
