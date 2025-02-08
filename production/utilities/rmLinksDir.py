import os
from common import rmLinksDir

path = '/mnt/E/landscapes/landscapesC2-main'
removeStrs = ['_to_C3']
keepStrs = []
controlStrs = ['remove',['_to_C3']]
rmLinksDir(path,controlStrs)
