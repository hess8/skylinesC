import os,subprocess
import platform
# import pathlib

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
    os.rename(oldname, newname)
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


