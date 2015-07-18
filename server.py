# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import ujson as json
import uuid
import math
import thread
import sys

from arena import racingArena
from car import car


# start racing arena thread
racing_arena = racingArena()


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


def check_double(s):
    try:
        float(s)
    except ValueError:
        return False
    return True


def register_car(name, color, type):
    global racing_arena

    user_car = car(name, color, type)
    return racing_arena.register(user_car)

def deregister_car(id):
    global racing_arena

    return racing_arena.deregister(id)

class JoinHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        name = self.get_argument('name', None, True)
        color = self.get_argument('color', None, True)
        type = self.get_argument('type', None, True)

        result = {}
        if name == None:
            result['result'] = 'error'
            result['message'] = 'name not specified!'
        elif color == None:
            result['result'] = 'error'
            result['message'] = 'color not specified!'
        elif type == None:
            result['result'] = 'error'
            result['message'] = 'type not specified!'
        else:
            user_car = register_car(name, color, type)

            result['result'] = 'success'
            result['token'] = user_car.token
            result['car'] = user_car
        
        self.write(json.dumps(result))
        self.flush()

class LeaveHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        id = self.get_argument('id', None, True)

        result = {}
        if id == None:
            result['result'] = 'error'
            result['message'] = 'id not specified!'
        elif check_int(id) == False:
            result['result'] = 'error'
            result['message'] = 'id should be int type!'
        elif int(id) not in racing_arena.car_info_dict:
            result['result'] = 'error'
            result['message'] = 'id not exist!'
        else:
            deregister_car(int(id))
            result['result'] = 'success'
        
        self.write(json.dumps(result))
        self.flush()

class CarPosHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        self.write(json.dumps(racing_arena.car_pos_dict))
        self.flush()

class CarInfoHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        self.write(json.dumps(racing_arena.car_info_dict))
        self.flush()

class CarDetailHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        id = self.get_argument('id', None, True)

        result = {}
        if id == None:
            result['result'] = 'error'
            result['message'] = 'id not specified!'
        elif check_int(id) == False:
            result['result'] = 'error'
            result['message'] = 'id should be int type!'
        elif int(id) not in racing_arena.car_info_dict:
            result['result'] = 'error'
            result['message'] = 'id not exist!'
        else:
            result['id'] = id
            result['car'] = racing_arena.car_list[int(id)]
        
        self.write(json.dumps(result))
        self.flush()

class AccelHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        token = self.get_argument('token', None, True)
        accel = self.get_argument('accel', None, True)

        result = {}
        if token == None:
            result['result'] = 'error'
            result['message'] = 'token not specified!'
        elif accel == None:
            result['result'] = 'error'
            result['message'] = 'accel not specified!'
        elif token not in racing_arena.token_id_dict:
            result['result'] = 'error'
            result['message'] = 'not exist token! are you trying to hack?'
        elif check_int(accel) == False:
            result['result'] = 'error'
            result['message'] = 'accel must be integer'

        if 'result' in result:
            self.write(json.dumps(result))
            self.flush()
            return
        
        accel = int(accel)

        if -101 > accel or accel > 100:
            result['result'] = 'error'
            result['message'] = 'accel must be in range [-100, 100]'
        else:

            id = racing_arena.token_id_dict[token]
            racing_arena.op_accel_list[id] = accel
            result['result'] = 'success'
        
        self.write(json.dumps(result))
        self.flush()
        

class HandleHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        token = self.get_argument('token', None, True)
        angle = self.get_argument('angle', None, True)

        result = {}
        if token == None:
            result['result'] = 'error'
            result['message'] = 'token not specified!'
        elif angle == None:
            result['result'] = 'error'
            result['message'] = 'angle not specified!'
        elif token not in racing_arena.token_id_dict:
            result['result'] = 'error'
            result['message'] = 'not exist token! are you trying to hack?'
        elif check_double(angle) == False:
            result['result'] = 'error'
            result['message'] = 'angle must be float'

        if 'result' in result:
            self.write(json.dumps(result))
            self.flush()
            return
        
        angle = float(angle)

        if -car.PI / 4 > angle or angle > car.PI / 4:
            result['result'] = 'error'
            result['message'] = 'angle must be in range [-PI / 4, PI / 4]'
        else:
            id = racing_arena.token_id_dict[token]
            racing_arena.op_handle_list[id] = angle
            result['result'] = 'success'
        
        self.write(json.dumps(result))
        self.flush()
        
        
class BrakeHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        token = self.get_argument('token', None, True)

        result = {}
        if token == None:
            result['result'] = 'error'
            result['message'] = 'token not specified!'
        elif token not in racing_arena.token_id_dict:
            result['result'] = 'error'
            result['message'] = 'not exist token! are you trying to hack?'

        if 'result' in result:
            self.write(json.dumps(result))
            self.flush()
            return

        id = racing_arena.token_id_dict[token]
        racing_arena.op_brake_list[id] = True
        result['result'] = 'success'
        
        self.write(json.dumps(result))
        self.flush()



application = tornado.web.Application([
    (r"/join", JoinHandler),
    (r"/leave", LeaveHandler),
    (r"/car_pos", CarPosHandler),
    (r"/car_info", CarInfoHandler),
    (r"/car_detail", CarDetailHandler),
    (r"/accel", AccelHandler),
    (r"/handle", HandleHandler),
    (r"/brake", BrakeHandler),
    (r"/", BrakeHandler),

])

if __name__ == "__main__":
    

    # start network thread
    if sys.argv[1] == 'REAL':
        application.listen(9999)
    elif sys.argv[1] == 'TEST':
        application.listen(10000)
    else:
        print 'undefined option [REAL/TEST]'
        sys.exit(-1)

    for i in range(0, 2):
        register_car('zone', 'black', 'go')
    

    try:
        racing_arena.start()
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        racing_arena.keep_racing = False
        racing_arena.join()
        tornado.ioloop.IOLoop.instance().stop()
