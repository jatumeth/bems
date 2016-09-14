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
        self._username = "test"
        self._api_key = "576ce7157410fef051b42ed5ed393498dc58a1b5"
        self._address = "http://192.168.1.13"
        self._id = "15"
        self.getDeviceStatus()


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
    current_temperature     GET    POST      Refrigerator ON/OFF status
    power                   GET    POST      Power
     ------------------------------------------------------------------------------------------

    '''

    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDeviceStatus() GET
    2. setDeviceStatus(postmsg) PUT
    '''

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        _url_append =  self._address + '/api/appliances/'+ self._id+'/info/?format=json&username=test&api_key='+ self._api_key
        r = requests.get(_url_append)
        #print _url_append
        _theJSON = json.loads(r.content)
        print _theJSON
        self.set_variable('current_temperature', _theJSON[0]["value"])
        self.set_variable('power', _theJSON[1]["value"])

        print(" Current_temperature = {}".format(self.get_variable('current_temperature')))
        print(" Power = {}".format(self.get_variable('power')))
        print("-----------------------------------------------------------------------------------")

    def setDeviceStatus(self, postmsg):
        _url_append = self._address + '/api/appliances/' + self._id + '/command/?username=' + self._username + '&api_key=' + self._api_key
        _body = []
        _data = self.convertPostMsg(postmsg)
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

    # print RefrigeratorZB.variables

    # RefrigeratorZB.getDeviceStatus()

    # print RefrigeratorZB.variables

    RefrigeratorZB.setDeviceStatus({"temp":"-5"})

    #RefrigeratorZB.identifyDevice()

    import time
    time.sleep(10)

    RefrigeratorZB.getDeviceStatus()


if __name__ == "__main__": main()