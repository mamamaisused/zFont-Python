#coding=UTF-8
#This Python file uses the following encoding: utf-8

import logging
import logging.handlers
import colorlog
import time
from colorlog import ColoredFormatter
import os

def initLogger():
    # logpath = '.log'
    # if not os.path.exists(logpath):
    #     os.makedirs(logpath)
    # logfile = './.log/'+time.strftime("%Y%m%d", time.localtime()) + '.log'
    logfile = time.strftime("%Y%m%d", time.localtime()) + '.log'
    hl = logging.handlers.RotatingFileHandler(logfile, mode="w", maxBytes=50000, backupCount=3, encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    hl.setFormatter(formatter)
    logging.root.addHandler(hl)
    logging.root.setLevel(logging.DEBUG)

def maGetLogger(name):
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s:%(name)s:%(levelname)s: %(white)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

if __name__ == '__main__':
    pass