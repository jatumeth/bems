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
        self._id_Smartplug_0 = "14"
        self._id_Smartplug_1 = "19"
        self._id_Smartplug_2 = "20"
        self._id_Smartplug_3 = "21"
        self._id_Smartplug_4 = "22"
        self._id_Smartplug_5 = "23"
        self._id_Smartplug_6 = "24"

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

        _url_append = self._address + '/api/meter/info/?format=json&username=' + self._username + '&api_key=' + self._api_key
        #print _url_append
        r = requests.get(_url_append)
        _theJSON = json.loads(r.content)
        #print _theJSON
        self.set_variable('Current', _theJSON["current"])
        self.set_variable('pf', _theJSON["pf"])
        self.set_variable('sys_kVarf', _theJSON["sys_kVarf"])
        self.set_variable('sys_kVarr', _theJSON["sys_kVarr"])
        self.set_variable('Power_Wf', _theJSON["sys_kWf"])
        self.set_variable('Power_Wr', _theJSON["sys_kWr"])
        self.set_variable('sys_pf', _theJSON["sys_pf"])
        self.set_variable('timestamp', _theJSON["timestamp"])
        self.set_variable('volt', _theJSON["volt"])

        print(" status = {}".format(self.get_variable('Current')))
        print(" Power Factor = {}".format(self.get_variable('pf')))
        print(" KVar_feed = {}".format(self.get_variable('sys_kVarf')))
        print(" KVar_reverse = {}".format(self.get_variable('sys_kVarr')))
        print(" Power_watt_feed = {}".format(self.get_variable('Power_Wf')))
        print(" Power_watt_reverse = {}".format(self.get_variable('Power_Wr')))
        print(" System_pf = {}".format(self.get_variable('sys_pf')))
        print(" timestamp = {}".format(self.get_variable('timestamp')))
        print(" volt = {}".format(self.get_variable('volt')))




def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    Smartmeter = API(model='SmartMeter',type='wifiLight',api='API3',address='http://192.168.1.13',username='acquired username',agent_id='LightingAgent')
    Smartmeter.getDeviceStatus()


if __name__ == "__main__": main()