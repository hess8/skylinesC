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
sys.path.append('s:\\skylinesCfiles\\skylinesC\\skylines')
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
    return versTag


def updateSymlinks(versionsLists):
    '''makes symlinks in main dir (first in versionDirs) for rest of paths in versionDirs'''
    for versionDirs in versionsLists:
        mainDir = versionDirs[0]
        listMain = os.listdir(mainDir)
        for otherDir in versionDirs[1:]:
            for item in os.listdir(otherDir):
                mainPath = os.path.join(mainDir, item)
                otherPath = os.path.join(otherDir, item)
                if item not in listMain and \
                    ('land' in mainDir.lower() and os.path.isdir(os.path.join(mainDir, item))) \
                    or \
                    ('zip' in mainDir.lower() and item.split('.')[-1] == '7z'):
                    os.system('mklink /D "{}" "{}"'.format(mainPath, otherPath))
                elif item not in list:
                    print('not added', otherDir, item)
                    print('isdir', os.path.isdir(otherPath))
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


debugMode = False
if debugMode: #use for pycharm debugging. Can't get paramiko to load in pycharm
    print("\n\nIn **debug mode**...won't run createTorrents on server\n\n")
    sleep(2)
lowVMain = 'P:\\Landscapes\\LandscapesC2\\landscapesC2-full'
lowVExt1 = 'Z:\\C2LandExt1'
lowVini = 'P:\\Landscapes\\LandscapesC2\\landscapesC2-ini'
lowVserver = 'P:\\Landscapes\\LandscapesC2\\landscapesC2-server'
highVMain = 'P:\\Landscapes\\LandscapesC3\\landscapesC3-full'
highVExt1 = 'Z:\\C3LandExt1'
highVini = 'P:\\Landscapes\\LandscapesC3\\landscapesC3-ini'
highVserver = 'P:\\Landscapes\\LandscapesC3\\landscapesC3-server'
LowerVersionLandDirs = [lowVMain,lowVExt1,lowVini,lowVserver]
HigherVersionLandDirs = [highVMain,highVExt1,highVini,highVserver]
versionsLists = [LowerVersionLandDirs, HigherVersionLandDirs]


zipMain = 'L:\\skylinesCfiles\landscapes-zip'
zipExt1 = 'R:\\zippedExt1'
zipPathPrior = []





zipDirs = [zipMain,zipExt1]

slcServerIP = '192.168.1.57'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']

lowVListA = os.listdir(lowVMain)
highVListA = os.listdir(highVMain)
#if dir in full dirs begins with "-", remove all but .ini files and move to ini dirs
print('Start the landscape dir name with "-" to move landscape to ini only directory with only ini file')
#print('To move landscape to sym link directory, start the landscape dir name with "."')
for list in [lowVListA,highVListA]:
    for item in list:
        if list == lowVListA: fullPath = lowVMain; ini = lowVini
        elif list == highVListA: fullPath = highVMain; ini = highVini
        if item[0] == '-':
            path = os.path.join(fullPath,item)
            for item2 in os.listdir(fullPath):
                if not '.ini' in item2:
                    if os.path.isdir(os.path.join(fullPath,item2)):
                        os.system('rmdir /S /Q "{}"'.format(os.path.join(fullPath,item2)))
                    else:
                        os.remove(os.path.join(fullPath,item2))
            shutil.move(path,os.path.join(ini,item.replace('-','')))
            print('Moved {} to {}'.format(path,ini))
        # elif item[0] == '.':  #legacy to move to symlinks dir...keep in code
        #     path = os.path.join(lowVMain,item)
        #     print('Moving {} to {}'.format(path,symLinksDir))
        #     shutil.move(path,os.path.join(symLinksDir,item.replace('.','')))
        #     print('Moved {} to {}'.format(path,symLinksDir))

#remove extra files from init-only dirs:
for dir1 in [lowVini,highVini]:
    for landscape in os.listdir(dir1):
        notifiedRemove = False
        for item in os.listdir(os.path.join(dir1,landscape)):
            if not '.ini' in item:
                if not notifiedRemove:
                    print ('Removing all but .ini in {}'.format(landscape))
                    notifiedRemove = True
                if os.path.isdir(os.path.join(dir1,landscape,item)):
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir1,landscape,item)))
                else:
                    os.remove(os.path.join(dir1,landscape,item))

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []
# versionDict = {'lowVList' : '2', 'highVList' : '3',}
lowVListB = os.listdir(lowVMain)
highVListB = os.listdir(highVMain)
#remove broken symbolic links
for list in [lowVListB,highVListB]:
    for item in list:
        if list == lowVListB: main1 = lowVMain
        elif list == highVListB: main1 = highVMain
        if os.path.islink(os.path.join(main1,item)) and not os.path.exists(os.path.join(main1,item,item,'.ini')):
            os.rmdir(os.path.join(main1,item))

#### update symbolic links to landscape folders

updateSymlinks(versionsLists)
## now all landscapes are represented in main folders ##

# get all landscape paths of any status
lowVListC = os.listdir(lowVMain)
highVListC = os.listdir(highVMain)
for list in [lowVListC,highVListC]:
    for item in list:
        if list == lowVListC: mainC = lowVMain
        elif list == highVListC: os.path.joinmainC = highVMain
        if os.path.isdir(os.path.join(mainC,item)) and 'WestGermany3' not in item:
            allLands.append(item)
            allLandPaths.append(os.path.join(mainC,item))

#### update symbolic links to zip files
updateSymlinks(zipDirs)
## now all zips are represented in zipMain ##

#get existing 7z files
for item in os.listdir(zipMain):
    if item.split('.')[-1] =='7z':
        allZips.append(os.path.join(zipMain,item))

#create new zips
newZipped = []
for i, landPath, in enumerate(allLandPaths):
    land = allLands[i]
    files = os.listdir(landPath)
    iniFilePath = os.path.join(landPath,land,'.ini')
    if not os.path.exists(iniFilePath) and 'path' not in iniFilePath.lower():
       ('Skipping...  No .ini file matches {}.  Consider renaming the landscape folder with the name of the .ini folder.'.format(landPath))
    elif os.path.exists(iniFilePath):
        lines = readfile(iniFilePath)
        if len(lines) > 1:
            version = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
            print('len lines',len(lines))
            print ('lines', lines)
            sys.exit("Stop: .ini file can't be parsed {}".format(iniFilePath))

        condorVers = vtagFromPath(path)
        zipName = '{}.v{}_{}.7z'.format(land.replace(' ','_'),version,condorVers) #no zips will have spaces, but landscapes folders might
        destination = zipDestDriveByPriority(zipPathPrior,landPath)
        zipPath = os.path.join(destination, zipName)  # no zips will have spaces, but landscapes folders might
        zipPathTemp = os.path.join(zipPath,'.temp')
        count = 0
        if zipPath not in allZips:
            print()
            print('----------------------------------------------------------')
            print(zipPath,)
            try:
                #create new zip
                landZip = zipPath.split('.')[0].split('')[-1]
                print ('***Creating {}***'.format(zipName))
                sevenzip(zipPathTemp,landPath)
                newZipped.append(zipPath)
                try:
                    # os.system('move {} {}'.format(zipPathTemp,zipPath)) #don't need to move...creating in zipMain
                    os.rename(zipPath,zipPath.remove('.temp'))
                    print('zip created and temp tag removed')
                    count += 1
                except:
                    sys.exit('Stop.  Problem with renaming temp file')
            except:
                print ('Error creating {}'.format(zipPath))
    else:
        print ('lines', lines)
        print('Warning: .ini file does not exist for {}'.format(landPath))
if len(newZipped) == 0:
    print ('No new landscapes to zip')
else:
    updateSymlinks(zipDirs)
# time.sleep(60)

# run createTorrents on skylinesC server
if not debugMode:
    runCreateTorrents(newZipped)

print ("Done")
