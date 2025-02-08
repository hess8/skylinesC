import os
from common import linkAllDir,pathWinLin
from production.utilities.common import pathWinLin

#realDir = pathWinLin(os.path.join('A','landscapesC2'))
realDir = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
linksDir =  pathWinLin(os.path.join('C','condor2','Landscapes'))
#realDir = '/mnt/E/landscapes/landscapesC2-main/'
#linksDir = '/mnt/E/landscapes/landscapesC3-main/'

linkAllDir(realDir,linksDir)
