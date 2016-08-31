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
        self._username = "test"
        self._api_key = "576ce7157410fef051b42ed5ed393498dc58a1b5"
        self._address = "http://192.168.1.13"
        self._id = "14"
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
    status              GET    POST      ZBplug ON/OFF status
    current_consumption GET    POST      current_consumption
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
        _url_append = self._address + '/api/appliances/' + self._id +'/info/?format=json&username=' + self._username + '&api_key=' + self._api_key
        #print _url_append
        r = requests.get(_url_append)
        _theJSON = json.loads(r.content)
        #print _theJSON
        self.set_variable('status', _theJSON[0]["value"])
        self.set_variable('volt', _theJSON[1]["value"])
        self.set_variable('current', _theJSON[2]["value"])
        self.set_variable('power', _theJSON[3]["value"])
        self.set_variable('current_consumption', _theJSON[1]["value"])

        print(" status = {}".format(self.get_variable('status')))
        print(" volt = {}".format(self.get_variable('volt')))
        print(" current = {}".format(self.get_variable('current')))
        print(" power = {}".format(self.get_variable('power')))
        print(" current_consumption = {}".format(self.get_variable('current_consumption')))


    def setDeviceStatus(self, postmsg):
        if postmsg.get('status') == "ON":
            self._set_On_Off_parameters = 1
        elif postmsg.get('status') == "OFF":
            self._set_On_Off_parameters =  0

        self._body_On_Off = {"cmd_name" : "set_On_Off" , "parameters" : {"setTo" : self._set_On_Off_parameters}}
        self._url_append = self._address + '/api/appliances/' + self._id + '/command/?username='+ self._username+'&api_key='+ self._api_key
        #print self._url_append
        #print self._body_On_Off
        r = requests.post(self._url_append,data = json.dumps(self._body_On_Off))

def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    testZBplug = API(model='Philips Hue',type='wifiLight',api='API3',address='http://192.168.1.13',username='acquired username',agent_id='LightingAgent')
    testZBplug.getDeviceStatus()
    #testZBplug.setDeviceStatus({"status":"OFF"})
    #testZBplug.identifyDevice()


if __name__ == "__main__": main()