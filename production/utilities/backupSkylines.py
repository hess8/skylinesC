
from __future__ import print_function
import os, sys, datetime, time, re
import time as t
# import paramiko
import tarfile
from shutil import copy2
sys.path.append('/media/sf_shared_VMs/common_py')
import subprocess


"""

This loops in a terminal and saves a compressed backed to a shared folder and gdrive (goltlabs), 
which keeps the latest db dump and others up to nkeepDaily,nKeepWeekly,nKeepYearly past versions.
It saves a text backup to gitBUdir each day, which is committed and pushed. Each dir keeps all the htdocs incremental tars. 
"""
def sortDumps(dumps):
    daily = []
    weekly = []
    monthly = []
    yearly = []
    files = os.listdir(dir)
    for dump in dumps:
        if '_D' in dump['filename']:
           daily.append(dump)
        elif '_W' in filename:
            weekly.append(dump)
        elif '_M' in filename:
            monthly.append(dump)
        elif '_Y' in filename:
            yearly.append(dump)
    return daily, weekly, monthly, yearly


def dump(dir,dbName,dumpType):
    dumpName = '{}.{}'.format(dumpBaseName,dumpType)
    tempDumpName = dumpName + '.temp'
    tempDumpPath = os.path.join(dir,tempDumpName)
    dumpCmd = ['sudo','-u','bret','pg_dump','--exclude-table-data=elevations','--format={}'.format(dumpType),dbName]
    f = open(tempDumpPath,'w')
    status = subprocess.call(dumpCmd, stdout=f)
    if status != 0: print('Error creating db dump')
    f.close()
    finishedDumpPath = tempDumpPath.replace('.temp', '')
    status = subprocess.call(['mv',tempDumpPath,finishedDumpPath])
    if status != 0: print('Error removing .temp tag')
    dumpSize = os.stat(finishedDumpPath).st_size
    print( '\t{:.2f} MB, {}'.format(dumpSize / float(10 ** 6), finishedDumpPath))
    return finishedDumpPath

def advanceTag(filename):
    if '_D' in filename:
        return filename.replace('_D','_W')
    elif '_W' in filename:
        return filename.replace('_W','_M')
    elif '_M' in filename:
       return filename.replace('_M','_Y')
    elif '_Y' in filename:
        sys.exit("Stop: no tag older than 'Y':", filename)
    else:
        sys.exit("Stop: can't advance", filename)

def getDumpsInfo(buDir):
    items = os.listdir(buDir)
    dumps = []
    for item in items:
        if 'dump' in item and dumpType in item and os.path.isfile(os.path.join(buDir,item)):
            try:
                dump = {}
                dump['name'] = item
                dumpTimeStamp = item.split('_')[1].replace('.custom','')
                dump['created'] = datetime.datetime.strptime(dumpTimeStamp, format(timeFormat))
                dump['delete'] = False
                size = None
                try:
                    size = os.stat(os.path.join(buDir, item)).st_size
                    # print('\ttest', item, size
                except:
                    print('\tNo size found for',item)
                dump['size'] = size
                dumps.append(dump) # print('\t{:.2f} MB, {}'.format(size / float(10 ** 6), item)
            except:
                print('\tError getting info for ',filename)
    return dumps

def pruneDumps(dumps):
    if len(dumps) > 0:
        dumps = sorted(dumps, key=lambda x: x['created']) #oldest first
        #advance oldest
        oldestDump = dumpsInfo[-1]
        while len(dumpsInfo) > nkeepDaily and oldestDump[2] <= dumpsInfo[0][2]: #Delete oldest if newest is larger or same size
            try: #delete oldest
                os.remove(os.path.join(buDir,oldestDump[0]))
                print('\t\tDeleted', oldestDump[0])
                dumpsInfo.pop()
                oldestDump = dumpsInfo[-1]
            except:
                print('\tError in deleting oldest dump',oldestDump)
    return dumps
###############################################################
loopTime = 1 #days
basePath = '/home/bret/'
# backupRepoName = 'backup-skylinesC'  #not using git for now because LFS backup saved much too much data and cost $ for bandwidth
# gitBUdir = os.path.join(basePath, backupRepoName)
htdocsSource = os.path.join(basePath,'skylinesC','htdocs','files')
dumpBaseName = 'skylinesdump'

# htdocsGitDir = os.path.join(gitBUdir, 'htdocs')
sf_backup = '/media/sf_backup' #on shared folder
htdocsSFbu = os.path.join(sf_backup, 'htdocs')
if not os.path.exists(htdocsSFbu): os.mkdir(htdocsSFbu)
# if not os.path.exists(htdocsGitDir): os.mkdir(htdocsGitDir)
dbName = 'skylines'
# gitDumpType = 'plain' # git can version text files.
dumpType = 'custom' # compression of about 3

#nkeepGitBU = 1
nkeepDaily = 5
nkeepWeekly = 5
nkeepMonthly = 5
nkeepYearly = 5
timeFormat = '%Y-%m-%d.%H.%M.%S'

debug = False
while not debug:
    newDump = False
    newTar = False
    now = datetime.datetime.now()
    nowStr = now.strftime(timeFormat)
    print
    print(now.strftime(timeFormat))
    #### Database backup #####
    doDump = True  # debugging switch
    dumpSize = 0
    if not doDump: #debugging switch, when working on tar section below
        print("Warning: Skipping db backup!")
    else:
        # print('Text backup for {}'.format(gitBUdir))
        # gitDumpPath = dump(gitBUdir,dbName,gitDumpType)
        print('Binary backup for {}'.format(sf_backup))
        sfDumpPath = dump(sf_backup,dbName,dumpType)
        #list = finishedDumpPath.split('.')
        #datedGitDumpPath =  '{}_{}.{}'.format(list[0], nowStr, list[1])
        #copy2(finishedDumpPath, datedGitDumpPath) #same folder as original (gitBU).  Keep date-tagged dump backups up to nkeepDaily, but don't commit them
        datedSFdumpPath =  os.path.join(sf_backup,'{}_D_{}.{}'.format(dumpBaseName, nowStr, dumpType))
        # if not os.path.exists(datedSFdumpPath):
        copy2(sfDumpPath, datedSFdumpPath)
    dumps = getDumpsInfo(sf_backup)
    daily, weekly, monthly, yearly = sortDumps(dumps)
    pruneDumps(dumps)


        ## git
        # commitStr = '"Latest db dump"'
        # cmd = ['git', '-C', gitBUdir, 'commit', '-am', commitStr]
        # status = subprocess.call(cmd)
        # if status != 0: print('Error git commit')
        # newDump = True
#    dumpsDelOld(gitBUdir, nkeepGitBU)

    #### htdocs backup #####:
    # Read date of last htdocs tar file

    #find latest htdocs backup
    try:
        htdocsBUfiles = os.listdir(htdocsSFbu)
    except:
        print('\tError in reading htdocs tars from shared folder')
    tars = []
    tarTimes = []
    tarSizes = []
    for filename in htdocsBUfiles:
        if 'tar' in filename:
            try:
                match = re.search('htdocs_(.*)-backto-.*.tar.gz', filename)
                if match:
                    tars.append(filename)
                tarTimeStamp = match.group(1)
                size = os.stat(os.path.join(htdocsSFbu,filename)).st_size
                tarSizes.append(size)
                tarTimes.append(datetime.datetime.strptime(tarTimeStamp, format(timeFormat)))
            except:
                'error getting tar file properties:', filename

    allInfo = zip(tarTimes,tars,tarSizes)
    tarsInfo =  [[tar,timeFile,size] for timeFile,tar,size in sorted(allInfo,reverse=True)]
    for i in range(len(tarsInfo)):
        file = tarsInfo[i][0]
        size = tarsInfo[i][2]
        #print('/t{:.2f} MB, {}'.format(size / float(10 ** 6), file)
    if len(tarsInfo) > 0:
        latestTar = tarsInfo[0]
        latestTime = latestTar[1]
    else:
        latestTar = None
        latestTime = datetime.datetime.strptime('2000-1-1.0.0.0', format(timeFormat))

    Are we adding to htdocs tar file or creating one for each day?

    # Add igcs to tar file
    # print("Compressing igc files"
    tarName = 'htdocs_{}-backto-{}.tar.gz.temp'.format(nowStr, latestTime.strftime(timeFormat))
    tempTarPath = os.path.join(htdocsGitDir,tarName)
    htdocsTar = tarfile.open(tempTarPath, mode='w:gz')
    items = os.listdir(htdocsSource)
    count = 0
    for item in items:
        modTime = datetime.datetime.fromtimestamp(os.path.getmtime('{}/{}'.format(htdocsSource,item)))
        if modTime > latestTime:
            # try:
            htdocsTar.add(os.path.join(htdocsSource,item))
            count += 1
            print('\t',count, end='\r')
    print('')
    htdocsTar.close()
    if count > 0:
        finishedTarPath = tempTarPath.replace('.temp', '')
        status = subprocess.call(['mv',tempTarPath,finishedTarPath])
        if status != 0: print('Error removing .temp tag')
        tarSize = os.stat(finishedTarPath).st_size
        print( '\t{:.2f} MB, {}'.format(tarSize / float(10 ** 6), finishedTarPath))
        if not os.path.exists(finishedTarPath.replace(gitBUdir,sf_backup)):
            copy2(finishedTarPath, htdocsSFbu)
        addCmd =  ['git','-C', gitBUdir, 'add', htdocsGitDir] #all htdocs tars
        status = subprocess.call(addCmd)
        if status != 0: print('Error git add htdocs backup dir')
        commitStr = '"New backup {}.{}"'.format(dumpBaseName, gitDumpType)
        cmd = ['git', '-C', gitBUdir, 'commit', '-am', commitStr]
        status = subprocess.call(cmd)
        if status != 0: print('Error git commit')
        newTar = True
    else:
        os.remove(tempTarPath)
        print('\tNo new htdocs files')

    print
    #commit the latest backup and the new htdocs tars  if any
    if newDump or newTar:
        cmd = ['git', '-C', gitBUdir, 'push']
        status = subprocess.call(cmd)
        if status != 0: print('Error git push')

    #ufw maintenance:
    # rules
    # os.system('sudo ufw enable > /dev/null 2>&1')
    # os.system('sudo ufw deny 4200 > /dev/null 2>&1')
    # os.system('sudo ufw deny 80 > /dev/null 2>&1')
    # os.system('sudo ufw deny 22 > /dev/null 2>&1')
    # os.system('sudo ufw allow from 192.168.1.50 to any port 4200 > /dev/null 2>&1')
    # os.system('sudo ufw allow from 192.168.1.50 proto tcp to any port 22 > /dev/null 2>&1')

    #find time until midnight
    secNextSave = ((24 * loopTime - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)

    #wait until 10 min after midnight.  Groupflights runs at midnight.
    print('\n--- sleeping ---\n')
    t.sleep(secNextSave + 10 * 60)
