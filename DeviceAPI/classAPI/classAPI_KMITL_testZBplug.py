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
        self.device_id = self.variables['device_id']
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

        try:
            if (self.device_id == "Smartplug_0"):
                self._id = self._id_Smartplug_0
            elif (self.device_id == "Smartplug_1"):
                self._id = self._id_Smartplug_1
            elif (self.device_id == "Smartplug_2"):
                self._id = self._id_Smartplug_2
            elif (self.device_id == "Smartplug_3"):
                self._id = self._id_Smartplug_3
            elif (self.device_id == "Smartplug_4"):
                self._id = self._id_Smartplug_4
            elif (self.device_id == "Smartplug_5"):
                self._id = self._id_Smartplug_5
            elif (self.device_id == "Smartplug_6"):
                self._id = self._id_Smartplug_6

            _url_append = self._address + '/api/appliances/' + self._id +'/info/?format=json&username=' + self._username + '&api_key=' + self._api_key
            #print _url_append
            r = requests.get(_url_append)
            _theJSON = json.loads(r.content)
            #print _theJSON
            self.set_variable('status', _theJSON[0]["value"])
            self.set_variable('volt', _theJSON[1]["value"])
            self.set_variable('current', _theJSON[2]["value"])
            self.set_variable('power', _theJSON[3]["value"])
            self.set_variable('energy_kWh', _theJSON[4]["value"])
            self.set_variable('PF', _theJSON[5]["value"])

            print(" status = {}".format(self.get_variable('status')))
            print(" volt = {}".format(self.get_variable('volt')))
            print(" current = {}".format(self.get_variable('current')))
            print(" power = {}".format(self.get_variable('power')))
            print(" Energy_kWh = {}".format(self.get_variable('energy_kwh')))
            print(" PF = {}".format(self.get_variable('PF')))

        except Exception as er:
            print er
            print('ERROR: classAPI_KMITL_testZBplug failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        try:
            if (self.device_id == "Smartplug_0"):
                self._id = self._id_Smartplug_0
            elif (self.device_id == "Smartplug_1"):
                self._id = self._id_Smartplug_1
            elif (self.device_id == "Smartplug_2"):
                self._id = self._id_Smartplug_2
            elif (self.device_id == "Smartplug_3"):
                self._id = self._id_Smartplug_3
            elif (self.device_id == "Smartplug_4"):
                self._id = self._id_Smartplug_4
            elif (self.device_id == "Smartplug_5"):
                self._id = self._id_Smartplug_5
            elif (self.device_id == "Smartplug_6"):
                self._id = self._id_Smartplug_6

            if postmsg.get('status') == "ON":
                self._set_On_Off_parameters = 1
            elif postmsg.get('status') == "OFF":
                self._set_On_Off_parameters = 0


            self._body_On_Off = {"cmd_name" : "set_On_Off" , "parameters" : {"setTo" : self._set_On_Off_parameters}}
            self._url_append = self._address + '/api/appliances/' + self._id + '/command/?username='+ self._username+'&api_key='+ self._api_key
            #print self._url_append
            #print self._body_On_Off
            r = requests.post(self._url_append,data = json.dumps(self._body_On_Off))
        except:
            print("ERROR: classAPI_KMITL_testZBplug  failure! @ setDeviceStatus")
            setDeviceStatusResult = False

    def identifyDevice(self):
        identifyDeviceResult = True
        try:

            if (self.device_id == "Smartplug_0"):
                self._id = self._id_Smartplug_0
            elif (self.device_id == "Smartplug_1"):
                self._id = self._id_Smartplug_1
            elif (self.device_id == "Smartplug_2"):
                self._id = self._id_Smartplug_2
            elif (self.device_id == "Smartplug_3"):
                self._id = self._id_Smartplug_3
            elif (self.device_id == "Smartplug_4"):
                self._id = self._id_Smartplug_4
            elif (self.device_id == "Smartplug_5"):
                self._id = self._id_Smartplug_5
            elif (self.device_id == "Smartplug_6"):
                self._id = self._id_Smartplug_6

            self._body_OFF = {"cmd_name": "set_On_Off", "parameters": {"setTo": 0}}
            self._body_ON = {"cmd_name": "set_On_Off", "parameters": {"setTo": 1}}
            self._url_append = self._address + '/api/appliances/' + self._id + '/command/?username=' + self._username + '&api_key=' + self._api_key

            if self.get_variable('status') == 1 :
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_OFF))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_ON))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_OFF))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_ON))
                print r
            elif self.get_variable('status') == 0 :
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_ON))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_OFF))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_ON))
                print r
                self.timeDelay(3)
                r = requests.post(self._url_append, data = json.dumps(self._body_OFF))
                print r

        except:
            print("ERROR: classAPI_KMITL_testZBplug  failure! @ identifyDevice")
            identifyDeviceResult = False

    def timeDelay(self,time_iden):  # specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            print("wait: {} sec".format(self.seconds))
            time.sleep(1)

def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    testZBplug = API(model='ZBplug',type='wifiLight',api='API3',address='http://192.168.1.13',username='acquired username',agent_id='LightingAgent',
                     device_id="Smartplug_3")
    testZBplug.getDeviceStatus()
    testZBplug.setDeviceStatus({"status":"OFF"})
    #testZBplug.identifyDevice()
    #testZBplug.identifyDevice()


if __name__ == "__main__": main()