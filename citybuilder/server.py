from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
import traceback
from citybuilder.messagehandler import MessageHandler
from citybuilder.player import Player
from citybuilder import core

connections = {}
players = {}

def json_default(o):
    return o.__dict__

class MainServerSocket(WebSocket):

    def handleMessage(self):
        try:
            print("Message received: " + self.data)
            message = json.loads(self.data)
            if self not in connections.values():
                if message['type'] == "login":
                    if message['username'] in players and players[message['username']].check_password(message['password']):
                        connections[message['username']] = self
                        self.player = players[message['username']]
                        self.player.login(self)
                        print(message['username'] + " logged in")
                        self.send_json({'result': 0})
                    else:
                        self.send_json({'result': 1})
                elif message['type'] == "register":
                    if message['username'] not in players:
                        connections[message['username']] = self
                        players[message['username']] = Player(message['username'], message['password'])
                        self.player = players[message['username']]
                        self.player.login(self)
                        self.send_json({'result': 0})
                    else:
                        self.send_json({'result': 2})
                else:
                    self.send_json({'result': 3})
            else:
                messagehandler.handle_message(self, self.player, message)
        except Exception as e:
            print("Exception in message handling:")
            traceback.print_exc()

    def send_json(self, data):
        self.sendMessage(json.dumps(data, default=json_default))

    def handleConnected(self):
        print(self.address, 'connected')
        self.send_json(core.config)

    def handleClose(self):
        print(self.address, 'closed')

def run_server():
    global messagehandler
    messagehandler = MessageHandler(core.config)
    server = SimpleWebSocketServer('', core.config['server']['port'], MainServerSocket)
    server.serveforever()
