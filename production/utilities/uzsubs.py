import os,sys,shutil
import re
import subprocess
import platform
import signal
from time import sleep
from datetime import datetime
sys.path.append('/mnt/D/common_py')
sys.path.append('/mnt/P/shared_VMs/common_py')
sys.path.append('/media/sf_shared_VMs/common_py')
from common import dirSize, landscapesMap, listRunningVms, makeLink, renameTry,copy_file_to_guest,dirSize, \
    readfileNoStrip, readfile, renameTry, pathWinLin, getOKor

def getParams():
    import argparse
    forceHelp = "Force landscapespage to run"
    growthHelp = "Check dir growth before zipping"
    linksHelp = "Work on links if on linux"
    loopHelp = "Loop N times.  If N == -1, loop forever"
    nozipsHelp = "Not zip any folders"
    reverseHelp = "Go through landscapes and zip lists in reverse order"
    upversionHelp = "Work with low versions that have been updated to high"
    parser = argparse.ArgumentParser(description="Landscape compression and management")
    parser.add_argument("-f", "--force", help=forceHelp, action="store_true")
    parser.add_argument("-g", "--growth", help=growthHelp, action="store_true")
    parser.add_argument("-k", "--links", help=linksHelp, action="store_true")
    parser.add_argument("-l", "--loop", help=loopHelp, type=int)
    parser.add_argument("-n", "--nozips", help=nozipsHelp, action="store_true")
    parser.add_argument("-r", "--reverse", help=reverseHelp, action="store_true")
    parser.add_argument("-u", "--upversion", help=upversionHelp, action="store_true")

    args = parser.parse_args()
    args.upversion = True  # not keeping C2zips now
    if args.force:
        print('Will:', forceHelp)
    if args.growth:
        print('Will:', growthHelp)
    if args.links:
        print('Will:', linksHelp)
    if args.loop:
        if args.loop == -1:
            print('Will: loop forever')
        else: print('Will: loop {} times'.format(args.loop))
    if args.nozips:
        print('Will:', nozipsHelp)
    if args.reverse:
        print('Will:', reverseHelp)
    if args.upversion:
        print('Will:', upversionHelp)
    sleep(2)
    return args

def pathWinLin(path):
    linuxPathStart = '/mnt/'
    winSharedDrives = ['A']
    winSambaDrive = '\\\\192.168.1.161\\S' # 'S:\\'  # Samba windows mapped drive...not reliable
    list = path.split(os.sep)
    driveLetter = list[0]
    if platform.system() == 'Windows':
        if driveLetter in winSharedDrives:
            list[0] += ':'
            path = os.sep.join(list)
        elif winSambaDrive not in path:
            path = winSambaDrive + path
    elif linuxPathStart not in path:
        path = linuxPathStart + path
    return path

def skylinesC_VM():
    """Get skylinesC VM name from listRunningVms"""
    output = listRunningVms()
    for line in output:
        if 'U14' in line and 'SkylinesC' in line:
            name = line.split('"')[1]
            return name
    else:
        return None

def good7zOrDel(response,archive):
    if 'is not an archive' in response.lower() or 'cannot open the file as [7z]' in response.lower() or 'is not archive' in response.lower():
        print("Archive {} is corrupted: deleting it".format(archive))
        os.remove(archive)
        return 'deleted'
    elif 'error' in response.lower():
        sys.exit('Stop:  Error...{}'.format(response))
    else:
        return 'OK'

def extractZipsLandsNotUpdated(zipDirs,lowVMain,destinationDir,versions,versionUpdateTag,nThreads,args):
    for dir in zipDirs:
        dirList = sorted(os.listdir(dir), reverse=args.reverse)
        for item in dirList:
            match = re.search(r'(.*)\.v.*\.7z$',item)
            if not match or versions[1] in item or 'WestGermany3' in item:
                continue
            name_underscores = match.group(1)
            archive = os.path.join(dir,item)
            response = sevenName(archive)
            check = good7zOrDel(response,archive)
            if check == 'OK':
                trueLandName = response
            else:
                continue
            convertedFilesPath = os.path.join(lowVMain,name_underscores + versionUpdateTag)
            destination = os.path.join(destinationDir,trueLandName)
            if os.path.exists(convertedFilesPath) or os.path.exists(destination) or trueLandName in landscapesMap:
                continue
            print('Extracting {} to {}'.format(archive,destination))
            response = sevenzip("extraction", archive, destination, nThreads)
            good7zOrDel(response,archive)

def copyFilesFromVersionUpdate(allLandPaths,lowVMain,highVMain,versions,versionUpdateTag,highVCheckExt):
    print('Disabled linking')
    for i, landPath, in enumerate(allLandPaths):

        if versions[1] in landPath: #create a link in the higher version folder
            # base,name = os.path.split(landPath)
            # linkSource = landPath.replace(versionUpdateTag,'') # the full landscape folder
            # linkDest = os.path.join(highVMain,name.replace(versionUpdateTag,''))
            # if not os.path.islink(linkDest):
            #     if platform.system() == 'Linux':
            #         os.symlink(linkSource,linkDest)
            continue
        landBase,name = os.path.split(landPath)
        highVFilesDir = os.path.join(landBase, name + versionUpdateTag).replace(' ', '_')
        if os.path.exists(highVFilesDir):
            continue
        highVFiles = lowVtoHighVFiles(landPath,highVCheckExt)
        if not highVFiles:
            continue
        else:
            print(versionUpdateTag, highVFiles)
            os.mkdir(highVFilesDir)
            for newFileExistingPath in highVFiles:
                newFileSavePath = newFileExistingPath.replace(landPath,highVFilesDir)
                dirsInPath = newFileSavePath.split(highVFilesDir)[1].split(os.sep)[:-1]
                if len(dirsInPath) > 0: #create dir structure needed for file
                    nextDirPath = highVFilesDir
                    for dir in dirsInPath:
                        nextDirPath = os.path.join(nextDirPath,dir)
                        if not os.path.exists(nextDirPath):
                            os.mkdir(nextDirPath)
                shutil.copy2(newFileExistingPath, newFileSavePath)
def checkModDateAndAppend(toMatchDateTimeStamp, path, matching):
    modTimeStamp = os.path.getmtime(path)
    timeDiffAllowed = 15 #min
    if abs(modTimeStamp - toMatchDateTimeStamp)/60 < timeDiffAllowed:
        matching.append(path)
    return matching

def getFilesByModDate(path,toMatchDateTimeStamp,matching):
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_file():
                matching = checkModDateAndAppend(toMatchDateTimeStamp, entry.path, matching)
            elif entry.is_dir(): # recursive for dirs
                getFilesByModDate(entry.path, toMatchDateTimeStamp,matching)
    return matching

def lowVtoHighVFiles(landPath,highVersionProof):
    items = os.listdir(landPath)
    condorHighVersionTimeStamp = None
    for item in items:
        if highVersionProof in item:
            condorHighVersionTimeStamp = os.path.getmtime(os.path.join(landPath,item))
            matching = []
            return getFilesByModDate(landPath,condorHighVersionTimeStamp,matching)
    else:
        print('{} has not been upgraded to the new version'.format(landPath))
        return None

def signal_handler(sig, frame):
    sleep(0.1)
    #zipProc.terminate() #no longer works...can't be found.
    sleep(0.1)
    sys.exit('Stopped by user')

def upLevelDel(highestDir,upperName,lowerName):
    '''Renames upper level dir to mark for deletion.
     Moves the lowerPath to the highestDir level (where upperDir is.
     Deletes the '''
    upperDir = os.path.join(highestDir,upperName)
    renamedUpper = upperDir+'_to_del'
    renameTry(upperDir, renamedUpper)
    lowerDir = os.path.join(renamedUpper, lowerName)
    shutil.move(lowerDir,highestDir)
    shutil.rmtree(renamedUpper)
    print('removed',renamedUpper)

def sevenName(archivePath): # -mmt limits number of threads -t7z specifies type of archive
    '''gets exact landscape name from the archive, regardless of characters added to avoid spaces'''
    if platform.system() == 'Linux':
        cmd = ['7z', 'l', archivePath]
    elif platform.system() == 'Windows':
        cmd = ['C:\\Program Files\\7-Zip\\7z.exe', 'l', archivePath]
    output = None
    try:
        zipProc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,shell=True)
        output, error = zipProc.communicate()
        if zipProc.returncode != 0:
            raise subprocess.CalledProcessError(zipProc.returncode, zipProc.args, output=output, stderr=error)
        lines = output.splitlines()
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr)
        return e.stderr
    for il,line in enumerate(lines):
        if "---------" in line:
            name = lines[il+1].split(' 0 ')[-1].strip()
            return name

def sevenTest(archivePath,nThreads): # -mmt limits number of threads -t7z specifies type of archive
    if platform.system() == 'Linux':
        sigs = [signal.SIGTERM, signal.SIGTSTP, signal.SIGINT, signal.SIGQUIT, signal.SIGHUP]
        for sig in sigs:
            signal.signal(sig, signal_handler)
        maxThreads = nThreads['linux']# On Soto with base cpu at 40%...1: 60% 2: 65% 3: 70& 4:80% 5:85% 6: 95%,
        trapSigPath = '/mnt/L/condor-related/skylinesC/production/utilities/trapSignals.sh'
        cmd = ['bash', trapSigPath, '7z', 't', '-mmt={}'.format(maxThreads), archivePath]
    elif platform.system() == 'Windows':
        maxThreads = nThreads['windows']
        cmd = ['C:\\Program Files\\7-Zip\\7z.exe', 't', '-mmt={}'.format(maxThreads), archivePath]
    outputLines = subPopenTry(cmd)
    return outputLines

def sevenzip(action,archivePath,folderPath,nThreads): # -mmt limits number of threads -t7z specifies type of archive
    compressTemp  = '.temp'
    extractTemp = '_temp'
    if action == 'compression':
        command = 'a'
        preFolder = ''
        archivePath += compressTemp
        if os.path.exists(archivePath):
            os.remove(archivePath)
    elif action == 'extraction':
        command = 'x' # 'e' doesn't keep dir structure
        folderPath += extractTemp
        preFolder = '-o'
    if platform.system() == 'Linux':
        sigs = [signal.SIGTERM, signal.SIGTSTP, signal.SIGINT, signal.SIGQUIT, signal.SIGHUP]
        for sig in sigs:
            signal.signal(sig, signal_handler)
        maxThreads = nThreads['linux']# On Soto with base cpu at 40%...1: 60% 2: 65% 3: 70& 4:80% 5:85% 6: 95%,
        trapSigPath = '/mnt/L/condor-related/skylinesC/production/utilities/trapSignals.sh'
        cmd = ['bash', trapSigPath, '7z', command, '-t7z', '-y', '-mmt={}'.format(maxThreads), archivePath, preFolder+folderPath]
    elif platform.system() == 'Windows':
        maxThreads = nThreads['windows']
        cmd = ['C:\\Program Files\\7-Zip\\7z.exe', command, '-t7z', '-y', '-mmt={}'.format(maxThreads), archivePath, preFolder+folderPath]
    output = None
    try:
        zipProc = subprocess.Popen(cmd,stdout=subprocess.PIPE,text=True) # Exits on linux if shell = True
        output, error = zipProc.communicate()
        if zipProc.returncode != 0:
            raise subprocess.CalledProcessError(zipProc.returncode, zipProc.args, output=output, stderr=error)
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr)
        sys.exit('Stop. Problems with {}'.format(action))
        return e.stderr
    # lines = output.splitlines()
    print(output)
    # print ("Windows 7zip done.  Run on Linux for links, torrents and page work")
    print("7zip finished {}".format(action))
    if action == 'compression':
        finalPath = archivePath.replace(compressTemp,'')
        renameTry(archivePath, finalPath)
    elif action == 'extraction':
        base, _ = os.path.split(folderPath)
        trueLandName = sevenName(archivePath)
        finalPath = os.path.join(base,trueLandName)
        renameTry(folderPath, finalPath)
        upLevelDel(base,trueLandName,trueLandName)
    print("7zip finished {}".format(action))
    return output
        # Following implements working cpulimit but signal handle doesn't work
    # maxCPU = 80  # %
    # cmd = ['cpulimit','-l',str(maxCPU),'--','bash',trapSigPath, '7z', 'a', '-t7z', archivePath, folderPath]

def origVersionFromPath(path):
    ''''''
    '''Gets version tag from regex pattern: C[any digits] in path'''
    versTag = re.search("C[0-9]+",path)
    return versTag[0]


def updateSymlinks(dirsLists):
    """"""
    '''makes symlinks in main dir (first in dirsLists) for rest of paths in dirsLists
    Works for both landscapes and zips folder.
    '''

    xx=0
    for list in dirsLists:
        mainDir = list[0]
        listMain = os.listdir(mainDir)
        for otherDir in list[1:]:
            for item in os.listdir(otherDir):
                mainPath = os.path.join(mainDir, item)
                otherPath = os.path.join(otherDir, item)
                if item in listMain: # note: isdir is true for a link pointing to a dir
                    if not os.path.islink(mainPath) and not os.path.islink(otherPath):
                        print('Duplication:  No symlink created between {} and {}.'.format(mainPath,otherPath))
                elif 'zip' in mainDir.lower():
                    if item.split('.')[-1] == '7z':
                        makeLink(truePath=otherPath,linkPath=mainPath)
                elif not os.path.islink(otherPath):
                   makeLink(truePath=otherPath,linkPath=mainPath)

def get_free_space_gb(drive):
    """Gets the free space on the specified drive in GB."""
    total, used, free = shutil.disk_usage(drive)
    return free / (2 ** 30)  # 1 GB = 2^30 bytes

def get_file_size_in_gb(filepath):
    """Gets the file size in gigabytes (GB)."""
    file_size_bytes = os.path.getsize(filepath)
    file_size_gb = file_size_bytes / (1024 ** 3)  # 1GB = 1024**3 bytes
    return file_size_gb

def zipDestDriveByPriority(priorList,toCompressPath):
    ''''''
    compressFactor = 0.8 * float(120/50)
    for dest in priorList:
        avail = get_free_space_gb(dest)
        size = get_file_size_in_gb(toCompressPath)
        if size/compressFactor < avail:
            return dest
    else:
        os.stop('Probably not enough room in dirs {} to compress dir {}, {} Gb'.format(priorList,toCompressPath,  size))
def checkZipsLinks(zipMain):
    '''Removes bad links'''
    zipMainList = os.listdir(zipMain)
    for mainItem in zipMainList:
        itemMainPath = os.path.join(zipMain, mainItem)
        if 'Cz' in mainItem:
            xx=0
        if os.path.islink(itemMainPath) and not os.path.exists(itemMainPath):
            os.remove(itemMainPath)
            print('Removed broken link {}'.format(mainItem))


def checkLinksIni(mainDir,versionUpdateTag):
    '''Checks for bad links and addresses mismatch between landscape and ini names'''
    mainDirList = os.listdir(mainDir)
    for mainItem in mainDirList:
        if versionUpdateTag in mainItem:
            continue
        itemMainPath = os.path.join(mainDir, mainItem)
        if not os.path.isdir(itemMainPath): continue
        if 'no_ini' in mainItem or not os.path.isdir(itemMainPath):
            continue
        elif os.path.islink(itemMainPath) and not os.path.isdir(itemMainPath):
            os.remove(itemMainPath)
            print('Removed broken link {}'.format(mainItem))
            continue
        landscapeDir = itemMainPath
        landscapeDirList = os.listdir(landscapeDir)
        for landDirItem in landscapeDirList:
            if '.ini' in landDirItem:
                file_name, extension = os.path.splitext(landDirItem)
                if extension != '.ini': # extension corrupted
                    newLandDirItem = landDirItem.replace(extension,'.ini')
                    renameTry(os.path.join(landscapeDir,landDirItem),os.path.join(landscapeDir,newLandDirItem))
                iniName = os.path.basename(landDirItem).split('.')[0]
                if iniName != mainItem and 'patch' not in mainItem.lower() and 'WestGermany3' not in mainItem:
                    # try:
                        print(
                            "The .ini file name {} doesn't match {}.  Rename the landscape folder with the name of the .ini file"
                            .format(landDirItem, mainItem))
                        landscapeDirOld = landscapeDir
                        landscapeDir = os.path.join(mainDir,iniName)
                        renameTry(landscapeDirOld, landscapeDir)
                        if os.path.islink(landscapeDir):
                            targetPath = os.readlink(landscapeDir)
                            targetList = targetPath.split(os.sep)
                            if targetList[-1] != iniName:
                                renameTry(targetPath, os.path.join(os.sep.join(targetList[:-1]),iniName))

                    # except:
                    #     renameTry(landscapeDir, os.path.join(mainDir,'__no_match_ini_' + iniName))
                break
        else:
                print('no .ini file found in full dir {}; adding "!no_ini_" to name'.format(landscapeDir))
                renameTry(landscapeDir,os.path.join(mainDir, "!no_ini_" + mainItem))

def get_qbtExe(qbtorrentExeDir):
    items = os.listdir(qbtorrentExeDir)
    items.sort()
    for item in items:
        if re.search("qb.*exe",item.lower()):
            exePath = os.path.join(qbtorrentExeDir,item)
            return exePath
    else:
        sys.exit("Stop.  Can't find path to qbittorrent.exe for landscapes.hbs")

def getLandPaths(topLandDirs, versionUpdateTag, args):
    from more_itertools import sort_together
    allLands = []
    allLandPaths = []
    for topDir in topLandDirs:
        items = os.listdir(topDir)
        for item in items:
            itemPath = os.path.join(topDir, item)
            if not item in allLands and os.path.isdir(itemPath) and ( ('Textures' in os.listdir(itemPath) and 'WestGermany3' not in item and 'Slovenia' not in item)
                        or versionUpdateTag in item ): # note: isdir is true for a link pointing to a dir
                allLands.append(item)
                allLandPaths.append(itemPath)
                cupFile = os.path.join(itemPath,item+'.cup')
                if not os.path.exists(cupFile) and 'Textures' in os.listdir(itemPath): #.cup file required for COTACO task converter
                    os.system('echo "name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,descr \n" > {}'.format(cupFile))
                    print('created', cupFile)

    allLands, allLandPaths = sort_together([allLands, allLandPaths],reverse=args.reverse)
    return allLands, allLandPaths

def checkGrowth(landPath,landSizes):
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
        return True #wait til next loop to check
