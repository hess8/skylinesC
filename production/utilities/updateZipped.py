# '''

# RUN AS ADMIN
# 1. run in windows (anaconda "conda activate bchenv") as ADMIN python d:\skylinesC\production\utilities\updateZipped.py
# 2. conda activate bch39
# 3. Add to windows path:  "C:\Program Files\7-Zip"
# 4. confirmation that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
# link target eg C:\Users\Bret\AppData\Local\qBittorrent\logs\qbittorrent.log
#   sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.
#
# Add "-" to the beginning of the landscape dir name to remove all but .ini files and move to iniOnlyDir
# Add "." to the beginning of the landscape dir name to move landscape to symlink directory,

# ssh access: make sure port 22 is open on U14.  Test ssh connection manually
# '''

import os,sys,shutil
# import py7zr
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

def linktoSSDdrive(zipDir,ssdDir,popular,zipsOnSSD):
    # replace zip files with symbolic links to ssdDrive
    for landZip in popular:
        zipPath = '{}\\{}'.format(zipDir, landZip)
        ssdPath = '{}\\{}'.format(ssdDir, landZip)
        if landZip in zipsOnSSD and not os.path.exists(zipPath):
            # print('Symlink for ssdDrive {}.'.format(landZip))
            os.system('mklink "{}" "{}"'.format(zipPath, ssdPath))

def getSSDdriveList(ssdDir):
    listSSD = os.listdir(ssdDir)
    zipsOnSSD = []
    for item in listSSD:
        if item.split('.')[-1] == '7z' and os.path.getsize(os.path.join(ssdDir,item)) > 10:
            zipsOnSSD.append(item)
    return zipsOnSSD

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
    #check that new torrents have been added to the qbittorrent servers
    # time.sleep(5)
    # shell = win32com.client.Dispatch("WScript.Shell")
    # for logfile in qbtLogLinks:
    #     shortcut = shell.CreateShortCut('{}\\{}'.format(zipDir,logfile))
    #     lines = readfile(shortcut.Targetpath)
    #     for zipped in newZipped:
    #         for line in lines:
    #             if 'added to download list' in line and zipped in line:
    #                 print('New torrent {} found in {}').format(zipped,logfile)
    #                 break
    #         else:
    #             print('Error. {} not found in {}').format(zipped,logfile)
    # time.sleep(5)


# fill up SSDdir and remove original files in zipDir
populateSSD = False # fill up SSDdir and remove original files in zipDirD
debugMode = False
if debugMode: #use for pycharm debugging. Can't get paramiko to load in pycharm
    print("\n\nIn **debug mode**...won't run createTorrents on server\n\n")
    sleep(2)
mainDir = 'Z:\\Condor\\Landscapes'
symLinksDir = 'L:\\landscapes_for_symlinks'  #py7zr does not follow symlinks
# otherDir2 = 'L:\\landscapes_for_symlinks2'
iniOnlyDir = 'L:\\landscapes_ini_only'
serverOnlyDir = 'L:\\landscapes_server_only'
zipDir = 'S:\\skylinesCfiles\landscapes-zip'
ssdDir = 'R:'
popularFile = os.path.join(zipDir,'.popularity.txt')
slcServerIP = '192.168.1.57'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']
mainList0 = os.listdir(mainDir)
#remove extra files from ini_only dirs:
for dir in [iniOnlyDir]:# :
    for landscape in os.listdir(dir):
        notifiedRemove = False
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                if not notifiedRemove:
                    print ('Removing all but .ini in {}'.format(landscape))
                    notifiedRemove = True
                if os.path.isdir(os.path.join(dir,landscape,item)):
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir,landscape,item)))
                else:
                    os.remove(os.path.join(dir,landscape,item))

#if folder (not symbolic link) in mainDir begins with "-", remove all but .ini files and move to iniOnlyDir
print('To move landscape to ini only directory with only ini file, start the landscape dir name with "-"')
print('To move landscape to sym link directory, start the landscape dir name with "."')
for item in mainList0:
    if item[0] == '-':
        path = os.path.join(mainDir,item)
        for item2 in os.listdir(path):
            if not '.ini' in item2:
                if os.path.isdir(os.path.join(path,item2)):
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(path,item2)))
                else:
                    os.remove(os.path.join(path,item2))
        shutil.move(path,os.path.join(iniOnlyDir,item.replace('-','')))
        print('Moved {} to {}'.format(path,iniOnlyDir))
    elif item[0] == '.':
        path = os.path.join(mainDir,item)
        print('Moving {} to {}'.format(path,symLinksDir))
        shutil.move(path,os.path.join(symLinksDir,item.replace('.','')))
        print('Moved {} to {}'.format(path,symLinksDir))

mainList = os.listdir(mainDir)

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []

#remove broken symbolic links
for item in mainList:
    if os.path.islink('{}\\{}'.format(mainDir,item)) and not os.path.exists('{}\\{}\\{}.ini'.format(mainDir,item,item)):
        os.rmdir('{}\\{}'.format(mainDir,item))
#update symbolic links
for dir in [symLinksDir, iniOnlyDir,serverOnlyDir]:
# for dir in [symLinksDir, iniOnlyDir]:
    for item in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,item)) and item not in mainList:
            # print ('Symlink for {}.'.format(item))
            mainPath = '{}\\{}'.format(mainDir,item)
            otherPath = '{}\\{}'.format(dir,item)
            os.system('mklink /D "{}" "{}"'.format(mainPath,otherPath))
        elif item not in mainList:
            print ('not added', dir, item)
            print ('isdir', os.path.isdir(os.path.join(dir,item)))

#landscapes are all represented in mainDir now.
for item in os.listdir(mainDir):
    if os.path.isdir(os.path.join(mainDir,item)) and 'WestGermany3' not in item:
        allLands.append(item)
        allLandPaths.append('{}\\{}'.format(mainDir,item))


#make symbolic links from ssdDrive to zipDrive:
popular = readfile(popularFile) #ssdDir has most popular landscapes in it
zipsOnSSD = getSSDdriveList(ssdDir)
linktoSSDdrive(zipDir,ssdDir,popular,zipsOnSSD)

#zips
for item in os.listdir(zipDir):
    if item.split('.')[-1] =='7z':
        allZips.append('{}\{}'.format(zipDir,item))

#create zips
newZipped = []
for i, landPath, in enumerate(allLandPaths):
    land = allLands[i]
    files = os.listdir(landPath)
    iniPath = '{}/{}.ini'.format(landPath,land)
    if not os.path.exists(iniPath):
       print('Stop.  No .ini file matches {}.  Consider renaming the landscape folder with the name of the .ini folder.'.format(landPath))
    if os.path.exists(iniPath):
        lines = readfile(iniPath)
        if len(lines) > 1:
            version = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
            print('len lines',len(lines))
            print ('lines', lines)
            sys.exit('Stop:  does not exist or cannot be parsed')
        zipName = '{}.v{}.7z'.format(land.replace(' ','_'),version) #no zips will have spaces, but landscapes folders might
        zipPathTemp = '{}\\{}'.format(mainDir,zipName)
        zipPath = '{}\\{}'.format(zipDir,zipName) #no zips will have spaces, but landscapes folders might
        count = 0
        if zipPath not in allZips:
            print()
            print('----------------------------------------------------------')
            print(zipPath,)
            try:
                #create new zip
                landZip = zipPath.split('.')[0].split('\\')[-1]
                print ('***Creating {}***'.format(zipName))
                sevenzip(zipPathTemp,landPath)
                print('Moving to zip directory')
                try:
                    os.system('move {} {}'.format(zipPathTemp,zipPath))
                    newZipped.append(zipPath)
                    count += 1
                except:
                    sys.exit('Stop.  Problem with moving file')
            except:
                print ('Error creating {}'.format(zipPath))
    else:
        print ('lines', lines)
        print('Warning: .ini file does not exist for {}'.format(landPath))
if len(newZipped) == 0:
    print ('No new landscapes to zip')
# time.sleep(60)

# run createTorrents on skylinesC server
if not debugMode:
    runCreateTorrents(newZipped)

# fill up SSDdir and remove original files in zipDir
if populateSSD:
    for landZip in popular:
        if landZip not in zipsOnSSD:
            try:
                zipPath = os.path.join(zipDir,landZip)
                ssdPath = os.path.join(ssdDir, landZip)
                print('Copying {} to {}'.format(zipPath, ssdPath))
                shutil.copy(zipPath, ssdPath)
                if os.path.getsize(zipPath) != os.path.getsize(ssdPath):
                    sys.exit('Stop: file sizes on zipDir and ssdDir were not equal after copy: {}'.format(landZip))
                print('Done: {}'.format(landZip))
            except:
                print("Can't copy {} to {}".format(zipPath, ssdPath))
                print('Break')
                break
#get new ssdDrive list
zipsOnSSD = getSSDdriveList(ssdDir)
#remove zip files on zipDir that are on ssdDir:
for landZip in zipsOnSSD:
    zipPath = os.path.join(zipDir, landZip)
    ssdPath = os.path.join(ssdDir, landZip)
    if os.path.exists(zipPath):
        try:
            if os.path.getsize(zipPath) == os.path.getsize(ssdPath):
                os.remove(zipPath)
            else:
                print("Didn't remove {} because sizes don't match".format(zipPath) )
        except Exception as error:
            print('Error in removing {}: {}'.format(zipPath,error))
### Create symlinks for newly copied
linktoSSDdrive(zipDir,ssdDir,popular,zipsOnSSD)

print ("Done")
