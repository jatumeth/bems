import time
import urllib2
import json

import requests
class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs):  # default color is white
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval',6000) #nothing to renew, right now
        self.only_white_bulb = None
        # to initialize the only white bulb value
        self.set_variable('_username', "test")
        self.set_variable('_api_key', "576ce7157410fef051b42ed5ed393498dc58a1b5")
        self.set_variable('_address', "http://192.168.1.13")
        self.set_variable('_id', "15")
        #self.getDeviceStatus()


    def renewConnection(self):
        pass

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none

    # 2. Attributes from Attributes table
    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    status            GET    POST      Philips Hue ON/OFF status
    brightness        GET    POST      brightness percentage
    effect            GET    POST      Hue light effect 'none' or 'colorloop'
    color             GET    POST      temporary target heat setpoint (floating point in deg F)
     ------------------------------------------------------------------------------------------

    '''

    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDeviceStatus() GET
    2. setDeviceStatus(postmsg) PUT
    3. identifyDevice()
    '''

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        _url_append_get =  self.get_variable('_address')+ '/api/appliances/'+ self.get_variable('_id')+'/info/?format=json&username=test&api_key='+ self.get_variable('_api_key')
        r = requests.get(_url_append_get)
        print _url_append_get
        _theJSON = json.loads(r.content)
        #print _theJSON
        self.set_variable('current_temperature', _theJSON[0]["value"])
        self.set_variable('power', _theJSON[1]["value"])




        print(" Current_temperature = {}".format(self.get_variable('current_temperature')))
        print(" Power = {}".format(self.get_variable('power')))





    def setDeviceStatus(self, postmsg):
        _url_append = self.get_variable('_address') + '/api/appliances/' + self.get_variable(
            '_id') + '/command/?username=' + self.get_variable('_username') + '&api_key=' + self.get_variable(
            '_api_key')
        _body = []
        _data = self.convertPostMsg(postmsg)
       # _data = _data.encode(encoding='utf_8')
        print _data
        for k in _data:
            print k
            if k == 'temp':
                _command = json.dumps({"cmd_name" : "set_temp" , "parameters" : {"setTo" : _data['temp']}})
                _body.append(_command)
            elif k == 'motor_speed':
                _command = json.dumps({"cmd_name": "set_moter_speed", "parameters": {"setTo": _data['motor_speed']}})
                _body.append(_command)

        for n in _body:
            r = requests.post(_url_append, data=n)

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        for k,v in postmsg.items():
            if k == 'temp':
                msgToDevice['temp'] = postmsg.get('temp')
            elif k == 'motor_speed':
                msgToDevice['motor_speed'] = postmsg.get('motor_speed')
            else:
                msgToDevice[k] = v
        return msgToDevice

def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    RefrigeratorZB = API(model='Philips Hue',type='wifiLight',api='API3',address='http://192.168.1.13',username='acquired username',agent_id='LightingAgent')
    #RefrigeratorZB.getDeviceStatus()
    RefrigeratorZB.setDeviceStatus({"temp":"-5", "motor_speed": "128"})
    #RefrigeratorZB.identifyDevice()


if __name__ == "__main__": main()