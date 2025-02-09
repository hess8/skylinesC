import os,sys
from common import linkAllDir,pathWinLin

trueDir = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
#trueDir = pathWinLin(os.path.join('A','landscapesC2'))
#linksDir =  pathWinLin(os.path.join('C','condor2','Landscapes'))
linksDir =  pathWinLin(os.path.join('E','landscapes','landscapesC3-main'))

linkAllDir(trueDir,linksDir)
