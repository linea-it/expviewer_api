from tornado import websocket, web, ioloop, gen
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
# from watchdog.observers.polling import PollingObserver as Observer
from watchdog.observers import Observer as Observer
from watchdog.events import RegexMatchingEventHandler
import asyncio
import json
import os
import time
import logging
from threading import Thread
import glob

level = os.getenv('LOGLEVEL', 'info')

if level == 'debug':
    level = logging.DEBUG
elif level == 'info':
    level = logging.INFO
else:
    level = logging.ERROR

logger = logging.getLogger(__name__)
handler = logging.FileHandler('expviewer.log')
formatter = logging.Formatter(
    '%(asctime)s: %(name)s ~ %(levelname)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(level)

WATCHERDIR = os.getenv('WATCHERDIR')

clients = list()
nuser = int()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(websocket.WebSocketHandler):
    tasks = list()

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            global nuser
            nuser = nuser + 1
            self.user_id = nuser
            clients.append(self)

            logger.debug('Open request: user {}'.format(self.user_id))

            loop = asyncio.get_event_loop()
            asyncio.run_coroutine_threadsafe(self.get_all_images(), loop)

    async def get_all_images(self):
        tasks = []

        for img in glob.glob("{}/exp-*.tif".format(WATCHERDIR)):
            try:
                tasks.append(self.on_message(img)) 
            except:
                logger.exception("Error to write message to websocket: user {}".format(self.user_id))

        await asyncio.gather(*tasks)


    def on_close(self):
        if self in clients:
            logger.debug('Close request: user {}'.format(self.user_id))
            clients.remove(self)
            cancel_tasks(self)

    @gen.coroutine
    def on_message(self, filepath):
        file_size = -1

        while file_size != os.path.getsize(filepath):
            file_size = os.path.getsize(filepath)
            asyncio.sleep(1)

        filename = os.path.basename(filepath)
        logger.debug("{} image created!".format(filename))
        yield self.write_message({'images': [filename]})


class ImageWatcher:
    """ Responsible for managing events in images
    on a particular path.
    """
    
    def __init__(self, src_path):
        """ Initializes attributes and start thread for the
        monitoring
        
        Arguments:
            src_path {str} -- directory path to be monitored
        """
        self.__src_path = src_path
        self.__event_handler = ImageHandler()
        self.__event_observer = Observer()
        self.__stop_thread = False
        self.__process = Thread(target=self.__run)
        self.__process.start()

    def __run(self):
        """ Sets the background monitoring. """
        self.__start()
        try:
            while True:  
                if self.__stop_thread: 
                    break
                time.sleep(2)
        except Exception:
            logger.exception("Image watcher interrupted")
        finally:
            self.__stop()

    def __start(self):
        """ Starts monitoring. """
        self.__schedule()
        self.__event_observer.start()
        logger.debug('Image watcher started!')

    def __stop(self):
        """ Breaks monitoring. """
        self.__event_observer.stop()
        self.__event_observer.join()
        logger.debug('Image watcher stoped!')

    def __schedule(self):
        """ Schedules the event handler. """
        self.__event_observer.schedule(
            self.__event_handler,
            self.__src_path,
            recursive=True
        )

    def close(self):
        """ Sets flag to stop monitoring. """
        self.__stop_thread = True


class ImageHandler(RegexMatchingEventHandler):
    
    FILE_REGEX = [r".*.tif$"]

    def __init__(self):
        super().__init__(self.FILE_REGEX)

    def on_created(self, event):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.send_msg(event))
        loop.close()

    async def send_msg(self, event):
        tasks = []

        for cl in clients:
            try:
                tasks.append(cl.on_message(event.src_path)) 
            except:
                logger.exception("Error to write message to websocket: user {}".format(cl.user_id))

        await asyncio.gather(*tasks)
        

def cancel_all_tasks():
    global clients
    for cl in clients:
        cancel_tasks(cl)


def cancel_tasks(cl):
    for task in cl.tasks:
        task.cancel()


app = web.Application([
    (r'/testing', IndexHandler),
    (r'/ws', WebSocketHandler),
])


if __name__ == '__main__':
    try: 
        exp = ImageWatcher(WATCHERDIR) 
        app.listen(int(os.getenv('APP_PORT')))
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        exp.close()
        cancel_all_tasks()