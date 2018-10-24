# -*- coding: utf-8 -*-
import time
import json
import requests
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
            # print "Sent:     ", r
            # print "Received: ", self.decrypt(da[4:])
            self.getDeviceStatusJson(self.decrypt(da[4:]))
            # print (self.decrypt(da[4:]))
            #
            # self.dump1 = json.dumps(self.decrypt(da[4:]).decode("utf-8"))
            # self.getDeviceStatusJson(self.decrypt(da[4:]))
            self.printDeviceStatus()

            # try:
            #     self.getDeviceStatusJson(self.dump1)
            #     self.printDeviceStatus()
            # except Exception as err:
            #     print err

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
        # print ['system']['get_sysinfo']
        self.set_variable('label', str(conve_json["system"]['get_sysinfo']['dev_name']))

        if(str(conve_json["system"]['get_sysinfo']['relay_state'])=='0'):
            self.set_variable('device_status','off')
        elif(str(conve_json["system"]['get_sysinfo']['relay_state'])=='1'):
            self.set_variable('device_status','on')
        else:
            print 'error'

        # self.set_variable('device_status', str(conve_json["system"]['get_sysinfo']['relay_state']))
        self.set_variable('device_type', str(conve_json["system"]['get_sysinfo']['type']))
        # self.set_variable('status', str(conve_json["status"]).upper())
        # self.set_variable('power', str(conve_json["power"]))

    def printDeviceStatus(self):
        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" status = {}".format(self.get_variable('device_status')))
        # print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" type= {}".format(self.get_variable('device_type')))
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        ip = self.get_variable("ip")
        port = self.get_variable("port")
        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            # _data = json.dumps(self.convertPostMsg(postmsg))
            _data = (self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            try:
                print "sending command"
                sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_tcp.connect((ip, port))
                sock_tcp.send(self.encrypt(_data))
                da = sock_tcp.recv(2048)
                sock_tcp.close()
                # print "Sent:     ", _data
                # print "Received: ", self.decrypt(da[4:])
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
            # print postmsg['status']
            print msgToDevice
        # if 'STATUS' in postmsg.keys():
        #     msgToDevice['command'] = str(postmsg['STATUS'].lower().capitalize())
        #     print msgToDevice
        return msgToDevice

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():

    # -------------Kittchen----------------
    TpG = API(model='TPlinkPlug', api='API3', agent_id='TPlinkPlugAgent',types='plug',ip = '192.168.1.166',
                  port=9999)


    # TpG.setDeviceStatus({"status": "off"})
    # time.sleep(5)
    # TpG.getDeviceStatus()
    #
    # time.sleep(3)
    #
    # TpG.setDeviceStatus({"status": "Off"})
    # #
    # # time.sleep(5)
    #
    # TpG.getDeviceStatus()
if __name__ == "__main__": main()