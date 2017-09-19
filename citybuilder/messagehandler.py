import re
import json

class MessageHandler:

    def __init__(self, config):
        self.handlers = {
            "build": self.build,
            "train": self.train,
            "mission": self.mission,
        }
        self.config = config

    def resource_check(self, player, cost):
        cost = { k: cost[k] for k in cost.keys() if k != "time" }
        for resource, required in cost.items():
            if player.resources[resource] < required:
                return False
        for resource, required in cost.items():
            player.resources[resource] -= required
        return True

    def build(self, player, message):
        spec = self.config['building'][message['name']]
        level_index = player.buildings[message['name']]
        cost = spec['levels'][level_index]['cost']
        if not self.resource_check(player, cost):
            return {
                'result': 1
            }
        player.add_job({
            'type': "building",
            'time': cost['time'],
            'name': message['name'],
        })

    def train(self, player, message):
        spec = self.config['unit'][message['name']]
        if message['level'] > player.research[message['name']]:
            return {
                'result': 2
            }
        level_index = message['level'] - 1
        cost = spec['levels'][level_index]['cost']
        if not self.resource_check(player, cost):
            return {
                'result': 1
            }
        player.add_job({
            'type': "unit",
            'time': cost['time'],
            'name': message['name'],
            'level': message['level'],
        })

    def mission(self, player, message):
        mission = player.missions[message['index']]
        if not self.resource_check(player, mission['cost']):
            return {
                'result': 1
            }
        units = list()
        for index in sorted(message['units'], reverse=True):
            units.append(player.units.pop(index))

        player.add_job({
            'type': "mission",
            'time': mission['cost']['time'],
            'mission': mission,
            'units': units,
        })

    def handle_message(self, connection, player, message):
        handler = self.handlers[message['type']]
        if handler:
            result = handler(player, message)
            if result is None:
                result = {'result': 0}
            result['context'] = message
            connection.send_json(result)
        else:
             connection.send_json({'result': 404})
