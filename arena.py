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

    op_list = []
    car_list = []

    cur_pos_dict = {}

    register_lock = threading.Lock()

    def __init__(self):
        max_count = self.max_player_count
        self.id_token_list = [None] * max_count
        self.op_list = [None] * max_count
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

            self.op_list[id] = None
            self.car_list[id] = user_car

            self.cur_pos_dict[id] = user_car.get_pos()

            self.player_count += 1
            registered = True
            
            self.register_lock.release()

            if registered == False:
                time.sleep(0.001)

        return user_car

    def run(self):

        while self.keep_racing:

            start_time = datetime.now()

            for id in range(0, self.player_count):

                op = self.op_list[id]
                user_car = self.car_list[id]
                
                # consume operation
                if op != None:
                    user_car.angle = op[0]
                    user_car.accel = op[1]
                self.op_list[id] = None

                # update position
                user_car.move_tick(1)

                # update position info for API
                self.cur_pos_dict[id] = user_car.get_pos()

            end_time = datetime.now()
            
            # sleep for next tick
            elapsed = end_time - start_time
            idle = 16
            idle -= elapsed.microseconds / 1000
            if idle < 0:
                idle = 0
            time.sleep(idle / 1000.0)
