import shutil
import os, sys

from uzsubs import getParams
from landscapesPage import landscapesPage
from createTorrents import createTorrents

args = getParams()
# zipMain = '/mnt/P/landscapes-zip'
zipMain = '/media/sf_landscapes-zip'
## Landscapes page ##
landPageLocalDest = os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs')

slcFilesPath = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/' #only used if can get copying by guest control working again
qbtExeLocal = get_qbtExe(qbtorrentExeDir,slcFilesPath)
qbtExePath = get_qbtExe(qbtorrentExeDir,slcFilesPath)
landHBS = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
slcVMname = 'U14 (SkylinesC server) Current'
## Torrents ##

trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = os.path.join(zipMain + '/qbtWatch')
makeAllMagnets = False  # needed only occasionally
createdTorr = createTorrents(zipMain, watchDir, makeAllMagnets)
landscapesPagelandscapesPage(zipMain,landPageLocalDest,qbtWebPath,trackerStr,versions,args)
