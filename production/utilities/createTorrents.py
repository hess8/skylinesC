#Notes on ***magnet links***, which are created in landscapes.py:
# npm install -g magnet-link
# magnet-link /home/bret/Downloads/AA2.v0.7.7z.torrent > magnet.txt

# Options for mktorrent:

# -a <url>[,<url>]* : specify the full announce URLs
#                     at least one is required
#                     additional -a adds backup trackers
# -c <comment>      : add a comment to the metainfo
# -d                : don't write the creation date
# -h                : show this help screen
# -l <n>            : set the piece length to 2^n bytes,
#                     default is 18, that is 2^18 = 256kb
# -n <name>         : set the name of the torrent,
#                     default is the basename of the target
# -o <filename>     : set the path and filename of the created file
#                     default is <name>.torrent
# -p                : set the private flag
# -s                : add source string embedded in infohash
# -v                : be verbose

import os, sys
from datetime import datetime

def extension(filepath):
    return os.path.splitext(filepath)[1]

def filename(filepath):
    return os.path.splitext(filepath)[0]

def createMagnet(zipped):
    try:
        os.system('magnet-link {}.torrent > {}.magnet'.format(zipped, zipped))
        print '{}.magnet created'.format(zipped)
    except:
        print 'Error in magnet link for {}'.format(zipped)

zipDir = '/media/sf_landscapes-zip'
einsteinWatchDir = zipDir + '/QBTwatchEinstein'
workDir = zipDir
os.chdir(workDir)

zipDirList = os.listdir(zipDir)
zippedForTorrent  = []
oldZipped = []



for item in zipDirList:
    if extension(item) == '.7z':
        zipPath = '{}/{}'.format(zipDir, item)
        torrPath = '{}/{}.torrent'.format(zipDir, item)
        magPath = '{}/{}.magnet'.format(zipDir, item)
        zipTime = os.path.getmtime(zipPath)
        if os.path.exists(torrPath):
            oldZipped.append(item)
            # check for missing magnets
            if not os.path.exists(magPath):
                createMagnet(item)
            # remove outdated torrents and magnets
            torrTime = os.path.getmtime(torrPath)
            if torrTime < zipTime:
                oldZipped.pop(-1)
                os.remove(torrPath)
                zippedForTorrent.append(item)
                continue
            elif os.path.exists(magPath):
                magTime = os.path.getmtime(magPath)
                if magTime < zipTime:
                    oldZipped.pop(-1)
                    os.remove(magPath)
                    zippedForTorrent.append(item)
                    continue
        else:
            zippedForTorrent.append(item)
    if extension(item) in ['.torrent', '.magnet'] and not os.path.exists(filename(item)): #missing .7z file
        os.remove(item)

created = []
#create torrents
tracker = 'http://tracker.opentrackr.org:1337/announcefile'
sizeExp = 21 # 2^21 bytes = 2MB
comment = 'skylinescondor.com'
for zipped in zippedForTorrent:
    webSeed = 'http://208.83.226.9:8080/{}'.format(zipped)
    try:
        os.system('mktorrent -a {} -l {} -c {} -w {} {}'.format(tracker,sizeExp,comment,webSeed,zipped))
        print '{}.torrent created'.format(zipped)
        created.append(zipped)
    except:
        print 'Error in torrent {}'.format(zipped)
    #create magnet link
    createMagnet(zipped)
    for dir in [einsteinWatchDir]:
        try:
            os.system ('cp {}.torrent {}'.format(zipped,dir))
            print('Copied {}.torrent to {}'.format(zipped,dir))
        except:
            sys.exit('Error copying {}.torrent to {}'.format(zipped,dir))
    # remove old version files with same landscape
    land = zipped.split('.')[0]
    for item in oldZipped:
        if item.split('.')[0] == land and land!='WestGermany3':
            zipVersion = '{}/{}'.format(zipDir,item)
            os.remove(zipVersion)
            print 'removed',zipVersion
            torrentVersion = '{}/{}.torrent'.format(zipDir,item)
            if os.path.exists(torrentVersion):
                os.remove(torrentVersion)
                print 'removed',torrentVersion
            magnetVersion = '{}/{}.magnet'.format(zipDir,item)
            if os.path.exists(magnetVersion):
                os.remove(magnetVersion)
                print 'removed',magnetVersion
#create all magnet links
makeAllMagnets = False #needed only occasionally
if makeAllMagnets:
    zipDirList = os.listdir(zipDir)
    torrents  = []
    for item in zipDirList:
        if item.split('.')[-1] == 'torrent':
            torrents.append(item)
    for torrent in torrents:
        try:
            os.system('magnet-link {} > {}.magnet'.format(torrent, torrent.replace('.torrent','')))
            print '{}.magnet created'.format(torrent.replace('.torrent',''))
        except:
            print 'Error in magnet link for {}'.format(torrent)

#run update for skylinesC page.
os.system('python /home/bret/servers/repo-skylinesC/skylinesC/production/utilities/landscapesPage.py')
print 'Updated landscapes.hbs'
#beep
print 'Done'
