# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import ujson as json
import uuid


token_set = set()
token_carinfo_dict = {}
token_carpos_dict = {}
token_control_dict = {}


def check_int(s):
    if s[0] in ('-', '+'):
        return s[1:].isdigit()
    return s.isdigit()


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

        self.write("Hello, world")
        self.flush()

class JoinHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

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
            token = str(uuid.uuid4().fields[-1])[:5]
            token_set.add(token)
            token_carinfo_dict[token] = (name, color, type)
            token_carpos_dict[token] = (0, 0, 0, 0)
            token_control_dict[token] = (0, 0)
    
            result['result'] = 'success'
            result['token'] = token
            result['carinfo'] = token_carinfo_dict[token]
            result['carpos'] = token_carpos_dict[token]
            result['control'] = token_control_dict[token]
        
        self.write(json.dumps(result))
        self.flush()

class CarPosHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

        self.write(json.dumps(token_carpos_dict))
        self.flush()

class CarInfoHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

        self.write(json.dumps(token_carinfo_dict))
        self.flush()

class CarControlHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

        self.write(json.dumps(token_control_dict))
        self.flush()


class DriveHandler(tornado.web.RequestHandler):
    def get(self):
        global token_set
        global token_carinfo_dict
        global token_carpos_dict
        global token_control_dict

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
        elif token not in token_set:
            result['result'] = 'error'
            result['message'] = 'not exist token! are you trying to hack?'
        elif check_int(angle) == False:
            result['result'] = 'error'
            result['message'] = 'angle must be integer'
        elif check_int(accel) == False:
            result['result'] = 'error'
            result['message'] = 'accel must be integer'
        elif 0 > int(angle) and int(angle) > 360:
            result['result'] = 'error'
            result['message'] = 'angle must be in range [0, 360]'
        elif 0 > int(accel) and int(accel) > 100:
            result['result'] = 'error'
            result['message'] = 'accel must be in range [0, 100]'
        else:

            token_control_dict[token] = (angle, accel)

            result['result'] = 'success'
            result['carinfo'] = token_carinfo_dict[token]
            result['carpos'] = token_carpos_dict[token]
            result['control'] = token_control_dict[token]
        
        self.write(json.dumps(result))
        self.flush()


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/join", JoinHandler),
    (r"/car_pos", CarPosHandler),
    (r"/car_info", CarInfoHandler),
    (r"/car_control", CarControlHandler),
    (r"/drive", DriveHandler),

])

if __name__ == "__main__":
    application.listen(9999)
    tornado.ioloop.IOLoop.instance().start()
