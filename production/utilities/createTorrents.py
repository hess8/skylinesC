def createTorrents(zipDir, watchDir,makeAllMagnets):
    '''Called by updateZipped.py
    mktorrent can be installed in PyCharm interpreter settings

    magnet-link: npm install -g magnet-link.   On Windows install nodejs first

    Notes on ***magnet links***, which are created in landscapes.py:
    npm install -g magnet-link
    magnet-link /home/bret/Downloads/AA2.v0.7.7z.torrent > magnet.txt

    Options for mktorrent:

    -a <url>[,<url>]* : specify the full announce URLs
                        at least one is required
                        additional -a adds backup trackers
    -c <comment>      : add a comment to the metainfo
    -d                : don't write the creation date
    -h                : show this help screen
    -l <n>            : set the piece length to 2^n bytes,
                        default is 18, that is 2^18 = 256kb
    -n <name>         : set the name of the torrent,
                        default is the basename of the target
    -o <filename>     : set the path and filename of the created file
                        default is <name>.torrent
    -p                : set the private flag
    -s                : add source string embedded in infohash
    -v                : be verbose
'''
    import os, sys

    def extension(filepath):
        return os.path.splitext(filepath)[1]

    def filename(filepath):
        return os.path.splitext(filepath)[0]

    def createMagnet(zipped):
        try:
            os.system('magnet-link {}.torrent > {}.magnet'.format(zipped, zipped))
            print('{}.magnet created'.format(zipped))
        except:
            print('Error while creating magnet link for {}'.format(zipped))


    workDir = zipDir
    os.chdir(workDir)

    zipDirList = sorted(os.listdir(zipDir))
    torrentsList = []
    toMakeTorrent  = []
    toMakeMagnet = []

    for item in zipDirList:
        if extension(item) == '.7z':
            zipPath = os.path.join(zipDir, item)
            torrPath = zipPath + '.torrent'
            magPath = zipPath + '.magnet'
            zipTime = os.path.getmtime(zipPath)
            # Check for outdated torrent
            if os.path.exists(torrPath):
                torrTime = os.path.getmtime(torrPath)
                if torrTime < zipTime or os.stat(torrPath).st_size == 0:
                    os.remove(torrPath)
                    toMakeTorrent.append(zipPath)
                else:
                    torrentsList.append(torrPath)
                    if not os.path.exists(magPath):
                        toMakeMagnet.append(zipPath)
            else:
                toMakeTorrent.append(zipPath)
            # check for outdated magnet
            if makeAllMagnets and not zipPath not in toMakeMagnet:
                toMakeMagnet.append(zipPath)
            elif os.path.exists(magPath):
                magTime = os.path.getmtime(magPath)
                if magTime < zipTime or os.stat(magPath).st_size == 0:
                    print(magTime < zipTime ,os.stat(magPath).st_size == 0)
                    os.remove(magPath)
                    toMakeMagnet.append(zipPath)
        # Check for missing .7z file
        elif extension(item) in ['.torrent', '.magnet']:
            if not os.path.exists(os.path.join(zipDir,item.replace(extension(item), ''))):
                print('remove', os.path.join(zipDir,item))
                os.remove(os.path.join(zipDir,item))

    createdTorr = []
    #create torrents
    tracker = 'http://tracker.opentrackr.org:1337/announcefile'
    sizeExp = 21 # 2^21 bytes = 2MB
    comment = 'skylinescondor.com'
    #make new torrents
    for zippedPath in toMakeTorrent:
        webSeed = 'http://208.83.226.9:8080/{}'.format(zippedPath)
        try:
            print(zippedPath)
            os.system('mktorrent -a {} -l {} -c {} -w {} {}'.format(tracker,sizeExp,comment,webSeed,zippedPath))
            print('{}.torrent created'.format(zippedPath))
            createdTorr.append(toMakeTorrent)
            toMakeMagnet.append(zipPath)
        except:
            sys.exit('Stop.Error in torrent {}'.format(zippedPath))
        try:
            os.system ('cp {}.torrent {}'.format(zippedPath,watchDir))
            print('Copied {}.torrent to {}'.format(zippedPath,watchDir))
        except:
            sys.exit('Error copying {}.torrent to {}'.format(zippedPath,watchDir))
        # remove old version files for same landscape
        land = zippedPath.split('.')[0]
        for item in zipDirList:
            if item.split('.')[0] == land and land!='WestGermany3':
                zipVersion = '{}/{}'.format(zipDir,item)
                os.remove(zipVersion)
                print('removed',zipVersion)
                torrentVersion = '{}/{}.torrent'.format(zipDir,item)
                if os.path.exists(torrentVersion):
                    os.remove(torrentVersion)
                    print('removed',torrentVersion)
                magnetVersion = '{}/{}.magnet'.format(zipDir,item)
                if os.path.exists(magnetVersion):
                    os.remove(magnetVersion)
                    print('removed',magnetVersion)
    # make new magnets
    for magPath in toMakeMagnet:
        createMagnet(magPath)
    # print('Torrents done')
    return createdTorr

