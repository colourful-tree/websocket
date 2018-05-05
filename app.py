# manage.py
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template, abort
import uuid

import message


msgsrv = message.MessageServer()

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('message.html')


@app.route('/create/')
def create():
    uid = request.args.get("uid")
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        print "uid:[%s]" % uid
        msgsrv.uid2ws[uid] = ws
        msgsrv.observers.append(ws)
        msgsrv.to_room()
        while True:
            if ws is not None:
                if not ws.closed: 
                    message = ws.receive()
                    if message:
                        msgsrv.add_message(ws, "%s" % message)
                else:
                    msgsrv.clean_up(ws)
                    break
            else:
                abort(404)
    return "Connected!"

@app.route('/send/')
def send():
    uid = request.args.get("uid")
    ws = msgsrv.uid2ws[uid]
    message = request.args.get("message")
    msgsrv.add_message(ws, "%s" % message)
    return message


if __name__ == '__main__':
    http_server = WSGIServer(('your ip', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
