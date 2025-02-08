import os,subprocess
import platform
import shutil
# import pathlib

landscapesMap = {
    'AA2': 'AA3',
    'Arequipa_Peru':'Arequipa_Peru3',
    'Atacama_C2': 'Atacama3',
    'Cajamarca_Peru': 'Cajamarca_Peru3',
    'Centro_Italia': 'Centro_Italia3',
    'Coquimbo_SanJuan': 'CoquimboSanJuan3',
    'Cuzco_Peru': 'Cuzco_Peru3',
    'Husacaran': 'Huascaran_Peru3',
    'Lima_Peru': 'Lima_Peru3',
    'North-UK2': 'United Kingdom3',
    'Pumalin_Park': 'Pumalin_Park3',
    'Scotland3': 'United Kingdom3',
    'Scotland4': 'United Kingdom3',
    'Slovenia2': 'Slovenia3',
    'South East UK3': 'United Kingdom3',
    'Talca_Los_Andes': 'TalcaLosAndes3',
    'Temuco_Los_Andes': 'TemucoLosAndes3',
    'Transandino': 'Transandino3',
    'United Kingdom': 'United Kingdom3',
    'West_Balkans': 'West_Balkans3',
    'West_Balkans2': 'West_Balkans3',
    'West_Patgonia': 'West_Patagonia3',
    'West-UK': 'United Kingdom3',
    'West-UK2': 'United Kingdom3',
    'France Champagne': 'Fr_ChampagneC3',
    '': '',
}
def renameDirsWithTag(dirsList,tags,tagReplacement):
    for dir in dirsList:
        for tag in tags:
            if tag in dir:
                newName = dir.replace(tag,tagReplacement)
                renameTry(dir, newName)

def readfile(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines() #strips the lines of \n
    return lines

def readfileNoStrip(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines(True) #keeplinebreaks=True.  Does not strip the lines of \n
    return lines

def writefile(lines,filepath): #need to have \n's inserted already
    file1 = open(filepath,'w')
    file1.writelines(lines)
    file1.close()
    return

def renameTry(oldname, newname):
    shutil.move(oldname, newname)
    print('Renamed {} to {}'.format(oldname, newname))


def linkAllDir(realDir,linksDir):
    '''puts links to every item in realDir in a windows linksDir
    Windows can follow these links more frequently than when realDir is linked'''
    if platform.system() == 'Windows': print('Must run as Administrator to use linkAllDir')
    if not os.path.exists(linksDir):
       os.mkdir(linksDir)
    items = os.listdir(realDir)
    for item in items:
        if not os.path.exists(os.path.join(linksDir,item)):
            if platform.system() == 'Windows':
                cmd = ['mklink', '/d', os.path.join(linksDir, item), os.path.join(realDir, item) ]
            else:
                cmd = ['ln', '-s', os.path.join(realDir, item), os.path.join(linksDir, item)]
                print(cmd)
            subprocess.run(cmd)

def rmLinksDir(path,controlStrs):
    '''If mode is 'keep', removes all links that don't contain on the selected strings.
    Mode 'remove' Removes all links that do contain oneof the selected strings'''
    mode =  controlStrs[0] # 'keep' or 'remove'
    strs = controlStrs[1]
    for item in os.listdir(path):
        itemPath = os.path.join(path,item)
        if not os.path.islink(itemPath):
            continue
        for str in strs:
            if mode == 'keep' and str in strs:
                break
            elif mode == 'remove' and str in item:
                os.remove(itemPath)
                print('Removed symlink', itemPath)
                break
        else:
            if mode == 'keep':
                os.remove(itemPath)





def copy_file_to_guest(vm_name, host_file_path, guest_file_path,usernm,passwd):
    """Copies a file from host to guest using VBoxManage."""
    cmd = [
        "vboxmanage",
        "guestcontrol",
        vm_name,
        "copyto",
        host_file_path,
        guest_file_path,
        '--username={}'.format(usernm),
        '--password={}'.format(passwd)
    ]
    try:
        subprocess.check_output(cmd)
    except subprocess.CalledProcessError as e:
        print(e.output)

def listRunningVms():
    cmd = [
        "vboxmanage",
        "list",
        "runningvms"
    ]
    result = subprocess.check_output(cmd)
    outputLines = result.decode('utf-8').split('\n')
    return outputLines

def dirSize(path):
    # This suggestion is very slow: sum(f.stat().st_size for f in pathlib.Path(path).glob('**/*') if f.is_file())
    if platform.system() == 'Linux':
        size = subprocess.run(["du", "-s", path], stdout=subprocess.PIPE, text=True).stdout.split('\t')[0]
    else:
        size = 0
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    size += entry.stat().st_size
                elif entry.is_dir():
                    size += dirSize(entry.path)
    return size


