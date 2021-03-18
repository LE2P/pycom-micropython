"""
logging.py
from : https://github.com/micropython/micropython-lib/blob/master/logging/logging.py
add file management by gfo, quick fix
File dedicated to manage logging file
"""
import sys
import os, uos
import utime


CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_stream = sys.stdout

class Logger:

    level = NOTSET

    def __init__(self, name, file):
        self.name = name
        print("Create logger file {} with file {}".format(name, file))
        self.file = file
        if self.file is not None:
            f = open(self.file, 'w')
            # TODO : RTC TIME ENabled
            f.write("Logger file initilized at : {}".format(utime.time()))
            f.close()


    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def log(self, level, msg, *args):
        if level >= (self.level or _level):
            with open(self.file, 'a') as logfile:
                if not args:
                    print("{} - {} - {} - {}".format(self.name, self._level_str(level), utime.time(), msg), file=_stream)
                    logfile.write("{} - {} - {} - {}".format(self.name, self._level_str(level), utime.time(), msg) )
                else:
                    print("{} - {} - {} - {}".format(self.name, self._level_str(level), utime.time(), msg % args), file=_stream )
                    logfile.write("{} - {} - {} - {}".format(self.name, self._level_str(level), utime.time(), msg % args) )
                logfile.write("\n")

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)

    def exc(self, e, msg, *args):
        self.log(ERROR, msg, *args)
        sys.print_exception(e, _stream)

    def exception(self, msg, *args):
        self.exc(sys.exc_info()[1], msg, *args)


_level = INFO
_loggers = {}

# TODO :
# file shall not be hard defined
def getLogger(name, file="log.txt"):
    if name in _loggers:
        return _loggers[name]
    l = Logger(name, file = file)
    _loggers[name] = l
    return l

def info(msg, *args):
    getLogger(None).info(msg, *args)

def debug(msg, *args):
    getLogger(None).debug(msg, *args)

def checkFileExist(file):
    for f in os.listdir():
        if file == f:
            uos.remove(f)
    return

def basicConfig(name, level=INFO, filename=None, stream=None, format=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
       # Create logger with file
        checkFileExist(filename)
        l = Logger(name, file = filename)
        _loggers[name] = l
        # print("logging.basicConfig: filename arg is not supported")
    if format is not None:
        print("logging.basicConfig: format arg is not supported")
