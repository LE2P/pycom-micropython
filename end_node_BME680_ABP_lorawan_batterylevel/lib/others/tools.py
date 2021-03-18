# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2019 schade <schade@schadelin-System>
#

'''
tools.py :
    the tools file is dedicated to store useful functions.
'''
rgb_code_status = {
    "INIT": 0x7f7f00,   # Yellow
    "SLEEP": 0x00047f,  # Blue heartbeat
    "RUN": 0x007f00,    # Green
    "ACTIVATION": 0x7f005f,  # purple
    "ERROR": 0x7f0000,  # RED
}

def set_state_led(status):
    import pycom
    #Disable heartbeat
    status = status.upper()
    if status in rgb_code_status:
        if status is "SLEEP":
            pycom.heartbeat(True)
        else:
            pycom.heartbeat(False)
            pycom.rgbled(rgb_code_status[status])

    else:
        raise_error("Try to set led with Undefined status {}".format(status))



def create_logger(name, level, file):
    import lib.others.logging as logging

    print("Create log file {} with level {}".format(file, level))
    if level == 'DEBUG':
        loglevel = logging.DEBUG
    elif level == 'INFO':
        loglevel = logging.INFO
    elif level == 'WARNING':
        loglevel = logging.WARNING
    else:
        loglevel = logging.ERROR

    try:
        logging.basicConfig(name, level=loglevel, filename=file)
        log = logging.getLogger(name)
    except Exception as ex:
        print("Error logger creation !!! {}, {}, {}".format(name, level, file))
    return log


def raise_error(error, fromWho="Scenario"):
    '''
    Function dedicated to raise error (print + log + led)
    '''
    import pycom
    import time
    import lib.others.logging as logging
    log = logging.getLogger(fromWho)
    set_state_led("ERROR")
    log.error("ERROR : {}".format(error))

def read_json(filename, path):
    """Accepts a file name and loads it as a json object.
    Args:
        filename   (str): Filename to be loaded.
        path       (str): Directory path to use.
    Returns:
        obj: json object
    """
    result = []
    try:
        import ujson
        with open(path + filename + ".json", "r") as entry:
            print("Read {}{}.json".format(path, filename))
            result = ujson.load(entry)
    except Exception as ex:
        raise_error(ex)

    else:
        entry.close()
        return result
