from citybuilder import core
from random import randrange

class City:
    def __init__(self, owner, name, position):
        self.owner = owner
        self.name = name
        self.position = position
        self.buildings = { key: 0 for key in core.config['building'] }
        self.units = list()
        self.resources = { resource: 0 for resource in core.config['general']['resources'] }
        self.missions = list()

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

    def get_production(self, resource):
        production = 0
        for building, level in self.buildings.items():
            spec = core.config['building'][building]
            if 'production' in spec and spec['production'] == resource and level > 0:
                production += spec['levels'][self.buildings[building] - 1]['rate']
        return production

    def update(self, tick_length):
        while len(self.missions) < self.buildings['palace'] + 1:
            missions_available = [mission for mission in core.config['missions'] if self.check_requirements(mission['requirements'])]
            random_index = randrange(0, len(missions_available))
            self.missions.append(missions_available[random_index])
        # Resource generation
        for resource in self.resources.keys():
            self.add_resource(resource, self.get_production(resource) * tick_length)

    def __dict__(self):
        return {
            'buildings': self.buildings,
            'units': self.units,
            'resources': self.resources,
            'resources_production': {resource: self.get_production(resource) for resource in self.resources.keys()},
            'resources_max': { key: self.get_storage_space(key) for key in self.resources.keys() },
            'missions': self.missions,
        }
