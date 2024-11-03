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

import os,sys,shutil
import re
# import py7zr #py7zr does not follow symlinks!  So we use C:\Program Files\7-Zip.  See note above
# import win32com.client

# from subprocess import Popen, PIPE
# print(os.path.abspath(os.curdir))
sys.path.append('L:\\skylinesCfiles\\skylinesC\\skylines')
from time import sleep
from common import readfileNoStrip, readfile

def sevenzip(tempPath,landPath):
    os.system('7z a -t7z "{}" "{}"'.format(tempPath,landPath)) #quotes to handle spaces in windows file names
#     os.system('py7zr c "{}" "{}"'.format(tempPath,landPath))
#     with py7zr.SevenZipFile(tempPath, 'w') as archive:
#                     archive.writeall(landPath, 'base')  #This seems slow, but uses threads well

def runCreateTorrents(newZipped):
    import paramiko
    if len(newZipped) > 0:
        k = paramiko.Ed25519Key.from_private_key_file(keyFile)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=slcServerIP, username=user, pkey=k)
        except:
            print('ssh.connect failed to {}'.format(slcServerIP))
        print('Connecting to {} to create torrents'.format(slcServerIP))
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('python /home/bret/servers/repo-skylinesC/skylinesC/production/utilities/createTorrents.py')
        stdout = ssh_stdout.readlines()
        stderr = ssh_stderr.readlines()
        if len(stderr) > 0:
            print('Errors in createTorrents command:')
            for line in stderr:
                print(line)
        else:
            print('Results:')
            for line in stdout:
                print(line)

def vtagFromPath(path):
    ''''''
    '''Gets version tag from regex pattern: C[any digits] in path'''
    versTag = re.search("C[0-9]+",path)
    return versTag[0]


def updateSymlinks(dirsLists):
    '''makes symlinks in main dir (first in versionDirs) for rest of paths in versionDirs'''
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
                        print('Duplication of directories:  No symlink created between {} and {}.'.format(mainPath,otherPath))
                elif 'zip' in mainDir.lower() and item.split('.')[-1] == '7z':
                    os.system('mklink "{}" "{}"'.format(mainPath, otherPath))
                elif not os.path.islink(otherPath):
                    os.system('mklink /D "{}" "{}"'.format(mainPath, otherPath))


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
        drive = dest.split(os.sep)[0]
        avail = get_free_space_gb(drive)
        size = get_file_size_in_gb(toCompressPath)
        if size/compressFactor < avail:
            return dest
    else:
        os.stop('Probably not enough room in dirs {} to compress dir {}, {} Gb'.format(priorList,toCompressPath,  size))


def checkForIni(mainDir):
    '''Checks for bad links and addresses mismatch between landscape and ini names'''
    mainDirList = os.listdir(mainDir)
    for mainItem in mainDirList:
        itemMainPath = os.path.join(mainDir, mainItem)
        if mainItem[:2] == 'no':
            continue
        elif os.path.islink(itemMainPath) and not os.path.isdir(itemMainPath):
            os.remove(itemMainPath)
            print('Removed broken link {}'.format(mainItem))
            continue
        itemDirList = os.listdir(itemMainPath)
        for dirItem in itemDirList:
            if '.ini' in dirItem:
                iniName = os.path.basename(dirItem).split('.')[0]
                if iniName != mainItem and 'patch' not in mainItem.lower() and 'WestGermany3' not in mainItem:
                    try:
                        os.rename(itemMainPath, os.path.join(mainDir,iniName))
                        print(
                            "The .ini file name {} doesn't match {}.  Renamed the landscape folder with the name of the .ini file"
                            .format(dirItem, mainItem))
                        xx=0
                    except:
                        try:
                            os.rename(itemMainPath, os.path.join(mainDir,'no_match_ini_' + iniName))
                            print('Renamed {} to {}'.format(itemMainPath,os.path.join(mainDir,'no_match_ini_' + iniName)))
                        except:
                            os.stop("Stop: can't rename {} to {}".format(itemMainPath,os.path.join(mainDir,'no_match_ini_' + iniName)))
                break
        else:
            print('no .ini file found in full dir {}; adding "no_ini_" to name'.format(itemMainPath))
            os.rename(itemMainPath, "no_ini_"+itemMainPath)

debugMode = False
if debugMode: #use for pycharm debugging. Can't get paramiko to load in pycharm
    print("\n\nIn **debug mode**...won't run createTorrents on server\n\n")
    sleep(2)
lowVMain = 'P:\\landscapes\\landscapesC2\\landscapesC2-main'
lowVExt1 = 'Z:\\C2LandExt1'
lowVini = 'P:\\landscapes\\landscapesC2\\landscapesC2-ini'
lowVserver = 'P:\\landscapes\\landscapesC2\\landscapesC2-server'
highVMain = 'P:\\landscapes\\landscapesC3\\landscapesC3-main'
highVExt1 = 'Z:\\C3LandExt1'
highVini = 'P:\\landscapes\\landscapesC3\\landscapesC3-ini'
highVserver = 'P:\\landscapes\\landscapesC3\\landscapesC3-server'
lowerVersionLandDirs = [lowVMain,lowVExt1,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVExt1,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]

zipMain = 'P:\\landscapes\\landscapes-zip'
zipExt1 = 'R:\\zippedExt1'
zipDirs = [zipMain,zipExt1]
zipPathPrior = [zipExt1,zipMain] # fill up in this order

slcServerIP = '192.168.1.57'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']

lowVListA = os.listdir(lowVMain)
highVListA = os.listdir(highVMain)

# #temp
# print(' temp changing zip file names')
# for dir in zipDirs:
#     list = os.listdir(dir)
#     for item in list:
#         if '.7z' in item and '_C2.7z' not in item and 'C3' not in item:
#             os.rename(os.path.join(dir,item), os.path.join(dir,item.replace('.7z','_C2.7z' )))

#temp add C2 back to some names
#
list = os.listdir(lowVMain)
tochange = ['Belgium','Atlantide','','','','','',]
for land in list:
    landbase = land.replace('_C2','')
    if landbase not in tochange:
        continue
    dirlist = os.listdir(os.path.join(lowVMain,land))
    newland = land + '_C2'
    os.rename(os.path.join(lowVMain,land),os.path.join(lowVMain,newland))
    for item in dirlist:
        if land in item:
            os.rename(os.path.join(lowVMain,newland, item), os.path.join(lowVMain,newland, item + '_C2'))
        if '_C2' in item:
            newname = item.replace('_C2','')
            name2 = newname.replace(landbase,landbase+'_C2')
            os.rename(os.path.join(lowVMain,land,item),os.path.join(lowVMain,land,name2))


#if dir in main dirs begins with "-", remove all but .ini files and move to ini dirs
print('Start the landscape dir name with "-" to move landscape to ini only directory with only ini file')
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
checkForIni(lowVMain)
checkForIni(highVMain)

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
    if os.path.basename(landPath)[:2] == 'no':
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
    condorVers = vtagFromPath(landPath)
    zipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),version,condorVers) #no zips will have spaces, but landscapes folders might
    if zipName not in allZips:
        toZip.append(zipName)
if len(toZip) > 0:
    print("Will create these zips:")
    for name in toZip:
        print(name)

#create new zips
newZipped = []
for name in toZip:
        destination = zipDestDriveByPriority(zipPathPrior,landPath)
        zipPath = os.path.join(destination, zipName)  # no zips will have spaces, but landscapes folders might
        zipPathTemp = os.path.join(zipPath + '.temp')
        count = 0
        if zipName not in allZips:
            print()
            print('----------------------------------------------------------')

            try:
                #create new zip
                print ('***Creating {}***'.format(zipName))
                print(zipPath, )
                sevenzip(zipPathTemp,landPath)
                newZipped.append(zipPath)
                try:
                    # os.system('move {} {}'.format(zipPathTemp,zipPath)) #don't need to move...creating in zipMain
                    os.rename(zipPath,zipPath.remove('.temp'))
                    print('zip created and temp tag removed')
                    count += 1
                except:
                    print('Problem with renaming temp file')
            except:
                print ('Error creating {}'.format(zipPath))

if len(newZipped) == 0:
    print ('No new landscapes to zip')
else:
    updateSymlinks(zipDirs)
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
