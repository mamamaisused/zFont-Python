#coding=UTF-8
#This Python file uses the following encoding: utf-8

import serial
import serial.tools.list_ports as serialPortList
import logging
import json
import time
from maLogger import *

#获取可用的串口列表，并选择可用的口发送数据
class maPorts:
    def __init__(self):
        #可用的串口列表
        self.portList = list()
        self._logger = logging.getLogger('serial')
        self.port = serial.Serial()
        self.port.baudrate = 9600
        self.port.timeout = 3
        self.state = "Idle"
        self.isConnected = False #串口是否连接成功
    
    def bringUp(self):
        self.portList = list()
        for port in serialPortList.comports():
            port_dict = {
                "name": port.device,
                "hwid": port.hwid
            }
            self.portList.append(port_dict)
            self._logger.info(json.dumps(port_dict))

    def openPort(self,name):
        self.port.port = name
        try:
            if not self.port.is_open:
                self.port.open()
                self._logger.info('open port %s success.'%name)
                self.isConnected = True
                return True
            else:
                self._logger.info('port %s is already open.'%name)
                return True
        except BaseException as e:
            self._logger.error(e)
            return False

    def readline(self, eol=':'):
        self.data = self.port.read_until(eol)
        self.data = self.data[0:len(self.data)-1]
        self.state = 'DataReady'
        return self.data

    def getData(self):
        tmp = self.data
        self.data = ''
        return tmp

    def upDataState(self, msg):
        if msg == '$Up:':
            self.state = 'Up'
        elif msg == '$Down:':
            self.state = 'Down'
        elif msg == '$Left:':
            self.state = 'Left'
        elif msg == '$Right:':
            self.state = 'Right'
        elif msg == '$Shake:':
            self.state = 'Shake'
        elif msg == '$A:':
            self.state = 'A'
        elif msg == '$B:':
            self.state = 'B'
    
    def setIdle(self):
        self.state = 'Idle'

if __name__ == '__main__':
    initLogger()
    microbit = maPorts()
    microbit.bringUp()
    print(microbit.openPort('COM9'))
    idleCount = 0 #记录多长时间没有收到消息
    while True:
        time.sleep(0.001)
        if(microbit.port.in_waiting > 0):
            idleCount = 0
            s = microbit.port.read_until(':')
            s = s[0:len(s)-1]
            microbit.upDataState(s)
            print(s)
        else:
            idleCount += 1
            if idleCount > 100:
                idleCount = 0
                microbit.setIdle()
            #print(string[0:2])