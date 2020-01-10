#!/usr/bin/env python
#coding=UTF-8
#This Python file uses the following encoding: utf-8

'''IDGET000000001'''

from ws4py.client.threadedclient import WebSocketClient as wsclient
import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
import time
import yaml
import json
import threading
from maLogger import *
from maSerial import *

'''全局变量'''
gComs = maPorts()

Microbit = maPorts()

class ComReplyParam:
    SETSUCCESS = 0
    SETFAIL = -1
    GETSUCCESS = 2
    GETFAIL = -2

class WingbotRoot():
    def __init__(self):
        self.data = dict()

'''
WingbotLocalMsgParse
@description: 本地websocket服务器消息解析
{
    "sender":"python"/"js",
    "opCode":"info",
    "data":{
        "param":0,
        "description":''
    }
}
'''

'''每次收到新的消息都会创建一个新的这个类的实例'''
class WingbotLocalMsgParse(WebSocket):
    def __init__(self, *args, **kargs):
        WebSocket.__init__(self, *args, **kargs)
        self.isAlive = True
        self._logger =logging.getLogger('python')
        self.comMessage = {
            "sender":"python",
            "opCode":"info",
            "data":{
                "param":0,
                "discription":''
            }
        }
        self._serialThread = threading.Thread(target = self.serialLoop, name = "wait serial data")
        self._serialThread.start()
        print("_________init_________")

    def opened(self):
        """
        Called by the server when the upgrade handshake
        has succeeded.
        """
        if Microbit.isConnected == True:
            self.send('ready')
        else:
            self.send('not ready')

    def serialLoop(self):
        while self.isAlive:
            time.sleep(0.01)
            if Microbit.state == 'DataReady':
                Microbit.setIdle()
                m = Microbit.getData()
                self._logger.info(m)
                try:
                    self.send(m)
                except BaseException as e:
                    self._logger.error(e)

    def closed(self, code, reason=None):
        self._logger.warning('websocket closed')
        self.isAlive = False

    def received_message(self,message):
        self._logger.debug(message)
        print(message)
        message_dict = yaml.safe_load(message.data)
        if message_dict['opCode'] == 'test':
            self.send(self.testReply())
        elif message_dict['opCode'] == 'com_list':
            gComs.bringUp()
            self.send(self.comListReply())
        elif message_dict['opCode'] == 'open_com':
            ret = gComs.openPort(message_dict['data']['param'])
            if ret:
                self.send(self.comTaskSuccess())
            else:
                self.send(self.comTaskFail())
        elif message_dict['opCode'] == 'get_bitstate':
            self.send(self.comStateReply(Microbit.state))

    def testReply(self):
        self.comMessage['opCode'] = 'test'
        self.comMessage['data'] = dict()
        self.comMessage['data']['param'] = 58
        self.comMessage['data']['description'] = 'this is a test message'
        return self.__toJson()

    '''
    {
        "opCode":"com_list",
        "data":{
            "description":'',
            "comList":[{
                "name":"COM4",
                "hwid":""
            },
            {
                "name":"COM5",
                "hwid":""
            }
            ]
        }
    }
    '''
    def comListReply(self):
        self.comMessage['opCode'] = 'com_list'
        self.comMessage['data'] = dict()
        self.comMessage['data']['description'] = '%d avialable serial port found'%(len(gComs.portList))
        self.comMessage['data']['comList'] = gComs.portList
        return self.__toJson()

    def comTaskSuccess(self, param, message='succuss'):
        #0表示成功
        return self.comTaskReply(param,message)

    def comTaskFail(self, param, message='faled'):
        #-1表示失败
        return self.comTaskReply(param, message)

    def comTaskReply(self, param, message):
        self.comMessage['opCode'] = 'com_reply'
        self.comMessage['data'] = dict()
        self.comMessage['data']['param'] = param
        self.comMessage['data']['description'] = message
        return self.__toJson()

    def comStateReply(self, param):
        self.comMessage['opCode'] = 'get_bitstate'
        self.comMessage['data'] = dict()
        self.comMessage['data']['param'] = param
        self.comMessage['data']['brief'] = "microbit state"
        return self.__toJson()

    def __toJson(self):
        self._logger.debug(self.comMessage)
        print(self.comMessage) 
        return json.dumps(self.comMessage)

'''
WingbotServer
@description: 本地websocket服务
'''
class WingbotServer(object):
    @cherrypy.expose
    def index(self):
        return 'Wingbot Local Server.'

    @cherrypy.expose
    def ws(self):
        pass

class WebSocketServer():
    @staticmethod
    def start(ipaddr = '0.0.0.0',ws_handler = WingbotLocalMsgParse):
        cherrypy.config.update({'server.socket_host': ipaddr,
                                'server.socket_port': 19002})
        WebSocketPlugin(cherrypy.engine).subscribe()
        cherrypy.tools.websocket = WebSocketTool()
        cherrypy.quickstart(WingbotServer(), '/', config={'/ws': {'tools.websocket.on': True,
                                                 'tools.websocket.handler_cls': ws_handler}}) 