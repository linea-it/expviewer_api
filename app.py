import tornado.web
import tornado.websocket
import tornado.ioloop
import logging
import time
from state import State
import json
from threading import Thread

logger = logging.getLogger('__main__')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

s = State()

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        logger.info("New client connected")
        s.count+=1
        status = {'status': "connected"}
        self.write_message(json.dumps(status))
        self.lock=False
        self.loop = tornado.ioloop.PeriodicCallback(self.check_ten_seconds, 4000)
        self.loop.start()

    async def on_message(self, message):
        logger.info(message)
        if message == "getAllImages":
            self.write_message(self.get_state())
        elif message == "clearImages":
            s.exps = []
        elif message == "findImages":
            t = Thread(target=s.monitor_files, args=(s,))
            t.start()

    def on_close(self):
        logger.info("Client disconnected")
        s.count-=1
        self.loop.stop()

    def check_origin(self, origin):
        return True

    def check_ten_seconds(self):
        # logger.info("Just check")
        self.write_message(self.get_state())

    def get_state(self):
        return json.dumps({"USERS": s.count, "images": s.exps})

application = tornado.web.Application([
    (r"/", WebSocketHandler),
], debug=True)


if __name__ == "__main__":
    application.listen(5678)
    tornado.ioloop.IOLoop.instance().start()
