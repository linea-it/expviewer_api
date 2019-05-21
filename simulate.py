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
    yield from asyncio.sleep(random.uniform(1.0, 3.0))
    logger.info('Creating img... {} to {}'.format(src, dst))
    start = time.time()
    shutil.copyfile(src, dst)
    logger.info('runtime: {}'.format(time.time() - start))

@asyncio.coroutine
def simulate_exposure():
    tasks = []

    for img in IMAGES:
        basename = os.path.basename(img)
        name = "exp-{}-{}".format(str(ID).zfill(3), basename) 
        tasks.append(create_img(img, "{}/{}".format(WATCHERDIR, name)))

    start = time.time()
    yield from asyncio.wait(tasks)
    logger.info('EXPOSURE {} runtime: {}'.format(ID, time.time() - start))

def rm_tif():
    logger.info('Removing TIF images...')
    files = glob.glob('{}/*'.format(WATCHERDIR))

    start = time.time()

    for f in files:
        os.remove(f)
    
    logger.info('Remove EXP {} runtime: {}'.format(ID, time.time() - start))

ioloop = asyncio.get_event_loop()

try: 
    while True:
        ioloop.run_until_complete(simulate_exposure())
        time.sleep(30)

        if ID <= 100:
            ID = ID + 1
        else:
            ID = 1

        for task in asyncio.Task.all_tasks():
            task.cancel()

        rm_tif()
except KeyboardInterrupt:
    logger.info('Bye!')
finally:
    rm_tif()
    ioloop.close()