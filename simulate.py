import os
import logging
import glob
import time
import random
import asyncio
import shutil

logger = logging.getLogger(__name__)
handler = logging.FileHandler('simulating.log')
formatter = logging.Formatter(
    '%(asctime)s: %(name)s ~ %(levelname)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

IMAGEDIR = os.getenv('IMAGEDIR')
WATCHERDIR = os.getenv('WATCHERDIR')
IMAGES = glob.glob("{}/*.tif".format(IMAGEDIR))
ID = 1

@asyncio.coroutine
def create_img(src, dst):
    yield from asyncio.sleep(random.uniform(2.0, 7.0))
    logger.info('Creating img... {} to {}'.format(src, dst))
    shutil.copyfile(src, dst)

@asyncio.coroutine
def simulate_exposure():
    tasks = []

    for img in IMAGES:
        basename = os.path.basename(img)
        name = "exp-{}-{}".format(str(ID), basename) 
        tasks.append(create_img(img, "{}/{}".format(WATCHERDIR, name)))

    yield from asyncio.wait(tasks)

def rm_tif():
    files = glob.glob('{}/*'.format(WATCHERDIR))
    for f in files:
        os.remove(f)

ioloop = asyncio.get_event_loop()

try: 
    while True:
        ioloop.run_until_complete(simulate_exposure())
        time.sleep(30)
        ID = ID + 1
        rm_tif()
except KeyboardInterrupt:
    logger.info('Bye!')
finally:
    rm_tif()
    ioloop.close()