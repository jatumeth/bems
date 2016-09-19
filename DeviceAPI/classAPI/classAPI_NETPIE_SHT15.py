import time
import urllib2
import json
import requests
import  microgear.client as microgear

class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs):  # default color is white
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval',6000) #nothing to renew, right now

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

        _url_append = 'https://api.netpie.io/topic/RSDPEA/SMH/power?auth=5xeHHg4vpGAYTzj:N2hc2XaAriu2grlvRO0kEEglE'
        try:
            r = requests.get(_url_append)
            _theJSON = json.loads(r.content)
            _temp = float(_theJSON[0]['payload'].split(',')[0])
            _humid = float(_theJSON[0]['payload'].split(',')[1])
            self.set_variable('Temp', _temp)
            self.set_variable('Humid', _humid)
            print "Temperature = "
            print self.get_variable('Temp')
            print "Humidity = "
            print self.get_variable('Humid')
        except Exception as er:
            print er
            print('ERROR: classAPI_NETPIE_SHT15 failed to getDeviceStatus')

def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    SHT15sensor = API(model='SHT15',type='wifiLight',api='API3',address='https://api.netpie.io/topic/RSDPEA/SMH/power',username='acquired username',agent_id='LightingAgent')
    SHT15sensor.getDeviceStatus()


if __name__ == "__main__": main()