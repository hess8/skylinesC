"""
    Calls landscapes.py an
"""
import os,sys
# import py7zr #py7zr does not follow symlinks!
# import win32com.client

# sys.path.append('/mnt/D/common_py')
# sys.path.append('/mnt/P/shared_VMs/common_py')
# sys.path.append('/media/sf_shared_VMs/common_py')
# sys.path.append('/media/sf_shared_VMs/common_py')
sys.path.append('/home/bret/common_py')
from common import landscapesMap, keepC2, pathWinLin, seven_extract, subPopenTry
from uzsubs import *

desired_landscapes = keepC2
desired_landscapes += landscapesMap.keys()

versions = ['C2','C3']
versionUpdateTag = '_to_{}'.format(versions[1])
lowVMain = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
lowVExt1 = pathWinLin(os.path.join('A','landscapesC2')) # None
lowVini = pathWinLin(os.path.join('E','landscapes','landscapesC2-ini'))
lowVserver = pathWinLin(os.path.join('E','landscapes','landscapesC2-server'))
highVMain = pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))
highVExt1 = None #pathWinLin(os.path.join('E','landscapes','landscapesC3-main')
highVini = pathWinLin(os.path.join('E','landscapes','landscapesC3-ini'))
highVserver = pathWinLin(os.path.join('E','landscapes','landscapesC3-server'))
lowerVersionLandDirs = [lowVMain,lowVini,lowVserver]
higherVersionLandDirs = [highVMain,highVini,highVserver]
landVersionsLists = [lowerVersionLandDirs, higherVersionLandDirs]
versionMainDict = {'C2': lowVMain, 'C3': highVMain}
zipMain = pathWinLin(os.path.join('P','shared_VMs','skylinesC-related','landscapes-zip'))
# zipMain = pathWinLin(os.path.join(winPathStart,'A:','zips')
zipExtras = None #[pathWinLin(os.path.join('E','landscapes','zipped1']
zipDirs = [zipMain] #+ zipExtras
zipPathPrior = [zipMain] # [zipExtras[0],zipMain] # fill up in this order
utilitiesDir = pathWinLin(os.path.join('L','condor-related','skylinesC','production','utilities'))

landDirs = [lowVMain, highVMain]
# landDirs = [lowVMain]

keepC2_spaces = [x.replace('_', ' ') for x in keepC2]

# from more_itertools import sort_together
allLands = []
allLandPaths = []
for topDir in [lowVMain]:
    items = os.listdir(topDir)
    for item in items:
        itemPath = os.path.join(topDir, item)
        item_spaces = item.replace('_',' ')
        if item_spaces not in allLands and os.path.isdir(itemPath): # note: isdir is true for a link pointing to a dir
            allLands.append(item.replace('_', ' '))
            allLandPaths.append(itemPath)

zips = os.listdir(zipMain)
zips_to_extract = []

for zip in zips:
    name_spaces = zip.split('.')[0].replace('_',' ')
    if name_spaces not in allLands and name_spaces in keepC2_spaces and zip.split('.')[-1] =='7z' and '_to' not in zip and 'WestGermany' not in zip:
        zips_to_extract.append(zip)

for zip in zips_to_extract:
    zip_path = os.path.join(zipMain, zip)
    destination = zip_path.replace(zipMain, lowVMain).replace('.7z',' ')
    print(zip)
    seven_extract(zip_path,destination)
    cmd = f'mv {destination}/* {lowVMain}'.split(' ')
    subPopenTry(cmd)
    sys.exit('stop')

