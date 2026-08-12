"""
    Calls landscapes.py and createTorrents.py if on Linux

    loop
    1. checks links and folder size
    2. creates new zips for folders that are static
    3. creates new links
    4. runs createTorrents.py
    5. runs landscapesPage.py
    6. can confirm (not enabled) that qBitTorrent has the new torrent is read from qbittorrent.log links in landscapes-qip.
    link target eg C:\\Users\\Bret\\AppData\\Local\\qBittorrent\\logs\\qbittorrent.log

      sample line:  (N) 2022-04-03T19:07:50 - 'Falkland_Islands.v1.0.7z' added to download list.

    Add "-" to the beginning of the landscape dir name to remove all but .ini files and move to lowVini
    Add "." to the beginning of the landscape dir name to move landscape to symlink directory,

    landscapes.py writes the new page locally so we need to make this symbolic link on the skylinesC server:
"""
import os,sys
# import py7zr #py7zr does not follow symlinks!
# import win32com.client

sys.path.append('/mnt/D/common_py')
sys.path.append('/mnt/P/shared_VMs/common_py')
sys.path.append('/media/sf_shared_VMs/common_py')

from common import landscapesMap, keepC2, pathWinLin
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
for topDir in landDirs:
    items = os.listdir(topDir)
    for item in items:
        itemPath = os.path.join(topDir, item)
        item_spaces = item.replace('_',' ')
        if item_spaces in keepC2_spaces and item_spaces not in allLands and os.path.isdir(itemPath) and ( ('Textures' in os.listdir(itemPath) and 'Slovenia' not in item) #and 'WestGermany3' not in item
                    or versionUpdateTag in item ): # note: isdir is true for a link pointing to a dir
            allLands.append(item.replace('_', ' '))
            allLandPaths.append(itemPath)
            cupFile = os.path.join(itemPath,item+'.cup')
            if not os.path.exists(cupFile) and 'Textures' in os.listdir(itemPath): #.cup file required for COTACO task converter
                os.system('echo "name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,descr \n" > {}'.format(cupFile))
                print('created', cupFile)





files = os.listdir(zipMain)
files.sort()
zips_to_extract = []

# for file in files:
#     if file in
#
# for i,file in enumerate(files):
#     if np.mod(i,100) == 0:
#         print('\r', f'{i} of {len(files) - len(processed)} adding/checking tracks')
#     if '.7z' not in file: continue
#
#     source_tag = file.split('.')[0]
#     flight = flight_from_string(source_tag)
#     if not flight:
#         write_line_new(processed_file,source_tag)
#         logging.error(f'Flight None was returned by flight_from_string for {i},{file}')
#         continue
#     elif source_tag not in processed:
#         zip_path = os.path.join(zip_dir, file)
#         igc_path = os.path.join(igc_dir, file.replace('.7z','.igc'))
#         if not os.path.exists(igc_path) or os.path.getsize(igc_path) == 0:
#             zip_path = igc_path.replace('/temp','').replace('.igc','.7z')
#             seven_extract_single_file(zip_path,igc_path)
