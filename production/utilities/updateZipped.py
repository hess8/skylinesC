"""
    Calls landscapes.py and createTorrents.py if on Linux

    loop
    1. checks links and folder size
    2. creates new zips for folders that are static
    3. creates new links
    4. runs createTorrents.py
    5. runs landscapesPage.py
    6. can confirm (not enabled) that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
    link target eg C:\\Users\\Bret\\AppData\\Local\\qBittorrent\\logs\\qbittorrent.log

      sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.

    Add "-" to the beginning of the landscape dir name to remove all but .ini files and move to lowVini
    Add "." to the beginning of the landscape dir name to move landscape to symlink directory,

    landscapes.py writes the new page locally so we need to make this symbolic link on the skylinesC server:
"""
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
from createTorrents import createTorrents
from landscapesPage import landscapesPage

args = getParams()

loopWaitTime = 5 # min when idle before checking agin (can be changed by checkGrowth)
maxZipTilTorr = 10 # then will run createTorrents if Linux
nThreads = {'linux': 1, 'windows': 12}

versions = ['C2','C3']
versionUpdateTag = '_to_{}'.format(versions[1])
versionBothTag = versions[0] + versions[1]
highVCheckExt = '.tm3'
## zipping ##
linuxPathStart = '/mnt/'
winToLinPathStart = 'S:\\' #includes Samba windows mapped drive
winToWinPathStart = None

if platform.system() == 'Windows':
    print("Running on Windows...no work on links, torrents or page")
    linPathStart = winToLinPathStart
    winPathStart =  winToWinPathStart
    linux = False
else:
    linPathStart = linuxPathStart
    winPathStart =linuxPathStart
    linux = True
lowVMain = os.path.join(linPathStart,'E','landscapes','landscapesC2-main')
lowVExt1 = winPath(os.path.join(winPathStart, 'A:','landscapesC2')) # None
lowVini = os.path.join(linPathStart,'E','landscapes','landscapesC2-ini')
lowVserver = os.path.join(linPathStart,'E','landscapes','landscapesC2-server')
highVMain = os.path.join(linPathStart,'E','landscapes','landscapesC3-main')
highVExt1 = None #os.path.join(linPathStart,'E','landscapes','landscapesC3-main')
highVini = os.path.join(linPathStart,'E','landscapes','landscapesC3-ini')
highVserver = os.path.join(linPathStart,'E','landscapes','landscapesC3-server')
lowerVersionLandDirs = [lowVMain,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = os.path.join(linPathStart,'P','landscapes-zip')
# zipMain = os.path.join(winPathStart,'A:','zips')
zipExtras = None #[os.path.join(linPathStart,'E','landscapes','zipped1']
zipDirs = [zipMain] #+ zipExtras
zipPathPrior = [zipMain] # [zipExtras[0],zipMain] # fill up in this order
utilitiesDir = os.path.join(linPathStart,'L','condor-related','skylinesC','production','utilities')
## Landscapes page ##
forceLandPage = False
landPageDest = os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs')
qbtorrentExeDir = os.path.join(zipMain,'qbt_exe')
slcFilesPath = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/' #only used if can get copying by guest control working again
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
if args.links and linux:
    checkLinksIni(lowVMain, versionUpdateTag)
    checkLinksIni(highVMain, versionUpdateTag)
    checkZipsLinks(zipMain)
lowVList = os.listdir(lowVMain)
highVList = os.listdir(highVMain)

landSizes = {}

landDirs = [lowVMain, lowVExt1, highVMain]
# landDirs = [lowVMain]
allLands, allLandPaths = getLandPaths(landDirs, versionUpdateTag, args)

#### optional scripts ###
# extractZipsLandsNotUpdated(zipDirs,lowVMain,'A:\\landscapesC2',versions,versionUpdateTag,nThreads,args)
# renameDirsWithTag(dirsList,tags,tagReplacement)
# copyFilesFromVersionUpdate(allLandPaths,lowVMain, highVMain,versions,versionUpdateTag,highVCheckExt)
# sys.exit('Stop')

print('Write code for:   Start the landscape dir name with "-" to move landscape to ini only directory')
print('Write code for:   Start the landscape dir name with "." to move landscape to other landscapes folder')

loopCount = 0
nZipAfterTorr = 0
go = True
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
    if args.links and  linux:
        checkLinksIni(lowVMain,versionUpdateTag)
        checkLinksIni(highVMain,versionUpdateTag)
        checkZipsLinks(zipMain)
        updateSymlinks(landVersionsLists)
        ## now all landscapes are represented in main folders ##

    allLands, allLandPaths = getLandPaths(landDirs,versionUpdateTag, args)

    #### update symbolic links to zip files
    if linux: updateSymlinks([zipDirs])
    # get all zip paths from zipMain
    items = os.listdir(zipMain)
    for item in items:
        if item.split('.')[-1] == '7z':
            allZips.append(item)
    allZips.sort()

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
        if os.path.basename(landPath)[0] == '!' or (highVMain in landPath and land in lowVLands):
            continue                      # no zips of C2 folders linked to C3
        base, name = os.path.split(landPath)

        if versionUpdateTag in landPath:
            zipNameUpdateVers = name.replace(' ', '_') + '.7z'
            if zipNameUpdateVers not in allZips:
                toZip.append({'zipName': zipNameUpdateVers, 'landPath': landPath})
            continue
        files = os.listdir(landPath)
        iniFilePath = os.path.join(landPath,land+'.ini')
        lines = readfile(iniFilePath)
        if len(lines) > 1:
            landVersion = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
            print('len lines',len(lines))
            print ('lines', lines)
            sys.exit("Stop: .ini file can't be parsed {}".format(iniFilePath))
        condorOrigVers = origVersionFromPath(landPath)
        condorVersInName = condorOrigVers
        if args.upversion and condorOrigVers == versions[0]:
            lowOnlyZipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),landVersion,condorOrigVers) #no zips will have spaces, but landscapes folders might
            items = os.listdir(landPath)
            if land + highVCheckExt in items and not os.path.exists(lowOnlyZipName):
                condorVersInName = versionBothTag
        zipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),landVersion,condorVersInName) #no zips will have spaces, but landscapes folders might
        # if versionBothTag in zipName: #see if we need to and can merge...but zipmerge doesn't work for 7z...keep for now.
        #     zipPathlow = os.path.join(zipMain, zipName.replace(versionBothTag, versions[0]))
        #     zipNameUpdateVers = os.path.join(zipMain, name.replace(' ', '_') + versionUpdateTag +'.7z')
        #     zipPathUpdateVers = os.path.join(zipMain, zipNameUpdateVers)
        #     zipPathBothVers = os.path.join(zipMain, zipName)
        #     if os.path.exists(zipPathlow) and os.path.exists(zipPathUpdateVers) and not os.path.exists(zipPathBothVers):
        #         zipMergeIntoNew([zipPathlow, zipPathUpdateVers], os.path.join(zipMain,zipName))
        #         continue

        if zipName not in allZips and not (linux and nZipAfterTorr >= maxZipTilTorr):
            if args.growth and checkGrowth(landPath, landSizes):
                print('Will check {} for growth'.format(os.path.basename(landPath)))
                toTestGrowth.append({'zipName': zipName, 'landPath': landPath})
            else:
                toZip.append({'zipName': zipName, 'landPath': landPath})


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
        for land in toZip:
            print('{} -> {}'.format(land['landPath'], land['zipName']))
        if args.nozips:
            print('\n"nozips" chosen, but the above zips need to be created\n')
        else:
            print("Will create the above zips \n")
            # create new zips
            newZipped = []
            for newZip in toZip:
                # print('skipping zipping')
                # continue
                landPath2 = newZip['landPath']
                if 'C3' in landPath2:
                    mainPath = highVMain
                else:
                    mainDir = lowVMain

                destination = zipDestDriveByPriority(zipPathPrior, landPath2)
                zipPath = os.path.join(destination, newZip['zipName'])  # no zips will have spaces, but landscapes folders might

                count = 0
                print()
                print('----------------------------------------------------------')
                print('***Creating {} in {}***'.format(newZip['zipName'], destination))
                response = sevenzip("compression", zipPath, landPath2, nThreads)
                nZipAfterTorr += 1
    if linux:
        createdTorr = createTorrents(zipMain,watchDir,makeAllMagnets)
        if (forceLandPage or len(createdTorr) > 0 or not os.path.exists(landPageDest)):
            qbtExeLocal = get_qbtExe(qbtorrentExeDir,slcFilesPath)
            qbtExePath = get_qbtExe(qbtorrentExeDir,slcFilesPath)
            landscapesPage(zipMain,landPageDest,landHBS,qbtExeLocal,slcFilesPath,slcVMname,trackerStr)
        if args.links:
            updateSymlinks([zipDirs])

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
