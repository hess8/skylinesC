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

from uzsubs import *
from time import perf_counter
from createTorrents import createTorrents
from landscapesPage import landscapesPage

args = getParams()
forever = False
if args.loop == -1:
    forever = True

loopWaitTime = 5 # min when idle before checking agin (can be changed by checkGrowth)
maxZipTilTorr = 10 # then will run createTorrents if Linux
nThreads = {'linux': 8, 'windows': 12}

versionBothTag = versions[0] + versions[1]
highVCheckExt = '.tm3'

## zipping ##
if platform.system() == 'Windows':
    print("Running on Windows...no work on links, torrents or page")
    linux = False
else:
    linux = True
lowVMain = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
lowVExt1 = pathWinLin(os.path.join('A','landscapesC2')) # None
lowVini = pathWinLin(os.path.join('E','landscapes','landscapesC2-ini'))
lowVserver = pathWinLin(os.path.join('E','landscapes','landscapesC2-server'))
highVMain = pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))
highVExt1 = None #pathWinLin(os.path.join('E','landscapes','landscapesC3-main')
highVini = pathWinLin(os.path.join('E','landscapes','landscapesC3-ini'))
highVserver = pathWinLin(os.path.join('E','landscapes','landscapesC3-server'))
lowerVersionLandDirs = [lowVMain,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = pathWinLin(os.path.join('P','shared_VMs','skylinesC-related','landscapes-zip'))
# zipMain = pathWinLin(os.path.join(winPathStart,'A:','zips')
zipExtras = None #[pathWinLin(os.path.join('E','landscapes','zipped1']
zipDirs = [zipMain] #+ zipExtras
zipPathPrior = [zipMain] # [zipExtras[0],zipMain] # fill up in this order
utilitiesDir = pathWinLin(os.path.join('L','condor-related','skylinesC','production','utilities'))
## Landscapes page ##
landPageLocalDest = pathWinLin(os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs'))
qbtExeLocalPath = get_qbtExe(pathWinLin(os.path.join(zipMain,'qbt_exe')))
convert_landscapesPath = pathWinLin(os.path.join('/home/bret/skylinesC/production/utilities/','Convert-Landscapes.ps1'))
slcPath = '/home/bret/skylinesC/'
slcFilesPath = os.path.join(slcPath, 'htdocs/files/')
landPageServerDest = os.path.join(slcPath,'ember/app/templates/landscapes.hbs')

## Torrents ##
trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = pathWinLin(os.path.join(zipMain + '/qbtWatch'))
makeAllMagnets = False  # needed only occasionally

qbtExeName = qbtExeLocalPath.split(os.sep)[-1]
qbtExeDest = os.path.join(slcFilesPath,qbtExeName)
qbtWebPath = os.path.join('/files',qbtExeName)
slcVMname = skylinesC_VM()
[username, passwd] = readfile('/home/bret/.credentials/userU')

########
print('Starting')
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

landDirs = [lowVMain, highVMain]#[lowVMain, lowVExt1, highVMain]
# landDirs = [lowVMain]
allLands, allLandPaths = getLandPaths(landDirs, versionUpdateTag, args)

#### optional scripts ###
# extractZipsLandsNotUpdated(zipDirs,lowVMain,'A:\\landscapesC2',versions,versionUpdateTag,nThreads,args)
# renameDirsWithTag(dirsList,tags,tagReplacement)
# copyFilesFromVersionUpdate(allLandPaths,lowVMain, highVMain,versions,versionUpdateTag,highVCheckExt)
# linkWinLinAllDir('\\192.168.1.161\\E\\landscapes\\landscapesC2-main','C:\\Condor2\\Landscapes')
# linkWinLinAllDir('s:\\E\\landscapes\\landscapesC2-main','C:\\Condor2\\Landscapes')
# linkWinLinAllDir('s:\\E\\landscapes\\landscapesC3-main','C:\\Condor3\\Landscapes')
# sys.exit('Stop')

print('Write code for:   Start the landscape dir name with "-" to move landscape to ini only directory')
print('Write code for:   Start the landscape dir name with "." to move landscape to other landscapes folder')

loopCount = 0
nZipAfterTorr = 0
go = True
while go:
    startTime = perf_counter()
    loopCount += 1
    #'.' and '-' tags
    #Move newly marked files to ini-only
    for list in [lowVList]:
        for item in list:
            if list == lowVList: mainPath = lowVMain; ini = lowVini
            elif list == highVList: mainPath = highVMain; ini = highVini
            if item[0] == '-':
                landPath = os.path.join(mainPath,item)
                rmExceptIni(landPath,item)
                shutil.move(landPath,os.path.join(ini,item.replace('-','')))
                print('Moved {} to {}'.format(landPath,ini))

            #######
            # elif item[0] == '.':  #legacy to move to symlinks dir...keep in code
            #     path = os.path.join(lowVMain,item)
            #     print('Moving {} to {}'.format(path,symLinksDir))
            #     shutil.move(path,os.path.join(symLinksDir,item.replace('.','')))
            #     print('Moved {} to {}'.format(path,symLinksDir))


    allZips = []
    allZipsPaths = []
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
            path = os.path.join(zipMain, item)
            #os.system('touch {}.torrent'.format(path))
            allZipsPaths.append(os.path.join(zipMain, item))
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
    # check for needed zips
    for i, landPath, in enumerate(allLandPaths):
        land = allLands[i]
        if land == 'Japan-Kyusyu3':
            xx=0
        if os.path.basename(landPath)[0] == '!' or (highVMain in landPath and land in lowVLands):
            continue                      # no zips of C2 folders linked to C3
        base, name = os.path.split(landPath)
        #Archive containing only files to update from low to high version
        if versionUpdateTag in landPath:
            zipNameUpdateVers = name.replace(' ', '_') + '.7z'
            if zipNameUpdateVers not in allZips:
                toZip.append({'zipName': zipNameUpdateVers, 'landPath': landPath})
            continue
        files = os.listdir(landPath)
        iniFilePath = os.path.join(landPath,land+'.ini')
        if os.path.exists(iniFilePath):
            lines = readfile(iniFilePath)
        else:
            print('{} has no .ini file'.format(landPath))
            continue
        if len(lines) > 1:
            landVersion = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
            print('len lines',len(lines))
            print ('lines', lines)
            sys.exit("Stop: .ini file can't be parsed {}".format(iniFilePath))
        condorOrigVers = origVersionFromPath(landPath)
        cVersInNewZip = condorOrigVers
        if condorOrigVers == versions[0]:
            if args.upversion:
                items = os.listdir(landPath)
                if land + highVCheckExt in items:
                    cVersInNewZip = versionBothTag
                else:
                    print('Landscape {} needs to be updated to {}'.format(land, versions[1]))
                    continue

        zipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),landVersion,cVersInNewZip) #no zips will have spaces, but landscapes folders might
        # if versionBothTag in zipName: #see if we need to and can merge...but zipmerge doesn't work for 7z...keep for now.
        #     zipPathlow = os.path.join(zipMain, zipName.replace(versionBothTag, versions[0]))
        #     zipNameUpdateVers = os.path.join(zipMain, name.replace(' ', '_') + versionUpdateTag +'.7z')
        #     zipPathUpdateVers = os.path.join(zipMain, zipNameUpdateVers)
        #     zipPathBothVers = os.path.join(zipMain, zipName)
        #     if os.path.exists(zipPathlow) and os.path.exists(zipPathUpdateVers) and not os.path.exists(zipPathBothVers):
        #         zipMergeIntoNew([zipPathlow, zipPathUpdateVers], os.path.join(zipMain,zipName))
        #         continue

        if zipName not in allZips and not nZipAfterTorr >= maxZipTilTorr:
            if args.growth and checkGrowth(landPath, landSizes):
                print('Will check {} for growth'.format(os.path.basename(landPath)))
                toTestGrowth.append({'zipName': zipName, 'landPath': landPath})
            else:
                #add full landscape
                toZip.append({'zipName': zipName, 'landPath': landPath})
                print('added',zipName)
                #remove old versions of same name
                if '.v' in zipName:
                    land = os.path.split(landPath.split('.')[0])[-1]
                    for path in allZipsPaths:
                        zipLand = os.path.split(path.split('.')[0])[-1]
                        if zipLand == land and land!='WestGermany3':
                            if getConfirmation('Do you want to remove old version {}'.format(path)):
                                os.remove(path)
                                print('removed',path)



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

    if linux:
        createdTorr = createTorrents(zipMain,watchDir,makeAllMagnets)
        qbtExeName = qbtExeLocalPath.split(os.sep)[-1]
        qbtExeDest = os.path.join(slcFilesPath,qbtExeName)
        qbtWebPath = os.path.join('/files',qbtExeName)
        slcVMname = skylinesC_VM()
        [username, passwd] = readfile('/home/bret/.credentials/userU')
        if args.force or len(createdTorr) > 0 or not os.path.exists(landPageLocalDest):
            landscapesPage(zipMain,landPageLocalDest,qbtWebPath,trackerStr,versions,args)
            if slcVMname:
                e = copy_file_to_guest(slcVMname, landPageLocalDest, landPageServerDest, username, passwd)
                if e:
                    sys.exit(f'Stop: error copying landscapes page to SLC: {e}')
                print('Copied landscapes page to SkylinesC server')
            else:
                sys.exit('SkylinesC server appears not to be running')
        if os.path.exists(convert_landscapesPath) and slcVMname:
            e = copy_file_to_guest(slcVMname, convert_landscapesPath, os.path.join(slcFilesPath, 'Convert-Landscapes.ps1'),
                               username, passwd)
            if e:
                sys.exit(f'Stop: error copying convert_landscapes page to SLC: {e}')
            print('Copied {} to SkylinesC server'.format(convert_landscapesPath))
        else:
            print('Cannot copy Convert-Landscapes to SkylinesC server')
        if os.path.exists(qbtExeLocalPath):
            e = copy_file_to_guest(slcVMname, qbtExeLocalPath, qbtExeDest, username, passwd)
            if e:
                sys.exit(f'Stop: error copying qbt executable to SLC: {e}')
            print('Copied {} to SkylinesC server'.format(qbtExeLocalPath))
        else:
            print('Cannot copy qbt executable to SkylinesC server: not found at', qbtExeLocalPath)
    if not forever and (not args.loop or loopCount == args.loop):
        print('Done')
        break
    waitTimeMins = int(max(0,loopWaitTime - (perf_counter() - startTime)/60)) #minutes
    for i in range(waitTimeMins):
        print("\r", end='')
        print('[loop {}]  Waiting {} min '.format(loopCount, waitTimeMins - i), flush=True, end='')
        sleep(60)
    print("\r", end='')
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
