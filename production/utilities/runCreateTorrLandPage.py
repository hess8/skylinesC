import shutil
import os, sys

from uzsubs import getParams, get_qbtExe
from landscapesPage import landscapesPage
from createTorrents import createTorrents
'''Runs on linux'''

args = getParams()
# zipMain = '/mnt/P/landscapes-zip' #for Debian
zipMain = '/media/sf_landscapes-zip' #for U14
## Landscapes page ##
qbtExeLocalPath = os.path.join(zipMain,'qbt_exe')
qbtExeName = qbtExeLocalPath.split(os.sep)[-1]
qbtWebPath = os.path.join('/files',qbtExeName)
versions = ['C2','C3']
slcFilesPath = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/' #only used if can get copying by guest control working again
# landPageLocalDest = os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs') # Debian
landPageLocalDest =  '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs' # U14
landHBS = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
slcVMname = 'U14 (SkylinesC server) Current'
## Torrents ##

trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = os.path.join(zipMain + '/qbtWatch')
makeAllMagnets = False  # needed only occasionally
createdTorr = createTorrents(zipMain, watchDir, makeAllMagnets)
landscapesPage(zipMain,landPageLocalDest,qbtWebPath,trackerStr,versions,args)
