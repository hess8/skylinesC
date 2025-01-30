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
    '': '',
}

def winLinkAllDir(sourceDir,targetDir):
    '''puts links to every item in sourceDir in a windows targetDir
    Windows can follow these links more frequently than when sourceDir is linked'''
    print('Must run as Administrator to use winLinkAllDir')
    if not os.path.exists(targetDir):
       os.mkdir(targetDir)
    items = os.listdir(sourceDir)
    for item in items:
        if not os.path.exists(os.path.join(targetDir,item)):
            cmd = ['mklink', '/d', os.path.join(targetDir, item), os.path.join(sourceDir, item) ]
            # cmd = 'mklink /d C:\Condor2\Landscapes\Florida2 s:\E\landscapes\landscapesC2-main\Florida2'
            # os.system(cmd)
            print(cmd)
            try:
                proc = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,shell=True)
                output, error = proc.communicate()
                if proc.returncode != 0:
                    raise subprocess.CalledProcessError(proc.returncode, proc.args, output=output, stderr=error)
                lines = output.splitlines()
            except subprocess.CalledProcessError as e:
                print("Error output:", e.stderr)

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
    # try:
    #     os.rename(oldname, newname)
    #     print('Renamed {} to {}'.format(oldname, newname))
    # except:
    #     sys.exit("Stop: can't rename {} to {}".format(oldname, newname))
    shutil.move(oldname, newname)
    print('Renamed {} to {}'.format(oldname, newname))

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


