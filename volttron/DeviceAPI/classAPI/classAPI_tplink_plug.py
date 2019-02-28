# -*- coding: utf-8 -*-
import time
import json
import socket
from struct import pack

class API:
    def __init__(self,**kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval', 6000)
        self.only_white_bulb = None

    def renewConnection(self):
        pass

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none

    def encrypt(self,string):
        key = 171
        result = pack('>I', len(string))
        for i in string:
            a = key ^ ord(i)
            key = a
            result += chr(a)
        return result

    def decrypt(self,string):
        key = 171
        result = ""
        for i in string:
            a = key ^ ord(i)
            key = ord(i)
            result += chr(a)
        return result

    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label            GET          label in string
    status           GET          status
    unitTime         GET          time
    type             GET          type      
     ------------------------------------------------------------------------------------------

    '''

    '''
    API3 available methods:
    1. getDeviceStatus() GET
    2. setDeviceStatus() SET
    '''

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        getDeviceStatusResult = True
        try:

            ip = self.get_variable("ip")
            port = self.get_variable("port")
            r = '{"system":{"get_sysinfo":{}}}'
            sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_tcp.connect((ip, port))
            sock_tcp.send(self.encrypt(r))
            da = sock_tcp.recv(2048)
            sock_tcp.close()
            self.getDeviceStatusJson(self.decrypt(da[4:]))
            self.printDeviceStatus()


            if getDeviceStatusResult==True:
                self.set_variable('offline_count', 0)
            else:
                self.set_variable('offline_count', self.get_variable('offline_count')+1)
        except Exception as er:
            print er
            print('ERROR: classAPI_Tplink failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def getDeviceStatusJson(self, data):

        conve_json = json.loads(data)
        self.set_variable('label', str(conve_json["system"]['get_sysinfo']['dev_name']))

        if(str(conve_json["system"]['get_sysinfo']['relay_state'])=='0'):
            self.set_variable('device_status','off')
            self.set_variable('status', 'OFF')
        elif(str(conve_json["system"]['get_sysinfo']['relay_state'])=='1'):
            self.set_variable('device_status','on')
            self.set_variable('status', 'ON')
        else:
            print 'error'

        self.set_variable('device_type', str(conve_json["system"]['get_sysinfo']['type']))

    def printDeviceStatus(self):
        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" status = {}".format(self.get_variable('status')))
        print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" type= {}".format(self.get_variable('device_type')))
        print("---------------------------------------------")

    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        ip = self.get_variable("ip")
        port = self.get_variable("port")
        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            _data = (self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            try:
                print "sending command"
                sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_tcp.connect((ip, port))
                sock_tcp.send(self.encrypt(_data))
                da = sock_tcp.recv(2048)
                sock_tcp.close()

            except:
                print("ERROR: classAPI_Tplink connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The POST message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        commands = {
            'info': '{"system":{"get_sysinfo":{}}}',
            'ON': '{"system":{"set_relay_state":{"state":1}}}',
            'OFF': '{"system":{"set_relay_state":{"state":0}}}',
            'cloudinfo': '{"cnCloud":{"get_info":{}}}',
            'wlanscan': '{"netif":{"get_scaninfo":{"refresh":0}}}',
            'time': '{"time":{"get_time":{}}}',
            'schedule': '{"schedule":{"get_rules":{}}}',
            'countdown': '{"count_down":{"get_rules":{}}}',
            'antitheft': '{"anti_theft":{"get_rules":{}}}',
            'reboot': '{"system":{"reboot":{"delay":1}}}',
            'reset': '{"system":{"reset":{"delay":1}}}',
            'energy': '{"emeter":{"get_realtime":{}}}'
        }
        msgToDevice = {}
        if ('status' in postmsg.keys()):
            msgToDevice = commands[(postmsg['status'].upper())]
            print msgToDevice
        return msgToDevice
    # ----------------------------------------------------------------------

def main():

    tplinkplug = API(model='TPlinkPlug', api='API3', agent_id='TPlinkPlugAgent',types='switch',ip = '192.168.1.117',
                  port=9999)

    tplinkplug.getDeviceStatus()
    tplinkplug.setDeviceStatus({"status": "on"})
    time.sleep(2)
    tplinkplug.getDeviceStatus()
    tplinkplug.setDeviceStatus({"status": "off"})
    time.sleep(2)
    tplinkplug.getDeviceStatus()

if __name__ == "__main__": main()