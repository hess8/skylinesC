import shutil
import os, sys

from uzsubs import *
from landscapesPage import landscapesPage
from createTorrents import createTorrents


zipMain = '/mnt/P/landscapes-zip'
## Landscapes page ##
landPageDest = os.path.join(zipMain,'latestLandscapesPage', 'landscapes.hbs')
qbtorrentExeDir = os.path.join(zipMain,'qbt_exe')
slcFilesPath = '/home/bret/servers/repo-skylinesC/skylinesC/htdocs/files/' #only used if can get copying by guest control working again
qbtExeLocal = get_qbtExe(qbtorrentExeDir,slcFilesPath)
qbtExePath = get_qbtExe(qbtorrentExeDir,slcFilesPath)
landHBS = '/home/bret/servers/repo-skylinesC/skylinesC/ember/app/templates/landscapes.hbs'
slcVMname = 'U14 (SkylinesC server on Z) Current'
# landHBS = '/home/bret/servers/repo-skylinesC/landscapes.test.hbs'
## Torrents ##

trackerStr = "&tr=http://tracker.opentrackr.org:1337/announce"
watchDir = os.path.join(zipMain + '/qbtWatch')
makeAllMagnets = False  # needed only occasionally
createdTorr = createTorrents(zipMain, watchDir, makeAllMagnets)
landscapesPage(zipMain, landPageDest, landHBS, qbtExeLocal, slcFilesPath, slcVMname, trackerStr)
