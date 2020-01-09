#coding=UTF-8
#This Python file uses the following encoding: utf-8
#python 3

import serial
import logging
import zlib
from maLogger import *

class FilePorts:
    def __init__(self, version = 1):
        #可用的串口列表
        self._logger = maGetLogger('serial')
        self.port = serial.Serial()
        self.port.baudrate = 9600
        self.port.timeout = 3
        self.fileVersion = version
        self.filePages = list()

    def readline(self, eol=b'\n'):
        leneol = len(eol)
        line = ''
        while True:
            time.sleep(0.001)
            c = bytes.decode(self.port.read(1),'utf8')
            if c:
                line += c
                if line[-leneol:] == eol:
                    break
            else:
                break
        return line

    def openPort(self,name):
        self.port.port = name
        try:
            if not self.port.is_open:
                self.port.open()
                self._logger.info('open port %s success.'%name)
                return True
            else:
                self._logger.info('port %s is already open.'%name)
                return True
        except BaseException as e:
            self._logger.error(e)
            return False

    def loadFile(self, path):
        try:
            self.file = open(path, 'rb')
            self._img = self.file.read()
            return True
        except BaseException as e:
            self._logger.error(e)
            return False

    def checkFile(self):
        if self._img[7] != 0x08:
            print (self._img[7])
            self._logger.error('the file is not a stm32 bin file.')
            return False
        else:
            print('file check success.')
            return True

    '''
    把镜像切片为1k大小的几组
    '''
    def sliceImage(self):
        # 0xc1 写入APP区域 c1 00 size(2字节) pos(4字节) content(最多1024字节) 校验(1字节) (需要预先擦除)
        size = 1024
        count = 0
        pos = 0
        img = self._img
        self.totalsize = len(img) #文件大小
        while len(img) % 4 != 0:
            img += b'\xff'
        while len(img) > 0:
            perc = (1 - len(img) / self.totalsize) * 100
            pb = img[0:size]  #切片成1K
            # |68H|00H|lenH|lenL|posH1|posH2|posL1|posL2|...Data...|crc
            # 总共字节数 2(header)+2(len)+4(pos)+1024(data)+4(crc)
            # 只有data参与校验
            msg = b'\x68\x00' + len(pb).to_bytes(2, byteorder='little') + pos.to_bytes(4, byteorder='little') + pb
            crccheck = zlib.crc32(msg[8:]).to_bytes(4, byteorder='little')
            msg += crccheck
            count += 1
            self.filePages.append(msg)
            img = img[size:]
            pos += len(pb)
            if img == (b'\xff' * len(img)):  # 全0xff则跳过剩余部分
                print('slice file done')
                self.filePageNumber = count #分包数
                break

    def eraseInfo(self):
        timeout = 0
        self.port.write(b'BT+STDOWNLD\r\n')
        time.sleep(1) #等1秒钟等待设备准备好
        self.port.flushInput() #清数据
        msg = b'\x68\x02'
        self._logger.debug('waiting device response')
        for i in range(5):
            self._logger.debug('%d query device'%i)
            self.port.write(msg)
            time.sleep(1)
            if self.port.in_waiting > 0:
                ack = self.readline()
                self._logger.info(ack)
                if ack.find('BT+BOOT READY') >= 0:
                    return True
                else:
                    return False
        self._logger.error('erase failed.')
        return False

    def downLoad(self):
        timeout = 0
        ack = ''
        self._logger.info('start downloading...')
        #发送启动本次bin文件信息，启动下载
        startMsg = b'\x68\x01' + self.totalsize.to_bytes(4,'little') + \
                self.filePageNumber.to_bytes(2,'little') + self.fileVersion.to_bytes(2,'little')
        self.port.write(startMsg)
        while self.port.in_waiting == 0:
            time.sleep(0.01)
            timeout += 1
            if timeout > 50:
                self._logger.error('start downloading timeout')
                return
        
        ack = self.readline()
        if ack == 'BT+OK\r\n':
            self._logger.info('start OK.')
        else:
            self._logger.error('start failed.%s'%ack)
            return

        for i in range(len(self.filePages)):
            self.port.write(self.filePages[i])
            while self.port.in_waiting == 0:
                time.sleep(0.01)
                timeout += 1
                if timeout > 500:
                    self._logger.error('downloading no.%d/%d timeout error'%(i+1,self.filePageNumber))
                    return
            timeout = 0
            ack = self.readline()
            self._logger.info('page %d/%d get response: %s'%(i+1,self.filePageNumber,ack))
            if ack.find('OK') >= 0:
                if self.port.in_waiting > 0:
                    #如果还有数据
                    ack = self.readline()
                    self._logger.info(ack)
            else:
                break

if __name__ == '__main__':
    initLogger()
    stm32File = FilePorts()
    #加载文件
    if(stm32File.loadFile('./binfiles/hc01_app.bin')):
        #校验文件
        if(stm32File.checkFile()):
            #切分文件
            stm32File.sliceImage()
            #打开串口
            if(stm32File.openPort('COM9')):
                #擦除信息页
                if(stm32File.eraseInfo()):
                    #下载程序
                    stm32File.downLoad()