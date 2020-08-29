import socket
import struct

import json

import threading

from utils import get_config

from google.protobuf.json_format import MessageToJson

from protocols import packet_pb2


class FiraVision(threading.Thread):
    def __init__(self):
        super(FiraVision, self).__init__()
        self.config = get_config()

        self.frame = {}
        
        self.vision_port = self.config['network']['vision_port']
        self.host = self.config['network']['multicast_ip']

    def assign_vision(self, game):
        self.game = game

    def run(self):
        print("Starting vision...")
        self.vision_sock = self._create_socket()
        self._wait_to_connect()
        print("Vision completed!")

        while True:
            env = packet_pb2.Environment()
            data = self.vision_sock.recv(1024)
            env.ParseFromString(data)
            self.frame = json.loads(MessageToJson(env))
            self.game.update()
            
    
    def _wait_to_connect(self):
        self.vision_sock.recv(1024)
    
    def _create_socket(self):
        sock = socket.socket(
            socket.AF_INET, 
            socket.SOCK_DGRAM, 
            socket.IPPROTO_UDP
        )

        sock.setsockopt(
            socket.SOL_SOCKET, 
            socket.SO_REUSEADDR, 1
        )

        sock.bind((self.host, self.vision_port))

        mreq = struct.pack(
            "4sl",
            socket.inet_aton(self.host),
            socket.INADDR_ANY
        )

        sock.setsockopt(
            socket.IPPROTO_IP, 
            socket.IP_ADD_MEMBERSHIP, 
            mreq
        )

        return sock


def assign_empty_values(raw_frame):
    frame = raw_frame.get('frame')
    if frame.get('ball'):
        frame['ball']['x'] = frame['ball'].get('x', 0)
        frame['ball']['y'] = frame['ball'].get('y', 0)
        frame['ball']['z'] = frame['ball'].get('z', 0)
        frame['ball']['vx'] = frame['ball'].get('vx', 0)
        frame['ball']['vy'] = frame['ball'].get('vy', 0)
    
    for robot in frame.get("robotsYellow"):
        robot['x'] = robot.get('x', 0)
        robot['y'] = robot.get('y', 0)
        robot['vx'] = robot.get('vx', 0)
        robot['vy'] = robot.get('vy', 0)
        robot['robotId'] = robot.get('robotId', 0)
        robot['orientation'] = robot.get('orientation', 0)
    
    for robot in frame.get("robotsBlue"):
        robot['x'] = robot.get('x', 0)
        robot['y'] = robot.get('y', 0)
        robot['vx'] = robot.get('vx', 0)
        robot['vy'] = robot.get('vy', 0)
        robot['robotId'] = robot.get('robotId', 0)
        robot['orientation'] = robot.get('orientation', 0)
    
    return frame

if __name__ == "__main__":
    import time
    v = FiraVision()

    v.start()

    while True:
        time.sleep(1)
        print(v.frame)