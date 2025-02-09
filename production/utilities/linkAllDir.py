import os,sys
from common import linkAllDir,pathWinLin


#trueDir = pathWinLin(os.path.join('A','landscapesC2'))
trueDir = pathWinLin(os.path.join('E','landscapes','landscapesC2-main'))
linksDir =  pathWinLin(os.path.join('C','condor2','Landscapes'))

linkAllDir(trueDir,linksDir)
