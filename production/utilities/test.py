import os, sys, time
import time as t
# import paramiko
import tarfile
from shutil import copy2
    #utsoar maintenance:
# os.system('cp /media/sf_landscapes-zip/utsoar-* ember/app/templates/')
# os.system('cp /media/sf_landscapes-zip/flights.csv /media/sf_Google_Drive/')

# fname = pathlib.Path('/media/sf_landscapes-zip/utsoar-dist')
# print(fname.stat())
print os.path.getmtime('/media/sf_landscapes-zip/utsoar-dist.hbs')

print (time.time() - os.path.getmtime('/media/sf_landscapes-zip/utsoar-dist.hbs'))/3600.0 < 24

# def timestamp(self):
#     "Return POSIX timestamp as float"
#     if self._tzinfo is None:
#         return _time.mktime((self.year, self.month, self.day,
#                              self.hour, self.minute, self.second,
#                              -1, -1, -1)) + self.microsecond / 1e6
#     else:
#         return (self - datetime(1970, 1, 1).total_seconds()
# where _EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


