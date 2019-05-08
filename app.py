from tornado import websocket, web, ioloop
import json
import logging

logger = logging.getLogger('__main__')
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s: %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

clients = list()


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("index.html")


class WebSocketHandler(websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        if self not in clients:
            clients.append(self)

    def on_close(self):
        if self in clients:
            clients.remove(self)


class ApiHandler(web.RequestHandler):

    async def get(self, *args):
        self.finish()
        _id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id" : _id, "value" : value}
        data = json.dumps(data)
        for cl in clients:
            cl.write_message(data)

    async def post(self):
        pass

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', WebSocketHandler),
    (r'/api', ApiHandler),
])

if __name__ == '__main__':
    app.listen(5678)
    ioloop.IOLoop.instance().start()