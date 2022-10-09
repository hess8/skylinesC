# '''
# 1. run in windows (anaconda "conda activate bchenv") as ADMIN python d:\skylinesC\production\utilities\updateZipped.py
# 2. conda activate bchenv
# 3. SET PATH=%PATH%;"C:\Program Files\7-Zip"
# 4. confirmation that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
# link target eg C:\Users\Bret\AppData\Local\qBittorrent\logs\qbittorrent.log
#   sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.
#
# ssh access: make sure port 22 is open on U14.  Test ssh connection manually
# '''

import os,sys,shutil
# import py7zr
import winsound
import win32com.client
import paramiko
from subprocess import Popen, PIPE

def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def sevenzip(tempPath,landPath):
    os.system('7z a -t7z "{}" "{}"'.format(tempPath,landPath)) #quotes to handle spaces in windows file names
#     os.system('py7zr c "{}" "{}"'.format(tempPath,landPath))
#     with py7zr.SevenZipFile(tempPath, 'w') as archive:
#                     archive.writeall(landPath, 'base')  #This seems slow, but uses threads well

mainDir = 'Z:\\Condor\\Landscapes'
otherDir1 = 'E:\\landscapes_for_symlinks'  #py7zr does not follow symlinks
otherDir2 = 'F:\\landscapes_for_symlinks2'
iniOnlyDir1 = 'E:\\landscapes_ini_only'
iniOnlyDir2 = 'F:\\landscapes_ini_only2'
zipDir = 'S:\\Skylines-C\landscapes-zip'
slcServerIP = '192.168.1.50'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']

mainList0 = os.listdir(mainDir)

#remove extra files from ini_only dirs:
for dir in [iniOnlyDir1]:# iniOnlyDir2]:
    for landscape in os.listdir(dir):
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                print ('Removing all but .ini in {}'.format(landscape))
                break
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                if os.path.isdir(os.path.join(dir,landscape,item)):
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir,landscape,item)))
                else:
                    os.remove(os.path.join(dir,landscape,item))

#if folder (not symbolic link) in mainDir begins with "-", remove all but .ini files and move to iniOnlyDir1
for item in mainList0:
    if item[0] == '-':
        path = os.path.join(mainDir,item)
        for item2 in os.listdir(path):
            if not '.ini' in item2:
                if os.path.isdir(os.path.join(path,item2)):
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(path,item2)))
                else:
                    os.remove(os.path.join(path,item2))
        shutil.move(path,os.path.join(iniOnlyDir1,item.replace('-','')))
        print('Moved {} to {}'.format(path,iniOnlyDir1))

mainList = os.listdir(mainDir)

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []

#update symbolic links
#remove broken symbolic links
for item in mainList:
    if os.path.isdir('{}\\{}'.format(mainDir,item)) and not os.path.exists('{}\\{}\\{}.ini'.format(mainDir,item,item)):
        os.rmdir('{}\\{}'.format(mainDir,item))

for dir in [otherDir1, otherDir2,iniOnlyDir1,iniOnlyDir2]:
# for dir in [otherDir1, iniOnlyDir1]:
    for item in os.listdir(dir):
        if 'Kanta' in item:
            print()
        if os.path.isdir(os.path.join(dir,item)) and item not in mainList:
            print ('Updated symlink for {}.'.format(item))
            mainPath = '{}\\{}'.format(mainDir,item)
            otherPath = '{}\\{}'.format(dir,item)
            os.system('mklink /D "{}" "{}"'.format(mainPath,otherPath))
        elif item not in mainList:
            print ('not added', dir, item)
            print ('isdir', os.path.isdir(os.path.join(dir,item)))

#landscapes are all represented in mainDir now.
for item in os.listdir(mainDir):
    if os.path.isdir(item) and 'WestGermany3' not in item:
        allLands.append(item)
        allLandPaths.append('{}\\{}'.format(mainDir,item))

#zips
for item in os.listdir(zipDir):
    if item.split('.')[-1] =='7z':
        allZips.append('{}\{}'.format(zipDir,item))

#create zips
newZipped = []
for i, landPath, in enumerate(allLandPaths):
    land = allLands[i]
    files = os.listdir(landPath)
    for file in files:
        if '.ini' in file:
            iniFile = file
            break
    if not iniFile:
        sys.exit('Stop.  No .ini file for {}'.format(landPath))
    iniPath = '{}/{}.ini'.format(landPath,land)
    # if not os.path.exists(iniPath):
    #     sys.exit('Stop.  No .ini file for {}'.format(landPath))
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
                except:
                    sys.exit('Stop.  Problem with moving file')
            except:
                print ('Error creating {}'.format(zipPath))
    else:
        print ('lines', lines)
        sys.exit('Stop: .ini file does not exist for {}'.format(landPath))
if len(newZipped) == 0:
    print ('No new landscapes to zip')
# time.sleep(60)
winsound.PlaySound("SystemHand", winsound.SND_ALIAS)

# run createTorrents on skylinesC server
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
print ("Done")
