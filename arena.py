# -*- coding: utf-8 -*-
import uuid
import car
import threading
import time
from datetime import datetime

class racingArena(threading.Thread):

    keep_racing = True

    max_player_count = 100
    player_count = 0

    id_token_list = []
    token_id_dict = {}

    op_accel_list = []
    op_handle_list = []
    op_brake_list = []
    
    car_list = []

    car_info_dict = {}
    cur_pos_list = []

    register_lock = threading.Lock()

    def __init__(self):
        
        max_count = self.max_player_count
        
        self.id_token_list = [None] * max_count
        
        self.op_accel_list = [None] * max_count
        self.op_handle_list = [None] * max_count
        self.op_brake_list = [None] * max_count
        
        self.car_list = [None] * max_count

        threading.Thread.__init__(self)


    def register(self, user_car):

        registered = False
        while registered == False:

            self.register_lock.acquire()
            
            token = str(uuid.uuid4().fields[-1])[:5]
            id = self.player_count

            user_car.id = id
            user_car.token = token

            self.id_token_list[id] = token
            self.token_id_dict[token] = id

            self.op_accel_list[id] = None
            self.op_handle_list[id] = None
            self.op_brake_list[id] = None
            
            self.car_list[id] = user_car

            self.cur_pos_list.append(user_car.get_pos())
            self.car_info_dict[id] = user_car.get_info()

            self.player_count += 1
            registered = True
            
            self.register_lock.release()

            if registered == False:
                time.sleep(0.001)

        return user_car


    def run(self):

        while self.keep_racing:

            idle = 16
            start_time = datetime.now()
            
            for id in range(0, self.player_count):

                accel = self.op_accel_list[id]
                handle = self.op_handle_list[id]
                brake = self.op_brake_list[id]

                cur_car = self.car_list[id]
               
                # consume operation
                if accel != None:
                    cur_car.throttle += accel
                    cur_car.brake = 0
                    cur_car.throttle = max(-100, cur_car.throttle)
                    cur_car.throttle = min( 100, cur_car.throttle)

                if handle != None:
                    cur_car.steer_angle += handle
                    cur_car.steer_angle = max(-car.car.PI / 4.0, cur_car.steer_angle)
                    cur_car.steer_angle = min( car.car.PI / 4.0, cur_car.steer_angle)

                if brake != None and brake == True:
                    cur_car.brake = 100
                    cur_car.throttle = 0

                self.op_accel_list[id] = None
                self.op_handle_list[id] = None
                self.op_brake_list[id] = None

                # update position
                cur_car.move_tick(idle / 1000.0)

                # update position info for API
                self.cur_pos_list[id] = cur_car.get_pos()

            end_time = datetime.now()
            
            # sleep for next tick
            elapsed = end_time - start_time
            idle -= elapsed.microseconds / 1000
            if idle < 0:
                idle = 0
            time.sleep(idle / 1000.0)
