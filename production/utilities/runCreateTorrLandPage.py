import shutil
import os, sys

from uzsubs import copy_file_to_guest, getParams, get_qbtExe, readfile, pathWinLin, skylinesC_VM
from landscapesPage import landscapesPage
from createTorrents import createTorrents
'''Runs on linux'''

args = getParams()
zipMain = pathWinLin(os.path.join('P','shared_VMs','skylinesC-related','landscapes-zip'))
## Landscapes page ##
## Landscapes page ##
landPageLocalDest = pathWinLin(os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs'))
qbtExeLocalPath = get_qbtExe(pathWinLin(os.path.join(zipMain,'qbt_exe')))
convert_landscapesPath = pathWinLin(os.path.join('/home/bret/skylinesC/production/utilities/','Convert-Landscapes.ps1'))
convert_landscapesPath = pathWinLin(os.path.join('/home/bret/skylinesC/production/utilities/','Convert-Landscapes.ps1'))
slcPath = '/home/bret/skylinesC/'
slcFilesPath = os.path.join(slcPath, 'htdocs/files/')
landPageServerDest = os.path.join(slcPath,'ember/app/templates/landscapes.hbs')
qbtExeName = qbtExeLocalPath.split(os.sep)[-1]
qbtExeDest = os.path.join(slcFilesPath,qbtExeName)
qbtWebPath = os.path.join('/files',qbtExeName)
slcVMname = skylinesC_VM()
[username, passwd] = readfile('/home/bret/.local/secure/userU')
versions = ['C2','C3']

## Torrents ##
trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = os.path.join(zipMain + '/qbtWatch')
makeAllMagnets = False  # needed only occasionally
createdTorr = createTorrents(zipMain, watchDir, makeAllMagnets)
landscapesPage(zipMain,landPageLocalDest,qbtWebPath,trackerStr,versions,args)
