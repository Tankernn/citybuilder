import re
import json

class MessageHandler:

    def __init__(self, config):
        self.handlers = {
            "build": self.build,
            "train": self.train,
            "mission": self.mission,
            "research": self.research,
        }
        self.config = config

    def build(self, player, message):
        spec = self.config['building'][message['name']]
        level_index = player.buildings[message['name']]
        requirements = spec['levels'][level_index]['requirements']
        cost = spec['levels'][level_index]['cost']
        return player.add_job({
            'type': "building",
            'time': cost['time'],
            'name': message['name'],
        }, requirements, cost)

    def train(self, player, message):
        spec = self.config['unit'][message['name']]
        level_index = message['level'] - 1
        requirements = spec['levels'][level_index]['requirements']
        cost = spec['levels'][level_index]['cost']
        return player.add_job({
            'type': "unit",
            'time': cost['time'],
            'name': message['name'],
            'level': message['level'],
        }, requirements, cost)

    def mission(self, player, message):
        mission = player.missions[message['index']]
        units = list()
        for index in sorted(message['units'], reverse=True):
            units.append(player.units.pop(index))

        return player.add_job({
            'type': "mission",
            'time': mission['cost']['time'],
            'mission': mission,
            'units': units,
        }, {}, mission['cost'])

    def research(self, player, message):
        spec = self.config['research'][message['name']]
        level_index = player.research.get(message['name'], 0)
        requirements = spec['levels'][level_index]['requirements']
        cost = spec['levels'][level_index]['cost']
        return player.add_job({
            'type': "research",
            'time': cost['time'],
            'name': message['name'],
        }, requirements, cost)

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
