from bge import logic
import socket
import requests
import math
from mathutils import Euler
from math import radians

API_CAR_POS = 'http://cosmosworld.cafe24.com:9999/car_pos'

class Monitor(object):

    def __init__(self):
        
        self.cars = {}
        self.session = requests.Session()
        self.logic_tick = 0
        
        self.scene = logic.getCurrentScene()
        self.spawner = self.scene.objects["Spawner"]
        self.car_count_text = self.scene.objects["CarCountText"]
        
    def poll(self):
    
        self.logic_tick = self.logic_tick + 1
        state = self.session.get(API_CAR_POS).json()
        
        self.car_count_text["Text"] = 'Car count: %d' % len(state)
        
        print('Tick %d' % self.logic_tick)
        for k in state:
            #print(k, state[k])
            if not k in self.cars:
                avatar = self.scene.addObject("Avatar", self.spawner)
                avatar.children[0]["Text"] = k
                
                self.cars[k] = avatar
            
            self.cars[k].worldPosition.x = state[k][0]
            self.cars[k].worldPosition.y = state[k][1]
            self.cars[k].worldPosition.z = 10#state[k][1]
            
            self.cars[k].localOrientation = Euler([0,0, radians(state[k][2])]).to_matrix()
        
        

monitor = Monitor()

def poll():
    print('polling')
    #monitor.poll()

class User:
    
    def __init__(self, name):
        
        self.name = name

class Server:
    
    def __init__(self, host="", port=9999):
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(False)
        self.socket.bind((host, port))
        
        self.addr_user = {}
        
    def receive(self):
        
        while True:
            
            try:
                data, addr = self.socket.recvfrom(1024)
                
                if not addr in self.addr_user:
                    
                    user = User(data.decode())
                    scene = logic.getCurrentScene()
                    spawner = scene.objects["Spawner"]
                    avatar = scene.addObject("Avatar", spawner)
                    avatar.children[0]["Text"] = user.name
            except socket.error:
                break

server = None # Server("", 19853)

def init():

    scene = logic.getCurrentScene()
    spawner = scene.objects["Spawner"]
    avatar = scene.addObject("Avatar", spawner)
    avatar.children[0]["Text"] = "hehehe"

    print("Init finished.")

def receive():
    server.receive()