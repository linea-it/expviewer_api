import os
import glob
import logging
from time import sleep

logger = logging.getLogger('__main__')

class State:
    def __init__(self):
        self.count = 0
        self.exps = []
        self.lock=False

    def monitor_files(self, s):
        if self.lock:
            return
        self.lock = True
        exps = glob.glob('/home/felipe/repos/lsst/notebook/expsNew/*')
        self.exps = []
        for PATH in exps:
            sleep(0.01)
            if os.path.isfile(PATH) and os.access(PATH, os.R_OK) and PATH not in self.exps:
                s.exps.append(PATH.split('expsNew/')[1].split('.')[0])
        self.lock=False
