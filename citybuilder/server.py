from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json
from citybuilder import messagehandler
from citybuilder.player import Player

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
                        print(message['username'] + " logged in")
                    else:
                        self.send_json({result: 1})
                elif message['type'] == "register":
                    if message['username'] not in players:
                        connections[message['username']] = self
                        players[message['username']] = Player(message['username'], message['password'])
                        self.player = players[message['username']]
                    else:
                        self.send_json({result: 2})
                else:
                    self.send_json({result: 3})
            else:
                messagehandler.handle_message(self, self.player, message)
        except Exception as e:
            print(e)

    def send_json(self, data):
        self.sendMessage(json.dumps(data))

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')

def run_server(config):
    server = SimpleWebSocketServer('', config['server']['port'], MainServerSocket)
    server.serveforever()
