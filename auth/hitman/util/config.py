# import json
import yaml
import sys
import logging
import os
import os.path
from collections import namedtuple

# These can be overridden in the config file. 
# They are just here some sensible defaults
# so the module shill functions
BUILT_IN_DEFAULTS = { 
			'meta':{
				"version": "dev_build",
				"app" : "unknown",
				"config_directory": '.',				
				},
			'logging': {
				"logfile" : None,
				"loglvl" : "debug",
				"log_rotation": False,
				"logfmt" : '%(asctime)s %(name)s %(levelname)s: %(message)s',
				"datefmt" : '%d-%m-%y %I:%m:%S %p',
				"debugging" : False,
				}
}

# Instert default values for app config here 
# instead of mixing them with BUILT_IN_DEFAULTS
# These can be use to override BUILT_IN_DEFAULTS as well
APP_DEFAULTS = {
}

BUILT_IN_DEFAULTS.update(APP_DEFAULTS)

def parseLogLevel(text, default = 30):
	text = text.lower()
	levelValues = {
	 'critical' : 50,
		'error' : 40,
	  'warning' : 30,
		 'info' : 20,
		'debug' : 10
	}
	return levelValues.get(text, default)

def recursivelyUpdateDict(orig, new):
	updated = orig.copy()
	updateFrom = new.copy()
	for key, value in updated.items():
		if key in new:
			if not isinstance(value, dict):
				updated[key] = updateFrom.pop(key)
			else:
				updated[key] = recursivelyUpdateDict(value, updateFrom.pop(key))
	for key, value in updateFrom.items():
		updated[key] = value
	return updated

def createNamespace(mapping, name = 'config'):
	data = {}
	for key, value in mapping.items():
		if not isinstance(value, dict):
			data[key] = value
		else:
			data[key] = createNamespace(value, key)
	nt = namedtuple(name, list(data.keys()))
	return nt(**data)

def loadYAML(path):
	with open(path) as configFile:
 		return yaml.load(configFile)

def loadImports(mapping, configDir = '.'):
	if not isinstance(mapping, dict):
		return mapping
	loaded = mapping.copy()
	parsed = {}
	for key, value in loaded.items():
		if isinstance(value, str):
			if os.path.exists(configDir + '/' + value) and value.split('.')[-1] == 'yaml':
				parsed[key] = loadImports(loadYAML(configDir + '/' + value),  configDir)
			else:
				parsed[key] = value
		elif isinstance(value, dict):
			parsed[key] = loadImports(value, configDir)
		else:
			parsed[key] = value
	return parsed

def loadConfig(path = 'main.yaml'):
	configDir = os.path.dirname(path)
	loadedConfig = loadImports(loadYAML(path), configDir = configDir)

	config = recursivelyUpdateDict(BUILT_IN_DEFAULTS, loadedConfig)
	config = updateFromEnv(config)

	config['logging']['loglvl'] = parseLogLevel(config['logging']['loglvl']) # Parse the loglvl
	if config['logging']['loglvl'] <= 10:
		config['logging']['debugging'] = True
	return createNamespace(config) # Return the config for good measure

def loadFromEnv(key):
	return os.getenv(key, None)
	
def updateFromEnv(config, namespace = []):
	newConfig = config.copy()
	for key, value in config.items():
		if not isinstance(value, dict):
			configVar = '_'.join(namespace + [key.upper()])
			env = loadFromEnv(configVar)
			if env:
				newConfig[key] = env
		else:
			newConfig[key] = updateFromEnv(value, namespace=namespace + [key.upper()])
	return newConfig

configPath = None
if os.path.exists('config_stub.yaml'):
	configPath = loadYAML('config_stub.yaml').get('config_directory', None)
if loadFromEnv('META_CONFIG_DIRECTORY'):
	configPath = loadFromEnv('META_CONFIG_DIRECTORY')
if not configPath:
	configPath = BUILT_IN_DEFAULTS['meta']['config_directory']

def getParentModule(name):
	return sys.modules.get(name, None)

def loadByName(name, root = None):
	if isinstance(root, str):
		root = getParentModule(root)

	if root:
		sub = name.split('.')
		if len(sub) > 1:
			return loadByName('.'.join(sub[1:]), root = getattr(root, sub[0], None))
		else:
			return getattr(root, name,  None)
	else:
		raise KeyError('%s not found in config!'%name)

config = loadConfig(configPath + '/config.yaml')