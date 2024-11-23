import ipaddress
import socketserver
import socket
import threading
import json
import time
import math
import random
import os

PORT = int(os.getenv("PORT", 3000))

class Player:
    socket = 0
    x = 0
    y = 0
    z = 0
    YAW = 0
    nick = ""
    healt = 100
    score = 0
    deadCount = 0
    isDead = False
    spawn = False
    
class TimeClass:
    lastTime = 0

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
            data = self.request[0].strip().decode()
            socket = self.request[1]
            recvJson = json.loads(data)
            for player in players:
                if player.nick == recvJson["nick"]:
                    player.x = float(recvJson["x"])
                    player.y = float(recvJson["y"])
                    player.z = float(recvJson["z"])
                    player.YAW = float(recvJson["YAW"])

                    if player.spawn:
                        player.isDead = False
                        SpawnPlayer(player)
                    
                    sData = {
                        player.nick: {
                            "healt": player.healt,
                            "dead": player.isDead,
                            "x": player.x,
                            "y": player.y,
                            "z": player.z,
                            "changeXYZ": player.spawn,
                            "kill": player.score,
                            "deadC": player.deadCount,
                            "lastTime": timeClass.lastTime
                        },
                    }

                    if player.spawn:
                        player.spawn = False
                    
                    for plyr in players:
                        if plyr.nick != player.nick and not(plyr.isDead):
                            sData.update({
                                plyr.nick: {
                                    "x": plyr.x,
                                    "y": plyr.y,
                                    "z": plyr.z,
                                    "YAW": plyr.YAW,
                                    "kill": plyr.score,
                                    "deadC": plyr.deadCount,
                                    "lastTime": timeClass.lastTime
                                },
                            })
                    sendJson = json.dumps(sData)
                    #print(sData)
                    socket.sendto(sendJson.encode(), self.client_address)

def SpawnPlayer(player):
    player.x = random.randint(0, 52)
    player.z = random.randint(0, 52)
    player.y = 6

def BulletThread(lx, ly, lz, player):
    x = player.x
    y = player.y
    z = player.z
    bx = x
    by = y
    bz = z
    t = 0.01
    while True:
        for plyr in players:
            if plyr.socket != player.socket:
                px = plyr.x
                py = plyr.y
                pz = plyr.z
                if x >= px - 0.25 and x < px + 0.25 and y >= py - 1.75 and y < py + 0.25 and z >= pz - 0.25 and z < pz + 0.25:
                    if not(plyr.isDead):
                        plyr.healt -= 25
                        if plyr.healt <= 0:
                            plyr.isDead = True
                            player.score += 1
                            plyr.deadCount += 1
                            time.sleep(3)
                            plyr.healt = 100
                            plyr.spawn = True
                        return
        x += lx * 0.01
        y += ly * 0.01
        z += lz * 0.01
        dx = bx - x
        dy = by - y
        dz = bz - z
        distance2D = math.sqrt(dx * dx + dy * dy)
        distance = math.sqrt(distance2D * distance2D + dz * dz)
        if distance >= 100:
            return

def PlayerHandler(player):
    while True:
        try:
            data = player.socket.recv(1024).decode()
            recvJson = json.loads(data)
            print(recvJson)
            if recvJson["mode"] == "1":
                if recvJson["command"] == "leave":
                    nick = player.nick
                    players.remove(player)
                    print("Player disconnected:", nick, ":", len(players))
                    break
            elif recvJson["mode"] == "2":
                bulletThread = threading.Thread(target=BulletThread, args=(recvJson["lookX"], recvJson["lookY"], recvJson["lookZ"], player))
                bulletThread.start()
        except Exception as e:
            print(e)
            nick = player.nick
            players.remove(player)
            print("Player disconnected:", nick, ":", len(players))
            break

def TCPFunc(tcp):
    while True:
        try:
            player = Player()
            player.socket, tmp = tcp.accept()
            data = player.socket.recv(1024).decode()
            recvJson = json.loads(data)
            player.nick = recvJson["nick"] # add mode control
            
            nickError = False
            for plyr in players: # nick control
                if plyr.nick == player.nick:
                    nickError = True
            
            if nickError:
                sendJson = {
                    "code": "1"
                }
                sendStr = json.dumps(sendJson)
                player.socket.sendall(sendStr.encode())
                continue
            else:
                SpawnPlayer(player)
                sendJson = {
                    "code": "0",
                    "map": "Walls",
                    "x": player.x,
                    "y": player.y,
                    "z": player.z
                }
                sendStr = json.dumps(sendJson)
                player.socket.sendall(sendStr.encode())
                players.append(player)
                print("Player connected:", player.nick, ":", len(players))
                playerThread = threading.Thread(target=PlayerHandler, args={player})
                playerThread.start()
        except Exception as e:
            print(f"Hata oluştu{e}")

def StartUDP():
    UDPServ = socketserver.UDPServer((ip, PORT), UDPHandler)
    UDPServ.serve_forever()

def StartTCP():
    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.bind((ip, PORT))
    tcpSocket.listen()
    TCPThread = threading.Thread(target=TCPFunc, args={tcpSocket})
    TCPThread.start()

def ResetGame():
    for player in players:
        player.healt = 100
        player.score = 0
        player.deadCount = 0
        player.isDead = False
        player.spawn = True

def Timing():
    gameDuration = 300
    endTime = time.perf_counter() + gameDuration
    while True:
        currentTime = time.perf_counter()
        timeClass.lastTime = int(endTime - currentTime)
        #print(lastTime)
        time.sleep((1000 / 256) / 100)
        if timeClass.lastTime <= 0:
            time.sleep(3)
            ResetGame()
            endTime = time.perf_counter() + gameDuration


players = []
timeClass = TimeClass()
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(0)
s.connect((socket.gethostbyname("www.google.com"), 1))
ip = s.getsockname()[0]
s.shutdown(2)
s.close()

print("Server starting on", ip, ":", PORT)

StartTCP()

udp = threading.Thread(target=StartUDP, args=())
udp.start()

timingThread = threading.Thread(target=Timing, args=())
timingThread.start()