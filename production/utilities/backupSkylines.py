
from __future__ import print_function
import os, sys, datetime, re, shutil
from datetime import timedelta
import time as t
import tarfile
from shutil import copy2
sys.path.append('/media/sf_shared_VMs/common_py')
import subprocess


"""

This loops in a terminal and saves a compressed backed to a shared folder and gdrive (goltlabs), 
which keeps the latest db dump and others up to nkeepDaily,nKeepWeekly,nKeepYearly past versions.
It saves a text backup to gitBUdir each day, which is committed and pushed. Each dir keeps all the htdocs incremental tars. 
"""

def sortByKey(list,mykey,order):
    if order == 'ascending':
        list.sort(key=lambda item: item[mykey])
    else:
        list.sort(key=lambda item: item[mykey], reverse=True)
    return list

def sortDumps(dumps):
    daily = []
    weekly = []
    monthly = []
    yearly = []
    for dump in dumps:
        if '_D' in dump['path']:
           daily.append(dump)
        elif '_W' in dump['path']:
            weekly.append(dump)
        elif '_M' in dump['path']:
            monthly.append(dump)
        elif '_Y' in dump['path']:
            yearly.append(dump)
    groups = [daily, weekly,monthly,yearly]
    sortedGroups = [sortByKey(group,'created','descending') for group in groups] #newest dump first in each group
    return sortedGroups

def dump(dir,dbName,dumpExtension):
    dumpName = '{}.{}'.format(dumpBaseName,dumpExtension)
    tempDumpName = dumpName + '.temp'
    tempDumpPath = os.path.join(dir,tempDumpName)
    dumpCmd = ['sudo','-u','bret','pg_dump','--exclude-table-data=elevations','--format={}'.format(dumpExtension),dbName]
    f = open(tempDumpPath,'w')
    status = subprocess.call(dumpCmd, stdout=f)
    if status != 0: print('Error creating db dump')
    f.close()
    return tempDumpPath

def getDumpsInfo(buDir):
    items = os.listdir(buDir)
    dumps = []
    for item in items:
        if 'dump' in item and not '.temp' in item and dumpExtension in item and os.path.isfile(os.path.join(buDir,item)):
            # try:
                dump = {}
                dump['path'] = os.path.join(buDir,item)
                try:
                    dumpTimeStamp = item.split('_')[1][:19]
                except:
                    xx=0
                dump['created'] = datetime.datetime.strptime(dumpTimeStamp, format(timeFormat))
                dump['delete'] = False
                size = None
                try:
                    size = os.stat(dump['path']).st_size
                    # print('\ttest', item, size
                except:
                    print('\tNo size found for',dump['path'])
                dump['size'] = size
                dumps.append(dump) # print('\t{:.2f} MB, {}'.format(size / float(10 ** 6), item)
            # except:
            #     print('\tError getting info for ',dump['path'])
    return dumps

def advance(path):
    if '_D' in path:
         return path.replace('_D','_W')
    elif '_W' in path:
        return path.replace('_W','_M')
    elif '_M' in path:
       return path.replace('_M','_Y')
    elif '_Y' in path:
        sys.exit("Stop: no tag older than 'Y':", path)
    else:
        sys.exit("Stop: can't advance", path)

def moveFile(path1,path2):
    try:
        shutil.move(path1,path2)
        print('\t\tMoved {} to {}'.format(path1,path2))
    except:
        print('\tError in moving file {} to {}'.format(path1,path2))

def deleteFile(path):
    try:
        os.remove(path)
        print('\t\tDeleted', path)
    except:
        print('\tError in deleting file',path)

def deleteMarked(dumpGroups):
    for group in dumpGroups:
        for dump in group:
            if dump['delete'] == True:
                deleteFile(dump['path'])

def pruneDumps(dumps, nkeep):
    periods = [timedelta(days=7), timedelta(days=7), timedelta(days=30), timedelta(days=365)]
    tags = ['D','W','M','Y']
    dumpGroups = sortDumps(dumps)
    for ig,group in enumerate(dumpGroups):
        tag = tags[ig]
        if tag == 'Y':
            break # keep all yearly backups...nothing to advance to
        if len(group) <= nkeep[tag]:
            continue
        oldest = dumpGroups[ig][-1]
        nextGroupNewest = dumpGroups[ig+1][0]
        if oldest['created'] >= nextGroupNewest['created'] + periods[ig+1]:
            moveFile(oldest['path'], advance(oldest['path']))
        else:
            dumpGroups[ig][-1]['delete'] = True
        for id in range(len(dumpGroups[ig]) - 1):
            if id <= nkeep[tag]:
                continue
            else:
                dumpGroups[ig][id]['delete'] = True

    deleteMarked(dumpGroups)

###############################################################
nkeep = {'D': 7, 'W': 4, 'M': 12} #, 'Y': 10000}
loopTime = 1 #days
basePath = '/home/bret/'
htdocsSource = os.path.join(basePath,'skylinesC','htdocs','files')
dumpBaseName = 'skylinesdump'

sf_backup = '/media/sf_backup' #on shared folder
# sf_backup = '/home/bret/Downloads/test'
htdocsSFbu = os.path.join(sf_backup, 'htdocs')
if not os.path.exists(htdocsSFbu): os.mkdir(htdocsSFbu)
dbName = 'skylines'
dumpExtension = 'custom' # compression of about 3
timeFormat = '%Y-%m-%d.%H.%M.%S'

debug = False
loop = True
while loop:
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
        print('Binary backup to {}'.format(sf_backup))
        tempDumpPath = dump(sf_backup,dbName,dumpExtension)
        datedSFdumpPath =  os.path.join(sf_backup,'{}_{}_D.{}'.format(dumpBaseName, nowStr, dumpExtension))
        status = subprocess.call(['mv',tempDumpPath,datedSFdumpPath])
        if status != 0:
            sys.exist('Error adding date to dump', tempDumpPath, datedSFdumpPath)
        dumpSize = os.stat(datedSFdumpPath).st_size
        print( '\t{:.2f} MB, {}'.format(dumpSize / float(10 ** 6), datedSFdumpPath))
    dumps = getDumpsInfo(sf_backup)
    pruneDumps(dumps,nkeep)

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
    # Add igcs to daily tar file
    tarName = 'htdocs_{}-backto-{}.tar.gz.temp'.format(nowStr, latestTime.strftime(timeFormat))
    tempTarPath = os.path.join(htdocsSFbu,tarName)
    htdocsTar = tarfile.open(tempTarPath, mode='w:gz')
    items = os.listdir(htdocsSource)
    count = 0
    for item in items:
        modTime = datetime.datetime.fromtimestamp(os.path.getmtime('{}/{}'.format(htdocsSource,item)))
        if modTime > latestTime:
            htdocsTar.add(os.path.join(htdocsSource,item))
            count += 1
            print('\t',count, end='\r')
        else:
            xx=0
    print('')
    htdocsTar.close()
    if count > 0:
        finishedTarPath = tempTarPath.replace('.temp', '')
        moveFile(tempTarPath,finishedTarPath)
        tarSize = os.stat(finishedTarPath).st_size
        print( '\t{} new files {:.2f} MB, {}'.format(count,tarSize / float(10 ** 6), finishedTarPath))
        newTar = True
    else:
        os.remove(tempTarPath)
        print('\tNo new htdocs files')

    #ufw maintenance:
    # rules
    # os.system('sudo ufw enable > /dev/null 2>&1')
    # os.system('sudo ufw deny 4200 > /dev/null 2>&1')
    # os.system('sudo ufw deny 80 > /dev/null 2>&1')
    # os.system('sudo ufw deny 22 > /dev/null 2>&1')
    # os.system('sudo ufw allow from 192.168.1.50 to any port 4200 > /dev/null 2>&1')
    # os.system('sudo ufw allow from 192.168.1.50 proto tcp to any port 22 > /dev/null 2>&1')
    if debug:
        print('Debug is on')
        break

    #find time until midnight
    secNextSave = ((24 * loopTime - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)

    #wait until 10 min after midnight.  Groupflights runs at midnight.
    print('\n--- sleeping ---\n')
    t.sleep(secNextSave + 10 * 60)
