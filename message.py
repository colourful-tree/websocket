 # -*- coding: UTF-8 -*-
from geventwebsocket import WebSocketError
import uuid

class MessageServer(object):

    def __init__(self):
        self.observers = []
        self.rooms = []
        self.uid2ws = {}

    def to_room(self):
        while len(self.observers) % 2 == 0:
            a = self.observers.pop(0)
            b = self.observers.pop(0)
            room_id = uuid.uuid1()
            self.rooms.append([a, b, True])
            a.send("create room success")
            a.send("it is your turn")
            b.send("create room success")

            if len(self.observers) == 0:
                break
            
    def add_message(self, ws, msg):
        #for ws in self.observers:
        for v in self.rooms:
            if ws == v[0] or ws == v[1]:
                try:
                    if ws == v[0] and v[2] is True:
                        v[1].send(msg)
                        v[2] = False
                    elif ws == v[0] and v[2] is not True:
                        v[0].send("is not your turn")
                    elif ws == v[1] and v[2] is False:
                        v[0].send(msg)
                        v[2] = True
                    else:
                        v[1].send("is not your turn")
                except WebSocketError:
                    print ws, 'is closed'
                break

    def clean_up(self, ws):
        for v in self.rooms[:]:
            is_closed = False
            if v[0].closed and not v[1].closed:
                v[1].send("you win!")
                is_closed = True
            elif v[1].closed and not v[0].closed:
                v[0].send("you win~")
                is_closed = True
            if is_closed:
                self.rooms.remove(v)
        if ws in self.observers:
            self.observers.pop(self.observers.index(ws))
            
        for i in list(self.uid2ws.keys()):
            if self.uid2ws[i].closed:
                del(self.uid2ws[i])
        print "observers:"
        print self.observers
        print "rooms:"
        print self.rooms
        print "uid2ws:"
        print self.uid2ws
        #self.observers = filter(lambda x: not x.closed, self.observers) 
