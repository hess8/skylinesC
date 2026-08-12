import os,sys
sys.path.append('/mnt/P/shared_VMs/common_py')
sys.path.append('/media/sf_shared_VMs/common_py')
from uzsubs import pathWinLin
'''If mode is 'keep', removes all links that don't contain the selected strings.
Mode 'remove' Removes all links that do contain one of the selected strings'
Mode 'all' removes all links
Mode 'broken' removes only broken links'''

dirToRmLinks = pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))
# dirToRmLinks = pathWinLin(os.path.join('C','condor2','landscapes'))
keepStrs = []
# controlStrs = ['remove',['_to_C3to_C3']]
# controlStrs = ['all']
controlStrs = ['broken']
mode = controlStrs[0]  # 'keep' or 'remove'
if len(controlStrs) > 1:
    strs = controlStrs[1]
for item in os.listdir(dirToRmLinks):
    remove = False
    itemPath = os.path.join(dirToRmLinks, item)
    if not os.path.islink(itemPath):
        continue
    if mode == 'broken':
        if not os.path.exists(itemPath): #broken
            remove = True
    else:
        for str in strs:
            if mode == 'all':
                remove = True
            if mode == 'keep' and str in item:
                break
            elif mode == 'remove' and str in item:
                remove = True

                break
    if remove:
        os.remove(itemPath)
        print('Removed symlink', itemPath)
