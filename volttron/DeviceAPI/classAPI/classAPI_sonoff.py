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
            response = requests.get(
                url=str("http://"+ip+"/cm"),
                params={
                    "cmnd": 'state',
                },
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Host": str(ip),
                },
                data=json.dumps({

                })
            )
            rload = json.loads(response.text)
            status = rload['POWER']
            self.set_variable('device_type', str('Switch'))
            self.set_variable('status', str(status))
            self.set_variable('device_status', str(status))
            self.printDeviceStatus()

        except Exception as er:
            print er
            print('ERROR: classAPI_Tplink failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)


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
        try:
            status = postmsg['status']
            ip = self.get_variable("ip")
            if status == 'ON':
                msg ='Power On'
            elif status == 'on':
                msg = 'Power On'
            elif status == 'On':
                msg = 'Power On'
            elif status == 'OFF':
                msg = 'Power Off'
            elif status == 'Off':
                msg = 'Power Off'
            elif status == 'off':
                msg = 'Power Off'
            print msg
            response = requests.get(
                url="http://"+ip+"/cm",
                params={
                    "cmnd": msg,
                },
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Host": ip,
                },
                data=json.dumps({

                })
            )
            print response

        except Exception as er:
            print er
            print('ERROR: classAPI_Tplink failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)


    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():

    # -------------Kittchen----------------
    TpG = API(model='TPlinkPlug', api='API3', agent_id='TPlinkPlugAgent',types='plug',ip = '192.168.1.36',
                  port=9999)


    TpG.setDeviceStatus({"status": "ON"})
    time.sleep(2)
    TpG.getDeviceStatus()
    TpG.getDeviceStatus()
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