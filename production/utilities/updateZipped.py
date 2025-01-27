'''Calls landscapes.py and createTorrents.py'''

# Not used...use threads limits...Run with cpulimit -l 90 python3 production/utilities/updateZipped.py

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
import platform
from common import dirSize, readfileNoStrip, readfile, renameTry
from uzsubs import *
from common import landscapesMap
from time import perf_counter
import argparse
parser = argparse.ArgumentParser(description="Description of your script")
parser.add_argument("-r", "--reverse", help="Goes through landscapes and zip lists in reverse order", action="store_true")
args = parser.parse_args()
reverse = False

looping = True
loopWaitTime = 5 # min when idle before checking agin (can be changed by checkGrowth)
nThreads = {'linux': 1, 'windows': 12}

versions = ['C2','C3']
versionUpdateTag = '_to_{}'.format(versions[1])
## zipping ##
linuxPathStart = '/mnt/'
winPathStart = 'S:\\' #includes Samba windows mapped drive
if platform.system() == 'Windows':
    print("Running on Windows...no work on links, torrents or page")
    pathStart = winPathStart
    linux = False
else:
    pathStart = linuxPathStart
    linux = True
lowVMain = os.path.join(pathStart,'E','landscapes','landscapesC2-main')
lowVExt1 = None #os.path.join(pathStart,'E','landscapes','landscapesC2-main')
lowVini = os.path.join(pathStart,'E','landscapes','landscapesC2-ini')
lowVserver = os.path.join(pathStart,'E','landscapes','landscapesC2-server')
highVMain = os.path.join(pathStart,'E','landscapes','landscapesC3-main')
highVExt1 = None #os.path.join(pathStart,'E','landscapes','landscapesC3-main')
highVini = os.path.join(pathStart,'E','landscapes','landscapesC3-ini')
highVserver = os.path.join(pathStart,'E','landscapes','landscapesC3-server')
lowerVersionLandDirs = [lowVMain,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = os.path.join(pathStart,'P','landscapes-zip')
zipExtras = None #[os.path.join(pathStart,'E','landscapes','zipped1']
zipDirs = [zipMain] #+ zipExtras
zipPathPrior = [zipMain] # [zipExtras[0],zipMain] # fill up in this order
utilitiesDir = os.path.join(pathStart,'L','condor-related','skylinesC','production','utilities')
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
print('Starting')
startTime = perf_counter()
if not os.path.exists(watchDir):
    os.mkdir(watchDir)

# #remove broken symbolic links and flag landscapes without .ini file or .ini name not matching landscape
# if linux:
#     checkLinksIni(lowVMain, versionUpdateTag)
#     checkLinksIni(highVMain, versionUpdateTag)
#     checkZipsLinks(zipMain)
lowVList = os.listdir(lowVMain)
highVList = os.listdir(highVMain)

landSizes = {}
allLands, allLandPaths = getLandPaths(lowVMain, highVMain,versionUpdateTag)

#temp
print('extracting zips of lands not updated')
# destination = 'A:\\landscapes'
for dir in zipDirs:
    dirList = sorted(os.listdir(dir))
    if args.reverse:
        dirList = sorted(os.listdir(dir), reverse=True)
    for item in dirList:
        match = re.search(r'(.*)\.v.*\.7z$',item)
        if not match or '_C3' in item or 'WestGermany3' in item:
            continue
        name_underscores = match.group(1)
        archive = os.path.join(dir,item)
        response = sevenName(archive)
        if 'is not an archive' in response.lower():
            print("Archive {} is corrupted: deleting it".format(item))
            os.remove(archive)
            continue
        else:
            trueLandName = response
        convertedFilesPath = os.path.join(lowVMain,name_underscores + '_to_C3')
        destination = os.path.join('A:\\landscapes',trueLandName)
        if os.path.exists(convertedFilesPath) or os.path.exists(destination) or trueLandName in landscapesMap:
            continue
        print('Extracting {} to {}'.format(archive,destination))
        output = sevenzip("extraction", archive, destination, nThreads)
        if "Can't open as archive" in output:
            print("Archive {} can't be extracted because it is corrupted: deleting it".format(item))
            os.remove(archive)

sys.exit('Stop')
#remove unwanted folders
# for i, landPath, in enumerate(allLandPaths):
#     if highVMain in landPath:
#         if os.path.islink(landPath):
#             os.unlink(landPath)


# # rename some folders
# for landPath in allLandPaths:
#     # badTags = ['_C2toC3_C2toC3','_toC3_toC3','_toC3',]
#     badTags = [' ']
#     if lowVMain in landPath:
#         for tag in badTags:
#             if tag in landPath:
#                 newName = landPath.replace(tag,'_')
#                 renameTry(landPath, newName)
#                 break

# for landPath in allLandPaths:
#     if versionUpdateTag in landPath and 'Airports' in os.listdir(landPath):
#         airportsDir = os.path.join(landPath,'Airports')
#         nAirports = len(os.listdir(airportsDir))
#         print('Airports',nAirports,landPath)

        # landBase,name = os.path.split(landPath)
        # badDir = os.path.join(landBase,name + versionUpdateTag)
        # if os.path.exists(badDir):
        #     newName = badDir.replace(versionUpdateTag,versionUpdateTag.replace('_C2toC3','_to_C3'))
        #     renameTry(badDir,newName)
####

# Copy files from high version update
for i, landPath, in enumerate(allLandPaths):
    if lowVMain in landPath:
        if versionUpdateTag in landPath: #create a link in the higher version folder
            base,name = os.path.split(landPath)
            linkSource = landPath.replace(versionUpdateTag,'') # the full landscape folder
            linkDest = os.path.join(highVMain,name.replace(versionUpdateTag,''))
            if not os.path.islink(linkDest):
                if platform.system() == 'Linux':
                    os.symlink(linkSource,linkDest)
            continue
        landBase,name = os.path.split(landPath)
        highVFilesDir = os.path.join(landBase, name + versionUpdateTag).replace(' ', '_')
        if os.path.exists(highVFilesDir):
            continue
        highVFiles = lowVtoHighVFiles(landPath)
        if not highVFiles:
            continue
        else:
            print(versionUpdateTag, highVFiles)
            os.mkdir(highVFilesDir)
            for newFileExistingPath in highVFiles:
                # newBase, newName = os.path.split(newFileExistingPath)
                newFileSavePath = newFileExistingPath.replace(landPath,highVFilesDir)
                dirsInPath = newFileSavePath.split(highVFilesDir)[1].split(os.sep)[:-1]
                if len(dirsInPath) > 0: #create dir structure needed for file
                    nextDirPath = highVFilesDir
                    for dir in dirsInPath:
                        nextDirPath = os.path.join(nextDirPath,dir)
                        if not os.path.exists(nextDirPath):
                            os.mkdir(nextDirPath)
                shutil.copy2(newFileExistingPath, newFileSavePath)

print('Write code for:   Start the landscape dir name with "-" to move landscape to ini only directory')
print('Write code for:   Start the landscape dir name with "." to move landscape to other landscapes folder')
go = True
loopCount = 0
while go:
    loopCount += 1

    # '.' and '-' tags
    # for list in [lowVList,highVList]:
    #     for item in list:
    #         if list == lowVList: mainPath = lowVMain; ini = lowVini
    #         elif list == highVList: mainPath = highVMain; ini = highVini
    #         if item[0] == '-':
    #             print("handling '-' files needs to be rewritten")
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

    allZips = []
    #remove broken symbolic links and flag landscapes without .ini file or .ini name not matching landscape
    if linux:
        checkLinksIni(lowVMain,versionUpdateTag)
        checkLinksIni(highVMain,versionUpdateTag)
        checkZipsLinks(zipMain)
        #### update symbolic links to landscape folders

        updateSymlinks(landVersionsLists)
        ## now all landscapes are represented in main folders ##

    allLands, allLandPaths = getLandPaths(lowVMain,highVMain,versionUpdateTag)

    #### update symbolic links to zip files
    if linux: updateSymlinks([zipDirs])
    # get all zip paths from zipMain
    items = os.listdir(zipMain)
    for item in items:
        if item.split('.')[-1] == '7z':
            allZips.append(item)
    all
    ## now all zips are represented in zipMain ##

    # list dirs to be zipped
    toTestGrowth = []
    toZip = []
    createdTorr = []
    #get low version list to avoid making zips of C2 folders linked to C3
    lowVLands = []
    for i, landPath, in enumerate(allLandPaths):
        land = allLands[i]
        if lowVMain in landPath:
            lowVLands.append(land)

    for i, landPath, in enumerate(allLandPaths):
        land = allLands[i]
        if 'Alps' in land:
            xx=0
        if os.path.basename(landPath)[0] == '!' or (highVMain in landPath and land in lowVLands):
            continue                      # no zips of C2 folders linked to C3
        if versionUpdateTag in landPath:
            base,name = os.path.split(landPath)
            zipName = name.replace(' ', '_') + '.7z'
            if zipName not in allZips:
                toZip.append({'zipName': zipName, 'landPath': landPath})
            continue
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
            if checkGrowth(landPath, landSizes):
                print('Will check {} for growth'.format(os.path.basename(landPath)))
                toTestGrowth.append({'zipName': zipName, 'landPath': landPath})
            else:
                toZip.append({'zipName': zipName, 'landPath': landPath})
        # add C2_C3 folder


    #this code works, but may be too short to check for growth, so for now let loop time determine it
    # if len(toTestGrowth) > 0:
    #     print('Waiting 30sec to check for growth')
    #     sleep(60)
    #     for landDict in toTestGrowth:
    #         if not checkGrowth(landDict['landPath'], landSizes):
    #             toZip.append(landDict)
    #         else:
    #             print('{} is still growing'.format(landDict['landPath']))

    if len(toZip) > 0:
        print("Will create these zips:")
        for land in toZip:
            print(land['landPath'])
        # create new zips
        newZipped = []
        for newZip in toZip:
            # print('skipping zipping')
            # continue
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
            output = sevenzip("compression", zipPathTemp, landPath2, nThreads)

            # except:
            #     print('Error creating {}'.format(zipPath))
    if linux:
        updateSymlinks([zipDirs])
        createdTorr = createTrrents(zipMain,watchDir,makeAllMagnets)
        if (forceLandPage or len(createdTorr) > 0 or not os.path.exists(landPageDest)):
            landscapesPage(zipMain,landPageDest,landHBS,qbtExeLocal,slcFilesPath,slcVMname,trackerStr)

    if looping:
        waitTimeMins = int(max(0,loopWaitTime - (perf_counter() - startTime)/60)) #minutes
        for i in range(waitTimeMins):
            print("\r", end='')
            print('[loop {}]  Waiting {} min '.format(loopCount, waitTimeMins - i), flush=True, end='')
            sleep(60)
        print("\r", end='')
print('Done')
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
