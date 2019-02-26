# -*- coding: utf-8 -*-

import json
import requests

class API:

    def __init__(self,**kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval', 6000) # nothing to renew, right now
        self.only_white_bulb = None

    def renewConnection(self):
        pass

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none

    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label            GET          label in string
    illuminance      GET          illuminance
    temperature      GET          temporary target heat setpoint (floating point in deg F)
    battery          GET          percent battery of Fibaro censor
    motion           GET          motion  status (active/inactive)
    tamper           GET          tamper  status (active/inactive)
    unitTime         GET          Hue light effect 'none' or 'colorloop'
    type             GET          type
     ------------------------------------------------------------------------------------------

    '''

    '''
    API3 available methods:
    1. getDeviceStatus() GET
    '''    

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):
        try:
            headers = {"Authorization": self.get_variable("bearer")}
            url = str(self.get_variable("url") + self.get_variable("device"))

            print url
            r = requests.get(url, headers=headers, timeout=20)
            print headers
            print r.text
            print(" {0}Agent is querying its current status (status:{1}) please wait ...")
            format(self.variables.get('agent_id', None), str(r.status_code))
            if r.status_code == 200:
                getDeviceStatusResult = False
                self.getDeviceStatusJson(r.text)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                getDeviceStatusResult = False
            # Check the connectivity
            if getDeviceStatusResult==True:
                self.set_variable('offline_count', 0)
            else:
                self.set_variable('offline_count', self.get_variable('offline_count')+1)
        except Exception as er:
            print er
            print('ERROR: classAPI_Fibaro failed to getDeviceStatus')


    def getDeviceStatusJson(self, data):


        conve_json = json.loads(data)
        print conve_json
        self.set_variable('label', str(conve_json["label"]).upper())
        self.set_variable('ILLUMINANCE', str(conve_json["illuminance"]))
        self.set_variable('TEMPERATURE', str(conve_json["temperature"]))
        self.set_variable('BATTERY', str(conve_json["battery"]))
        self.set_variable('STATUS', str(conve_json["motion"]).upper())
        self.set_variable('MOTION', str(conve_json["motion"]).upper())
        self.set_variable('TAMPER', str(conve_json["tamper"]).upper())
        self.set_variable('HUMIDITY', float(0))
        self.set_variable('unitTime', conve_json["unitTime"])
        self.set_variable('device_type', str(conve_json["type"]).upper())

    def printDeviceStatus(self):
        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" illuminance = {}".format(self.get_variable('ILLUMINANCE')))
        print(" temperature = {}".format(self.get_variable('TEMPERATURE')))
        print(" battery = {}".format(self.get_variable('BATTERY')))
        print(" STATUS = {}".format(self.get_variable('STATUS')))
        print(" MOTION = {}".format(self.get_variable('MOTION')))
        print(" tamper = {}".format(self.get_variable('TAMPER')))
        print(" humidity = {}".format(self.get_variable('HUMIDITY')))
        print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" device_type= {}".format(self.get_variable('device_type')))
        print("---------------------------------------------")

    # ----------------------------------------------------------------------

def main():

    Fibaro = API(model='Fibaro', type='illuminance', api='API3', agent_id='20FIB_FibaroAgent',
                 url='https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/6e7197d2-42d1-47fa-9572-54213a47a778/illuminances/',
                 bearer='Bearer fe132119-a2f7-4078-82c3-586a3aa5ce87', device='02d25f11-256a-41a7-8b61-837798ac0a54')
    Fibaro.getDeviceStatus()


if __name__ == "__main__": main()