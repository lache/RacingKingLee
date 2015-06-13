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


def register_car(name, color, type):
    global racing_arena

    user_car = car(name, color, type)
    return racing_arena.register(user_car)
 

class JoinHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        name = self.get_argument('name', None, True)
        color = self.get_argument('color', None, True)
        type = self.get_argument('type', None, True)

        result = {}
        if name == None:
            result['result'] = 'error'
            result['message'] = 'name is not specified!'
        elif color == None:
            result['result'] = 'error'
            result['message'] = 'color is not specified!'
        elif type == None:
            result['result'] = 'error'
            result['message'] = 'type is not specified!'
        else:
            user_car = register_car(name, color, type)

            result['result'] = 'success'
            result['token'] = user_car.token
            result['car'] = user_car
        
        self.write(json.dumps(result))
        self.flush()

class CarPosHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        self.write(json.dumps(racing_arena.cur_pos_dict))
        self.flush()


class DriveHandler(tornado.web.RequestHandler):
    def get(self):
        global racing_arena

        token = self.get_argument('token', None, True)
        angle = self.get_argument('angle', None, True)
        accel = self.get_argument('accel', None, True)

        result = {}
        if token == None:
            result['result'] = 'error'
            result['message'] = 'token is not specified!'
        elif angle == None:
            result['result'] = 'error'
            result['message'] = 'angle is not specified!'
        elif accel == None:
            result['result'] = 'error'
            result['message'] = 'accel is not specified!'
        elif token not in racing_arena.token_id_dict:
            result['result'] = 'error'
            result['message'] = 'not exist token! are you trying to hack?'
        elif check_int(angle) == False:
            result['result'] = 'error'
            result['message'] = 'angle must be integer'
        elif check_int(accel) == False:
            result['result'] = 'error'
            result['message'] = 'accel must be integer'

        if 'result' in result:
            self.write(json.dumps(result))
            self.flush()
            return
        
        angle = int(angle)
        accel = int(accel)

        if 0 > angle or angle > 360:
            result['result'] = 'error'
            result['message'] = 'angle must be in range [0, 360]'
        elif -101 > accel or accel > 100:
            result['result'] = 'error'
            result['message'] = 'accel must be in range [-100, 100]'
        else:

            id = racing_arena.token_id_dict[token]
            racing_arena.op_list[id] = (angle, accel)
            result['result'] = 'success'
        
        self.write(json.dumps(result))
        self.flush()


application = tornado.web.Application([
    (r"/join", JoinHandler),
    (r"/car_pos", CarPosHandler),
    (r"/drive", DriveHandler),

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
