import yaml
import _thread
from . import server
import time

def main_loop():
    for player in list(server.players.values()):
        player.update()
    time.sleep(100)

if __name__ == '__main__':
    config = yaml.load(open("config/game.yaml"))['game']
    def run(*args):
        server.run_server(config)
        print("Websocket thread terminated.")
    _thread.start_new_thread(run, ())

    while 1:
        main_loop()
