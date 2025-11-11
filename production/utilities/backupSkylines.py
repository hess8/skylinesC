
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
    for dump in dumps:
        if '_D' in dump['filename']:
           daily.append(dump)
        elif '_W' in filename:
            weekly.append(dump)
        elif '_M' in filename:
            monthly.append(dump)
        elif '_Y' in filename:
            yearly.append(dump)
    groups = [daily,weekly,monthly,yearly]
    groups = [[sorted(dump, key=lambda dump: dump['created']) for dump in group] for group in groups] #oldest dump appears first in group
    return groups #oldest firstdaily, weekly, monthly, yearly]

def dump(dir,dbName,dumpExtension):
    dumpName = '{}.{}'.format(dumpBaseName,dumpExtension)
    tempDumpName = dumpName + '.temp'
    tempDumpPath = os.path.join(dir,tempDumpName)
    dumpCmd = ['sudo','-u','bret','pg_dump','--exclude-table-data=elevations','--format={}'.format(dumpExtension),dbName]
    f = open(tempDumpPath,'w')
    status = subprocess.call(dumpCmd, stdout=f)
    if status != 0: print('Error creating db dump')
    f.close()
    finishedDumpPath = tempDumpPath.replace('{}.temp'.format(dumpExtension), '_D.{}'.format(dumpExtension))
    status = subprocess.call(['mv',tempDumpPath,finishedDumpPath])
    if status != 0: print('Error removing .temp tag')
    dumpSize = os.stat(finishedDumpPath).st_size
    print( '\t{:.2f} MB, {}'.format(dumpSize / float(10 ** 6), finishedDumpPath))
    return finishedDumpPath

def advanceTagPath(dump):
    path = dump['path']
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

def getDumpsInfo(buDir):
    items = os.listdir(buDir)
    dumps = []
    for item in items:
        if 'dump' in item and dumpExtension in item and os.path.isfile(os.path.join(buDir,item)):
            try:
                dump = {}
                dump['path'] = os.path.abspath(item)
                dumpTimeStamp = item.split('_')[1].replace('.custom','')
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
            except:
                print('\tError getting info for ',dump['path'])
    return dumps

def pruneDumps(dumps, nkeep):
    #period = {'W': 7, 'M': 30, 'Y': 365}
    period = {'W': 2, 'M': 3, 'Y': 4}
    dumpGroups = sortDumps(dumps)
    for ig,group in enumerate(dumpGroups):
        if len(group) < nkeep:
           continue #group needs no action
        oldest = group[0]
        tag = oldest['path'].split('_')[0]
        nextGroupNewest = dumpGroups[ig+1][-1]
        if oldest['created'] < nextGroupNewest['created'] - period[tag]:
            advanceTagPath(oldest['path'])
        else:
            try: #delete oldest
                os.remove(oldest['path'])
                print('\t\tDeleted', oldest['path'])
            except:
                print('\tError in deleting oldest dump',oldest['path'])
        if tag == 'Y':
            break

###############################################################
# nkeep = {'daily': 5, 'weekly': 5, 'monthly': 5, 'yearly': 5}
nkeep = {'daily': 2, 'weekly': 3, 'monthly': 4, 'yearly': 2}
loopTime = 1 #days
basePath = '/home/bret/'
htdocsSource = os.path.join(basePath,'skylinesC','htdocs','files')
dumpBaseName = 'skylinesdump'

#sf_backup = '/media/sf_backup' #on shared folder
sf_backup = '/media/test'
#testing
realfiles = os.listdir('/media/sf_backup')
for files in realfiles:
    os.system('touch /media/test/{}'.format(file))
#end testing


htdocsSFbu = os.path.join(sf_backup, 'htdocs')
if not os.path.exists(htdocsSFbu): os.mkdir(htdocsSFbu)
dbName = 'skylines'
dumpExtension = 'custom' # compression of about 3
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
        print('Binary backup for {}'.format(sf_backup))
        sfDumpPath = dump(sf_backup,dbName,dumpExtension)
        datedSFdumpPath =  os.path.join(sf_backup,'{}_D_{}.{}'.format(dumpBaseName, nowStr, dumpExtension))
        copy2(sfDumpPath, datedSFdumpPath)
    dumps = getDumpsInfo(sf_backup)
    pruneDumps(dumps)

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

    #Are we adding to htdocs tar file or creating one for each day?

    # Add igcs to tar file
    # print("Compressing igc files"
    tarName = 'htdocs_{}-backto-{}.tar.gz.temp'.format(nowStr, latestTime.strftime(timeFormat))
    tempTarPath = os.path.join(htdocsSFbu,tarName)
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

    #find time until midnight
    secNextSave = ((24 * loopTime - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)

    #wait until 10 min after midnight.  Groupflights runs at midnight.
    print('\n--- sleeping ---\n')
    t.sleep(secNextSave + 10 * 60)
