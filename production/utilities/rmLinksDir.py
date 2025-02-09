import os,sys
from common import pathWinLin, rmLinksDir

#dirToRmLinks = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
dirToRmLinks = pathWinLin(os.path.join('C','condor2','landscapes'))
removeStrs = ['_to_C3']
keepStrs = []
controlStrs = ['remove',['_to_C3']]
rmLinksDir(dirToRmLinks,controlStrs)
