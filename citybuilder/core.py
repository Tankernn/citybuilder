import yaml
import _thread
from . import server
import time

def main_loop():
    for player in list(server.players.values()):
        player.update(config, time.time() - main_loop.last_tick)
    main_loop.last_tick = time.time()
    time.sleep(1)

main_loop.last_tick = time.time()

if __name__ == '__main__':
    global config
    config = yaml.load(open("config/game.yaml"))['game']
    def run(*args):
        server.run_server(config)
        print("Websocket thread terminated.")
    _thread.start_new_thread(run, ())

    while 1:
        main_loop()
