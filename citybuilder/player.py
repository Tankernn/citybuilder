from passlib.hash import pbkdf2_sha256
import time
import json
from citybuilder import core
from random import randrange


class Unit:
    def __init__(self, key, level):
        self.type = key
        self.level = level


class Job:
    def __init__(self, player, product):
        self.player = player
        self.product = product
        self.finish_time = time.time() + product['time']

    def check_finish(self):
        if time.time() > self.finish_time or core.config['debug']:
            if self.product['type'] == "building":
                self.player.buildings[self.product['name']] += 1
            elif self.product['type'] == "research":
                self.player.research[self.product['name']] += 1
            elif self.product['type'] == "unit":
                self.player.units.append(Unit(self.product['name'], self.product['level']))
            elif self.product['type'] == "mission":
                mission = self.product['mission']
                if mission['type'] == "gather":
                    for resource, amount in mission['rewards']['resources'].items():
                        self.player.add_resource(resource, randrange(int(amount * 0.9), int(amount * 1.1)))
                    for unit in self.product['units']:
                        self.player.units.append(unit)
            return True
        return False


class Player:
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
        self.jobs = list()
        self.buildings = { key: 0 for key in core.config['building'] }
        self.units = [ Unit(unit['type'], unit['level']) for unit in core.config['general']['start']['units'] ]
        self.resources = { resource: core.config['general']['start'].get(resource, 0) for resource in core.config['general']['resources'] }
        self.research = { key: 0 for key in core.config['research'] }
        self.missions = list()

    def login(self, ws):
        self.ws = ws

    def set_password(self, password):
        self.password = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def add_job(self, product, requirements, cost):
        if not self.check_requirements(requirements):
            return {
                'result': 2
            }
        if not self.resource_check(cost):
            return {
                'result': 1
            }
        self.jobs.append(Job(self, product))

    def get_storage_space(self, resource):
        space = core.config['general']['storage'].get(resource, 0)
        for building in self.buildings.keys():
            spec = core.config['building'][building]
            if 'storage' in spec and self.buildings[building] > 0:
                space += spec['levels'][self.buildings[building] - 1]['capacity']
        return space

    def add_resource(self, resource, amount):
        self.resources[resource] += amount
        self.resources[resource] = min(self.get_storage_space(resource), self.resources[resource])

    def check_requirements(self, requirements):
        if 'buildings' in requirements:
            for building, level in requirements['buildings'].items():
                if self.buildings[building] < level:
                    return False
        if 'research' in requirements:
            for research, level in requirements['research'].items():
                if self.research[research] < level:
                    return False
        return True

    def resource_check(self, cost):
        """Checks if the resources are available,
        and takes them if that is the case."""
        cost = { k: cost[k] for k in cost.keys() if k != "time" }
        for resource, required in cost.items():
            if self.resources[resource] < required:
                return False
        for resource, required in cost.items():
            self.resources[resource] -= required
        return True

    def update(self, tick_length):
        while len(self.missions) < self.buildings['palace'] + 1:
            missions_available = [mission for mission in core.config['missions'] if self.check_requirements(mission['requirements'])]
            random_index = randrange(0, len(missions_available))
            self.missions.append(missions_available[random_index])

        self.jobs = [job for job in self.jobs if not job.check_finish()]
        # Resource generation
        for building in self.buildings.keys():
            spec = core.config['building'][building]
            if 'production' in spec and self.buildings[building] > 0:
                self.add_resource(spec['production'], spec['levels'][self.buildings[building] - 1]['rate'] * tick_length)

        self.ws.send_json({
            'username': self.username,
            'jobs': [{ 'product': job.product, 'finish_time': job.finish_time } for job in self.jobs],
            'buildings': self.buildings,
            'units': self.units,
            'resources': self.resources,
            'resources_max': { key: self.get_storage_space(key) for key in self.resources.keys() },
            'research': self.research,
            'missions': self.missions,
        })
