#coding=UTF-8
#This Python file uses the following encoding: utf-8

import logging
import logging.handlers
import colorlog
import time
import threading
from colorlog import ColoredFormatter
from maLogger import *
from maWebsocket import *

class HelloWorld:
    def __init__(self):
        self._logger = logging.getLogger('helloworld')

    def sayHello(self):
        self._logger.info('Hello, World!')

def startWsServer():
    _logger = logging.getLogger('cherrypy')
    _logger.info('cherrypy start.')
    WebSocketServer.start()

def microbitLoop():
    Microbit.bringUp()
    try:
        f = open( 'port.cfg', 'r' )
        pname = f.read()
        logging.info(pname)
        if(Microbit.openPort(pname)):
            logging.info("open com successfully")
            idleCount = 0 #记录多长时间没有收到消息
            while True:
                time.sleep(0.01)
                if(Microbit.port.in_waiting > 0):
                    idleCount = 0
                    Microbit.readline()
        else:
            logging.warning("open com failed")
    except BaseException as e:
        logging.error(e.strerror)

if __name__ == '__main__':
    initLogger()
    serialThread = threading.Thread(target = microbitLoop, name = "microbit message loop")
    serialThread.start()
    startWsServer()
