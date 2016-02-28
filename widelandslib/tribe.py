#!/usr/bin/env python
# encoding: utf-8

from conf import WidelandsConfigParser
from ConfigParser import NoSectionError, NoOptionError
import conf
from itertools import chain
import os.path as p
import re
from string import replace
import json
try:
    from settings import WIDELANDS_SVN_DIR
    basedir = WIDELANDS_SVN_DIR
except:
    basedir = p.join(p.dirname(__file__), p.pardir, p.pardir)

class BaseDescr(object):
    def __init__(self, tribe, name, descname, tdir, json):
        self.tribe = tribe
        self._tdir = tdir
        self._json = json

        self.name = name
        self.descname = descname

    @property
    def image(self):
        return p.abspath(p.join(self._tdir,self._json['icon']))

class Ware(BaseDescr):
    def __str__(self):
        return "Ware(%s)" % self.name

class Worker(BaseDescr):
    @property
    def outputs(self):
        rv = set(sorted(
            i.strip() for i in re.findall(r'\d+=\s*createitem\s*(\w+)',
                open(self._conf_file).read())
        ))
        return rv

    @property
    def becomes(self):
		 if 'becomes' in self._json:
			return self._json['becomes']
		 else:
			return None

    def __str__(self):
        return "Worker(%s)" % self.name

class Building(BaseDescr):
    @property
    def enhanced_building(self):
		 if 'enhanced' in self._json:
			return True
		 else:
			return False

    @property
    def base_building(self):
		 return None
       # NOCOM if not self.enhanced_building:
       # NOCOM            return None
       # NOCOM        bases = [b for b in self.tribe.buildings.values() if b.enhancement == self.name]
       # NOCOM        if len(bases) == 0 and self.enhanced_building:
       # NOCOM            raise Exception("Building %s has no bases in tribe %s" % (self.name, self.tribe.name))
       # NOCOM        if len(bases) > 1:
       # NOCOM            raise Exception("Building %s seems to have more than one base in tribe %s." % (self.name, self.tribe.name))
       # NOCOM        return bases[0]

    @property
    def enhancement(self):
		 if 'enhanced' in self._json:
			return self._json['enhanced']
		 else:
			return None

    @property
    def buildcost(self):
		 result = dict()
		 if 'buildcost' in self._json:
			for buildcost in self._json['buildcost']:
			  result[buildcost['name']] = buildcost['amount']
		 return result

    @property
    def size(self):
        return self._json['size']

class ProductionSite(Building):
    btype = "productionsite"
    @property
    def outputs(self):
		 result = dict()
		 if 'produced_wares' in self._json:
			for ware in self._json['produced_wares']:
			  result[ware['name']] = ware['amount']
		 return result

    @property
    def inputs(self):
		 result = dict()
		 if 'stored_wares' in self._json:
			for ware in self._json['stored_wares']:
			  result[ware['name']] = ware['amount']
		 return result

    @property
    def workers(self):
		 result = dict()
		 if 'workers' in self._json:
			for worker in self._json['workers']:
			  result[worker['name']] = worker['amount']
		 return result

    @property
    def recruits(self):
		 result = set()
		 if 'produced_workers' in self._json:
			for worker in self._json['produced_workers']:
			  result.add(worker['name'])
		 return result

class Warehouse(Building):
    btype = "warehouse"
    pass

class TrainingSite(ProductionSite):
    btype = "trainingsite"
    pass

class MilitarySite(Building):
    btype = "militarysite"
    @property
    def conquers(self):
        return self._conf.get("global", "conquers")

    @property
    def max_soldiers(self):
        return self._conf.get("global", "max_soldiers")

    @property
    def heal_per_second(self):
        return self._conf.getint("global", "heal_per_second")


class Tribe(object):
    def __init__(self, tribeinfo, base_directory, json_directory):
        self.name = tribeinfo['name']

        self._tdir = base_directory

        wares_file = open(p.normpath(json_directory + "/" + self.name + "_wares.json"), "r")
        waresinfo = json.load(wares_file)
        self.wares = dict()
        for ware in waresinfo['wares']:
			  # NOCOM print("Adding ware: " + ware['name'] + " " + ware['descname'])
			  descname = ware['descname'].encode('ascii', 'ignore')
			  #print(" -- " + descname)
			  self.wares[ware['name']] = Ware(self, ware['name'], descname, self._tdir, ware)

        workers_file = open(p.normpath(json_directory + "/" + self.name + "_workers.json"), "r")
        workersinfo = json.load(workers_file)
        self.workers = dict()
        for worker in workersinfo['workers']:
			  descname = worker['descname'].encode('ascii', 'ignore')
			  self.workers[worker['name']] = Worker(self, worker['name'], descname, self._tdir, worker)

        buildings_file = open(p.normpath(json_directory + "/" + self.name + "_buildings.json"), "r")
        buildingsinfo = json.load(buildings_file)
        self.buildings = dict()
        for building in buildingsinfo['buildings']:
			  descname = building['descname'].encode('ascii', 'ignore')
			  #descname = building['descname']
			  self.buildings[building['name']] = Building(self, building['name'], descname, self._tdir, building)

    def __str__(self):
        return "Tribe(%s)" % self.name
