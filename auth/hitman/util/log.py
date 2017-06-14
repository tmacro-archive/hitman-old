import logging
from .config import config

class Whitelist(logging.Filter):
    def __init__(self, *whitelist):
        self.whitelist = [logging.Filter(name) for name in whitelist]

    def filter(self, record):
        return any(f.filter(record) for f in self.whitelist)

class Blacklist(Whitelist):
    def filter(self, record):
        return not Whitelist.filter(self, record)



def setupLogging():
	rootLogger = logging.getLogger()
	rootLogger.setLevel(config.logging.loglvl)

	formatter = logging.Formatter(fmt=config.logging.logfmt, datefmt=config.logging.datefmt)

	streamHandler = logging.StreamHandler()
	streamHandler.setFormatter(formatter)

	rootLogger.addHandler(streamHandler)

	if config.logging.logfile:
		if config.logging.log_rotation:
			handler = logging.handlers.RotatingFileHandler(
				config.logging.logfile, maxBytes=10*1024*1024, backupCount=2)
		else:
			handler = logging.FileHandler(config.logging.logfile)

		handler.setFormatter(formatter)
		rootLogger.addHandler(handler)

	# for handler in logging.root.handlers:
		# handler.addFilter(Blacklist(some, stuff, here))
	baseLogger = logging.getLogger(config.meta.app)
	baseLogger.info('Starting %s: version %s'%(config.meta.app, config.meta.version))
	return baseLogger

BASE_LOGGER = setupLogging()

def getLogger(name):
	# configModule = sys.modules[__name__]
	# baselogger = getattr(configModule, 'BASE_LOGGER', None)
	baselogger = BASE_LOGGER
	if baselogger:
		return baselogger.getChild(name)
	else:
		return logging.getLogger(name)