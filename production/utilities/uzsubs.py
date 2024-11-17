import os,sys,shutil
import re

slcServerIP = '192.168.1.57'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519' #only shows up in PowerShell
qbtLogLinks = ['Einsteinqbittorrent.log.lnk','Sotoqbittorrent.log.lnk']

def sevenzip(tempPath,landPath): # 7z command is from an anaconda package...don't know the name
    os.system('7z a -t7z "{}" "{}"'.format(tempPath,landPath)) #quotes to handle spaces in windows file names
        #pyzr won't handle
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
        drive = dest.split(os.sep)[0]
        avail = get_free_space_gb(drive)
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

        itemMainPath = os.path.join(mainDir, mainItem)
        if not os.path.isdir(itemMainPath): continue
        if mainItem[0] == '!':
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
                        print(
                            "The .ini file name {} doesn't match {}.  Rename the landscape folder with the name of the .ini file"
                            .format(dirItem, mainItem))
                        renameTry(itemMainPath, os.path.join(mainDir,iniName))

                    except:
                        renameTry(itemMainPath, os.path.join(mainDir,'!_no_match_ini_' + iniName))
                break
        else:
            print('!_no .ini file found in full dir {}; adding "!no_ini_" to name'.format(itemMainPath))
            renameTry(itemMainPath,os.path.join(mainDir, "no_ini_" + mainItem))

def makeLink(linkDir, realDir):
    try:
        os.symlink(realDir, linkDir)
        # os.system('mklink "{}" "{}"'.format(, realDir))
    except:
        print('Problem creating symblolic link {} -> {}'.format(linkDir, realDir))

def renameTry(oldname, newname):
    try:
        os.rename(oldname, newname)
        print('Renamed {} to {}'.format(oldname, newname))
    except:
        sys.exit("Stop: can't rename {} to {}".format(oldname, newname))
