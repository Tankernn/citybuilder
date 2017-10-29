from passlib.hash import pbkdf2_sha256
import time
import json
from citybuilder import core
from citybuilder.city import City
from random import randrange, uniform


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
                self.player.cities[self.product['city']].buildings[self.product['name']] += 1
            elif self.product['type'] == "research":
                self.player.research[self.product['name']] += 1
            elif self.product['type'] == "unit":
                self.player.cities[self.product['city']].units.append(Unit(self.product['name'], self.product['level']))
            elif self.product['type'] == "mission":
                mission = self.product['mission']
                if mission['type'] == "gather":
                    for resource, amount in mission['rewards']['resources'].items():
                        self.player.cities[self.product['city']].add_resource(resource, randrange(int(amount * 0.9), int(amount * 1.1)))
                    for unit in self.product['units']:
                        self.player.cities[self.product['city']].units.append(unit)
            return True
        return False


class Player:
    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
        self.jobs = list()
        self.cities = [ City(self, username + "\'s Capital", (uniform(0, core.config['general']['mapsize']), uniform(0, core.config['general']['mapsize']))) ]
        self.cities[0].units = [ Unit(unit['type'], unit['level']) for unit in core.config['general']['start']['units'] ]
        for resource, amount in core.config['general']['start']['resources'].items():
            self.cities[0].resources[resource] = amount
        self.research = { key: 0 for key in core.config['research'] }

    def login(self, ws):
        self.ws = ws

    def set_password(self, password):
        self.password = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def add_job(self, product, requirements, cost):
        if product['type'] in ("building", "research"):
            for job in self.jobs:
                if job.product == product:
                    return 3

        if product['type'] == "research":
            # Research must be conducted in the capital
            city = self.cities[0]
        else:
            city = self.cities[product['city']]

        if not city.check_requirements(requirements):
            return 2
        if not city.resource_check(cost):
            return 1
        self.jobs.append(Job(self, product))
        return 0

    def update(self, tick_length):
        for city in self.cities:
            city.update(tick_length)

        self.jobs = [job for job in self.jobs if not job.check_finish()]

        self.ws.send_json({
            'username': self.username,
            'jobs': [{ 'product': job.product, 'finish_time': job.finish_time } for job in self.jobs],
            'cities': [city.__dict__() for city in self.cities],
            'research': self.research,
        })
