import os,sys
sys.path.append('/mnt/P/shared_VMs/common_py')
sys.path.append('/media/sf_shared_VMs/common_py')
from common import pathWinLin
'''If mode is 'keep', removes all links that don't contain on the selected strings.
Mode 'remove' Removes all links that do contain oneof the selected strings'''

dirToRmLinks = pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))
# dirToRmLinks = pathWinLin(os.path.join('C','condor2','landscapes'))
removeStrs = ['_to_C3']
keepStrs = []
controlStrs = ['remove',['_to_C3']]

mode = controlStrs[0]  # 'keep' or 'remove'
strs = controlStrs[1]
for item in os.listdir(dirToRmLinks):
    itemPath = os.path.join(dirToRmLinks, item)
    if not os.path.islink(itemPath):
        continue
    for str in strs:
        if mode == 'keep' and str in strs:
            break
        elif mode == 'remove' and str in item:
            os.remove(itemPath)
            print('Removed symlink', itemPath)
            break
    else:
        if mode == 'keep':
            os.remove(itemPath)
