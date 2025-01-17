import os,sys,shutil
import re
import subprocess
from time import sleep


slcServerIP = '192.168.1.14'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']

def sevenzip(tempPath,landPath): # -mmt limits number of threads -t7z specifies type of archive
    import signal
    def signal_handler(sig, frame):
        sleep(0.1)
        zipProc.terminate()
        sleep(0.1)
        sys.exit('Stopped by user')

    for sig in [signal.SIGTERM, signal.SIGTSTP, signal.SIGINT, signal.SIGQUIT, signal.SIGHUP]:
        signal.signal(sig, signal_handler)
    maxCPU = 80  # %
    maxThreads = 4# With base cpu at 40%...1: 60% 2: 65% 3: 70& 4:80% 5:85% 6: 95%,
    trapSigPath = '/mnt/L/condor-related/skylinesC/production/utilities/trapSignals.sh'
    cmd = ['bash', trapSigPath, '7z', 'a', '-t7z', '-mmt={}'.format(maxThreads),tempPath, landPath]
    # Following implements working cpulimit but signal handline doesn't work
    # cmd = ['cpulimit','-l',str(maxCPU),'--','bash',trapSigPath, '7z', 'a', '-t7z', tempPath, landPath]
    zipProc = subprocess.Popen(cmd)
    zipProc.communicate()

def versionFromPath(path):
    ''''''
    '''Gets version tag from regex pattern: C[any digits] in path'''
    versTag = re.search("C[0-9]+",path)
    return versTag[0]


def updateSymlinks(dirsLists):
    """"""
    '''makes symlinks in main dir (first in dirsLists) for rest of paths in dirsLists
    Works for both landscapes and zips folder.
    If zips folder, removes .temp files'''

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
                        makeLink(mainPath, otherPath)
                elif not os.path.islink(otherPath):
                    makeLink(mainPath, otherPath)
        #remove .temp files
        if 'zip' in mainDir.lower():
            for dir in list:
                for item in os.listdir(dir):
                    if 'zip' in item and item.split('.')[-1] == 'temp':
                        os.remove(os.path.join(dir,item))

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


def checkLinksIni(mainDir):
    '''Checks for bad links and addresses mismatch between landscape and ini names'''
    mainDirList = os.listdir(mainDir)
    for mainItem in mainDirList:
        if 'sweden' in mainItem:
            xx=0
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

def makeLink(linkDir, realDir):
    try:
        os.symlink(realDir, linkDir)
        # os.system('mklink "{}" "{}"'.format(, realDir))
    except:
        print('Problem creating symblolic link {} -> {}'.format(linkDir, realDir))

def get_qbtExe(qbtorrentExeDir,slcFilesPath):
    items = os.listdir(qbtorrentExeDir)
    items.sort()
    exeDirList = qbtorrentExeDir.split(os.sep)
    for item in items:
        if re.search("qb.*exe",item.lower()):
            u14path = os.path.join(slcFilesPath,exeDirList[-1],item)
            return u14path
    else:
        sys.exit("Stop.  Can't find path to qbittorrent.exe for landscapes.hbs")

def getLandPaths(lowVMain,highVMain):
    allLands = []
    allLandPaths = []
    for dir in [lowVMain,highVMain]:
        items = os.listdir(dir)
        for item in items:
            itemPath = os.path.join(dir, item)
            if os.path.isdir(itemPath) and \
                'Textures' in os.listdir(itemPath) \
                and 'WestGermany3' not in item and 'Slovenia' not in item: # note: isdir is true for a link pointing to a dir
                    allLands.append(item)
                    allLandPaths.append(os.path.join(dir, item))
    return allLands, allLandPaths

def dirSize(path):
    result = subprocess.run(["du", "-s", path], stdout=subprocess.PIPE, text=True)
    size = result.stdout.split('\t')[0]
    return size

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
