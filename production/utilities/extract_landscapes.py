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
from common import landscapesMap, keepC2, pathWinLin#, seven_extract_single_file
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

# from more_itertools import sort_together
allLands = []
allLandPaths = []
for topDir in landDirs:
    items = os.listdir(topDir)
    for item in items:
        itemPath = os.path.join(topDir, item)
        if not item in allLands and os.path.isdir(itemPath) and ( ('Textures' in os.listdir(itemPath) and 'Slovenia' not in item) #and 'WestGermany3' not in item
                    or versionUpdateTag in item ): # note: isdir is true for a link pointing to a dir
            allLands.append(item)
            allLandPaths.append(itemPath)
            cupFile = os.path.join(itemPath,item+'.cup')
            if not os.path.exists(cupFile) and 'Textures' in os.listdir(itemPath): #.cup file required for COTACO task converter
                os.system('echo "name,code,country,lat,lon,elev,style,rwdir,rwlen,freq,descr \n" > {}'.format(cupFile))
                print('created', cupFile)

# allLands, allLandPaths = sort_together([allLands, allLandPaths],reverse=args.reverse)

zips = os.listdir(zipMain)
zips_to_extract = []

for zip in zips:
    name = zip.split('.')[0]
    if zip.split('.')[-1] =='7z' and '_to' not in zip and 'WestGermany' not in zip:L
        zips_to_extract.append(zip)

source_tag = file.split('.')[0]
# flight = flight_from_string(source_tag)
# if not flight:
#     write_line_new(processed_file,source_tag)
#     logging.error(f'Flight None was returned by flight_from_string for {i},{file}')
#     continue
# elif source_tag not in processed:
#     zip_path = os.path.join(zip_dir, file)
#     igc_path = os.path.join(igc_dir, file.replace('.7z','.igc'))
#     if not os.path.exists(igc_path) or os.path.getsize(igc_path) == 0:
#         zip_path = igc_path.replace('/temp','').replace('.igc','.7z')
#         seven_extract_single_file(zip_path,igc_path)
# igc_path
