from __future__ import print_function
import os, sys, datetime, time, re
import time as t
# import paramiko
import tarfile
from shutil import copy2
sys.path.append('/media/sf_shared_VMs/common_py')
import subprocess


"""

This loops in a terminal and saves to local sf_backup and gitBUdir each day, which is committed and pushed. 
They keep the latest db dump and others up to nkeep, and all the htdocs incremental tars. 

Dump format "plain", or text requires about 3x more space than ".custom".  It requires psql to restore, not pg_restore.  

"""
def dumpsDelOld(buDir,nkeep):
    try:
        items = os.listdir(buDir)
        dumps = []
        dumpTimes = []
        dumpSizes = []
        for item in items:
            if 'dump' in item and os.path.isfile(os.path.join(buDir,item)):
                try:
                    dumps.append(item)
                    dumpTimeStamp = item.split('_')[1].replace('.custom','')
                    dumpTimes.append(datetime.datetime.strptime(dumpTimeStamp, format(timeFormat)))
                    try:
                        size = os.stat(os.path.join(buDir, item)).st_size
                        # print('\ttest', item, size
                    except:
                        size = None
                    dumpSizes.append(size)
                    # print('\t{:.2f} MB, {}'.format(size / float(10 ** 6), item)
                except:
                    'skip file'
    except:
        print('\tError in reading dumps')
    allInfo = zip(dumpTimes,dumps,dumpSizes)
    dumpsInfo =  [[dump,timeFile,size] for timeFile,dump,size in sorted(allInfo,reverse=True)] # name, timeFile, size
        #remove old dump files
#        for i in range(len(dumpsInfo)):
#            file = dumpsInfo[i][0]
#            size = dumpsInfo[i][2]
            # print('\t{:.2f} MB, {}'.format(size / float(10 ** 6), file)
    if len(dumpsInfo) > 0:
        oldestDump = dumpsInfo[-1]
        while len(dumpsInfo) > nkeep and oldestDump[2] <= dumpsInfo[0][2]: #Delete oldest if newest is larger or same size
            try: #delete oldest
                os.remove(os.path.join(buDir,oldestDump[0]))
                print('\t\tDeleted', oldestDump[0])
                dumpsInfo.pop()
                oldestDump = dumpsInfo[-1]
            except:
                print('\tError in deleting oldest dump',oldestDump)

###############################################################
slcBase = '/home/bret/skylinesC'
gitBUbase = '/home/bret/'
htdocsSource = os.path.join(slcBase,'htdocs','files')
dumpBaseName = 'skylinesdump'
backupRepoName = 'backup-skylinesC'
gitBUdir = os.path.join(gitBUbase, backupRepoName)
htdocsGitDir = os.path.join(gitBUdir, 'htdocs')
sf_backup = '/media/sf_backup'
htdocsSFbu = os.path.join(sf_backup, 'htdocs')



#dumpType = 'plain' #git can version this.
dumpType = 'custom'
#nkeepGitBU = 1
nkeepSfBackup = 15
timeFormat = '%Y-%m-%d.%H.%M.%S'

run = True
while run:
    newDump = False
    newTar = False
    now = datetime.datetime.now()
    nowStr = now.strftime(timeFormat)
    print
    print(now.strftime(timeFormat))
    #### Database backup #####
    doDump = True  # debugging switch
    dumpSize = 0
    if doDump: #debugging switch, when working on tar section below
        dumpName = '{}.{}'.format(dumpBaseName,dumpType)
        tempDumpName = dumpName + '.temp'
        tempDumpPath = os.path.join(gitBUdir,tempDumpName)
        dumpCmd = ['sudo','-u','bret','pg_dump','--exclude-table-data=elevations','--format={}'.format(dumpType),'skylines']
        f = open(tempDumpPath,'w')
        status = subprocess.call(dumpCmd, stdout=f)
        if status != 0: print('Error creating db dump')
        f.close()
        finishedDumpPath = tempDumpPath.replace('.temp', '')
        status = subprocess.call(['mv',tempDumpPath,finishedDumpPath])
        if status != 0: print('Error removing .temp tag')
        dumpSize = os.stat(finishedDumpPath).st_size
        print( '\t{:.2f} MB, {}'.format(dumpSize / float(10 ** 6), tempDumpName))
        list = finishedDumpPath.split('.')
        #datedGitDumpPath =  '{}_{}.{}'.format(list[0], nowStr, list[1])
        #copy2(finishedDumpPath, datedGitDumpPath) #same folder as original (gitBU).  Keep date-tagged dump backups up to nkeep, but don't commit them
        datedSFdumpPath =  os.path.join(sf_backup,'{}_{}.{}'.format(dumpName, nowStr, dumpType))
        if not os.path.exists(datedSFdumpPath):
            copy2(finishedDumpPath, datedSFdumpPath)
        dumpsDelOld(sf_backup, nkeepSfBackup)
        addCmd =  ['git','add', finishedDumpPath]
        status = subprocess.call(addCmd) #only current db
        if status != 0: print('Error git add new dB')
        commitStr = '"New /{}.{}"'.format(dumpBaseName, dumpType)
        cmd = ['git', '-C', gitBUbase, 'commit', '-am', commitStr]
        status = subprocess.call(cmd)
        if status != 0: print('Error git commit')
        newDump = True
#    dumpsDelOld(gitBUdir, nkeepGitBU)


    #### htdocs backup #####:
    # Read date of last htdocs tar file

    if not os.path.exists(htdocsGitDir):
        os.mkdir(htdocsGitDir)
    htdocsSfBUDir = os.path.join(sf_backup,'htdocs')
    #find latest backup
    if not os.path.exists(htdocsSfBUDir):
        os.mkdir(htdocsSfBUDir)
    try:
        htdocsBUfiles = os.listdir(htdocsGitDir)
    except:
        print('\tError in reading htdocs tars')
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
                size = os.stat(os.path.join(htdocsGitDir,filename)).st_size
                tarSizes.append(size)
                tarTimes.append(datetime.datetime.strptime(tarTimeStamp, format(timeFormat)))
            except:
                'skip file'

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
        copy2(finishedTarPath, htdocsGitDir)
        addCmd =  ['git','add', htdocsGitDir] #all htdocs tars
        status = subprocess.call(addCmd)
        if status != 0: print('Error git add htdocs backup dir')
        commitStr = '"New backup/{}.{}"'.format(dumpBaseName, dumpType)
        commitStr = '"New backup/{}.{} and {}"'.format(dumpBaseName, dumpType, tarName)
        cmd = ['git', '-C', gitBUbase, 'commit', '-am', commitStr]
        status = subprocess.call(cmd)
        if status != 0: print('Error git commit')
        newTar = True
    else:
        os.remove(tempTarPath)
        print('\tNo new htdocs files')

    print
    #commit the latest backup and the new htdocs tars  if any
    if newDump or newTar:
        cmd = ['git', '-C', gitBUbase, 'push']
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
    secMidnight = ((24 - now.hour - 1) * 3600) + ((60 - now.minute - 1) * 60) + (60 - now.second)

    #wait until 10 min after midnight.  Groupflights runs at midnight.
    t.sleep(secMidnight + 10 * 60)
