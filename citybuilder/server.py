from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
from citybuilder.messagehandler import MessageHandler
from citybuilder.player import Player
from citybuilder import core

connections = {}
players = {}

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
                    else:
                        self.send_json({'result': 1})
                elif message['type'] == "register":
                    if message['username'] not in players:
                        connections[message['username']] = self
                        players[message['username']] = Player(message['username'], message['password'])
                        self.player = players[message['username']]
                        self.player.login(self)
                    else:
                        self.send_json({'result': 2})
                else:
                    self.send_json({'result': 3})
            else:
                messagehandler.handle_message(self, self.player, message)
        except Exception as e:
            print("Exception in message handling:")
            print(e)

    def send_json(self, data):
        self.sendMessage(json.dumps(data))

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

def run_server():
    global messagehandler
    messagehandler = MessageHandler(core.config)
    server = SimpleWebSocketServer('', core.config['server']['port'], MainServerSocket)
    server.serveforever()
