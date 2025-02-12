import os,sys
import platform
sys.path.append('/mnt/P/shared_VMs/common_py')
sys.path.append('/media/sf_shared_VMs/common_py')
from common import makeLink,pathWinLin
'''puts links to every item in truePath in linksPath'''

truePath = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
#truePath = pathWinLin(os.path.join('A','landscapesC2'))
#linksPath =  pathWinLin(os.path.join('C','condor2','Landscapes'))
linksPath =  pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))

if platform.system() == 'Windows': print('Must run as Administrator to use linkAllPath')
if not os.path.exists(linksPath):
    os.mkdir(linksPath)
items = os.listdir(truePath)
for item in items:
    makeLink(truePath=os.path.join(truePath,item),linkPath=os.path.join(linksPath,item))
