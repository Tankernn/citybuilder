from passlib.hash import pbkdf2_sha256
import time
import json


class Unit:
    def __init__(self, spec, level):
        self.spec = spec
        self.level = level


class Job:
    def __init__(self, player, product):
        self.player = player
        self.product = product
        self.finish_time = time.time() + product['time']

    def check_finish(self):
        if time.time() > self.finish_time:
            if self.product['type'] == "building":
                self.player.buildings[self.product['name']] += 1
            elif self.product['type'] == "unit":
                self.player.units.append(Unit(self.product['spec'], self.product['level']))
            return True
        return False


class Player:
    def __init__(self, username, password, config):
        self.username = username
        self.set_password(password)
        self.jobs = list()
        self.buildings = { key: 0 for key in config['building'] }
        self.units = list()
        self.resources = {
            'gold': 100,
            'wood': 100,
            'stone': 0,
        }
        self.research = {
            'footman': 1,
            'archer': 0,
        }

    def login(self, ws):
        self.ws = ws

    def set_password(self, password):
        self.password = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password)

    def add_job(self, product):
        self.jobs.append(Job(self, product))

    def update(self):
        self.jobs = [job for job in self.jobs if not job.check_finish()]
        self.ws.send_json({
            'username': self.username,
            'jobs': [{ 'product': job.product, 'finish_time': job.finish_time } for job in self.jobs],
            'buildings': self.buildings,
            'units': [unit.__dict__ for unit in self.units],
            'resources': self.resources,
            'research': self.research,
        })
