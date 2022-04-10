# '''run in windows cmd window as ADMIN
#         SET PATH=%PATH%;"C:\Program Files\7-Zip"
#         python d:\skylinesC\production\utilities\updateZipped.py
#         Writes to final destination
#   conda activate bchenv
#
#         '''

import os,sys,time
# import py7zr
import winsound
import paramiko

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
slcServerIP = '192.168.1.122'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell

#remove extra files from ini_only dirs:
for dir in [iniOnlyDir1,iniOnlyDir2]:
    for landscape in os.listdir(dir):
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                print ('Removing all but .ini in {}'.format(landscape))
                break
        for item in os.listdir(os.path.join(dir,landscape)):
            if not '.ini' in item:
                if os.path.isdir(os.path.join(dir,landscape,item)):
#                     shutil.rmtree(os.path.join(dir,landscape,item))
                    os.system('rmdir /S /Q "{}"'.format(os.path.join(dir,landscape,item)))
                else:
                    os.remove(os.path.join(dir,landscape,item))

# keepRunning = False
# while keepRunning: #loops infinitely
allLands = []
allLandPaths = []
allZips = []

#update symbolic links
mainList = os.listdir(mainDir)

for dir in [otherDir1, otherDir2,iniOnlyDir1,iniOnlyDir2]:
    for item in os.listdir(dir) :
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
    if 'WestGermany3' not in item:
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
    try:
        files = os.listdir(landPath)
        for file in files:
            if '.ini' in file:
                iniFile = file
                break
        if not iniFile:
            sys.exit('Stop0.  No .ini file for {}'.format(landPath))
    except: #it's probably a broken link from moving files from _for_symlinks to _ini_only
        print ('Removing broken link {}.  Run this program again'.format(landPath))
        os.rmdir(landPath)
# #         break
    iniPath = os.path.join(landPath,iniFile)
    if os.path.exists(iniPath):
        lines = readfile(iniPath)
        if len(lines) > 1:
            version = lines[1].split('=')[1].split('(')[0].split(',')[0].replace('00','0').replace('.10.','.1.').replace(' ','')
        else:
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
#                 tempPathZip = mainDir+'\\temp_{}.7z'.format(landZip)
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
        sys.exit('Stop2: ini.txt does not exist for {}'.format(landPath))
else:
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
        for line in stderr:
            print(line)

print ("Done")
