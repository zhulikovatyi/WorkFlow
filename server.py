import tornado.ioloop
import tornado.web
import socket_handler
import api_handler

from tornado import options, websocket

options.define("port", default=8888, help="run on the given port", type=int)
options.define("debug", default=False, help="run in debug mode")

clients = []

class IndexHandler(tornado.web.RequestHandler):

    def get(request):
        request.render('index.html')

class SocketHandler(websocket.WebSocketHandler):

    def on_message(self, message):
        message = tornado.escape.json_encode({
            'text': message
        })
        for cl in clients:
            cl.write_message(message)

    def open(self, *args, **kwargs):
        clients.append(self)
        print("WebSocket opened")

    def on_close(self):
        clients.remove(self)
        print("WebSocket closed")


def main():
    options.parse_command_line()
    opts = options.options
    application = tornado.web.Application(
        [
            (r"/", IndexHandler),
            (r"/ws", SocketHandler),
            (r"/ws/timer", socket_handler.WorkTimerHandler),
            (r"/api/task/([^/]*)", api_handler.TaskHandler)
        ],
        debug=opts.debug
    )
    application.listen(opts.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()