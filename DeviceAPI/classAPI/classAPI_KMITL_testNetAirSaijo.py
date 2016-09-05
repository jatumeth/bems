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
        self._id_AirBedroom = "8"
        self._id_AirLiving1 = "17"
        self._id_AirLiving2 = "18"
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
    def getDeviceStatus(self, portmsg1):
         for k in portmsg1 :
            if k == 'BedroomAir':
                self._id   = self._id_AirBedroom
            elif k == 'LivingroomAir1':
                 self._id   = self._id_AirLiving1
            elif k == 'LivingroomAir2':
                 self._id   = self._id_AirLiving2
         self._url_append = self._address + '/api/appliances/' + self._id + '/info/?format=json&username=test&api_key=' + self._api_key
         r = requests.get(self._url_append)
         # print _url_append
         _theJSON = json.loads(r.content)
         # print _theJSON
         self.set_variable('status', _theJSON[0]["value"])
         self.set_variable('current_temperature', _theJSON[1]["value"])
         self.set_variable('set_temperature', _theJSON[2]["value"])
         self.set_variable('current_humidity', _theJSON[3]["value"])
         self.set_variable('set_humidity', _theJSON[4]["value"])
         self._mode = _theJSON[5]["value"]
         if self._mode == 0 :
            self.set_variable('mode' , "Cool")
         elif self._mode == 1 :
             self.set_variable('mode', "Fan")
         elif self._mode == 2:
            self.set_variable('mode', "Dry")
         elif self._mode == 3 :
            self.set_variable('mode', "Heat")
         elif self._mode == 4 :
            self.set_variable('mode', "Auto")
         self.set_variable('fan_speed', _theJSON[6]["value"])
         self.set_variable('fin_angle', _theJSON[7]["value"])

         print(" status = {}".format(self.get_variable('status')))
         print(" current_temperature = {}".format(self.get_variable('current_temperature')))
         print(" set_temperature = {}".format(self.get_variable('set_temperature')))
         print(" current_humidity = {}".format(self.get_variable('current_humidity')))
         print(" mode = {}".format(self.get_variable('mode')))
         print(" fan_speed = {}".format(self.get_variable('fan_speed')))
         print(" fin_angle = {}".format(self.get_variable('fin_angle')))

    def setDeviceStatus(self, postmsg):

        _body = []
        _data = self.convertPostMsg(postmsg)
        print _data
        for k in _data:
            print k
            if k == 'temp':
                _command = json.dumps({"cmd_name" : "set_temp" , "parameters" : {"setTo" : _data['temp']}})
                _body.append(_command)
            elif k == 'humidity':
                _command = json.dumps({"cmd_name": "set_humidity", "parameters": {"setTo": _data['humidity']}})
                _body.append(_command)
            elif k == 'fan_speed':
                _command = json.dumps({"cmd_name": "set_fan_speed", "parameters": {"setTo": _data['fan_speed']}})
                _body.append(_command)
            elif k == 'fin_angle':
                _command = json.dumps({"cmd_name": "set_fin_angle", "parameters": {"setTo": _data['fin_angle']}})
                _body.append(_command)
            elif k == 'mode':
                _command = json.dumps({"cmd_name": "set_mode", "parameters": {"setTo": _data['mode']}})
                _body.append(_command)
            elif k == 'status':
                _command = json.dumps({"cmd_name": "set_On_Off", "parameters": {"setTo": _data['status']}})
                _body.append(_command)
        print _data['_id']
        _url_append = self._address + '/api/appliances/' + _data['_id'] + '/command/?username=' + self._username + '&api_key=' + self._api_key
        for n in _body:
            r = requests.post(_url_append, data=n)

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        for k,v in postmsg.items():
            if k == 'temp':
                msgToDevice['temp'] = postmsg.get('temp')
            elif k == 'humidity':
                msgToDevice['humidity'] = postmsg.get('humidity')
            elif k == 'fan_speed':
                msgToDevice['fan_speed'] = postmsg.get('fan_speed')
            elif k == 'fin_angle':
                msgToDevice['fin_angle'] = postmsg.get('fin_angle')
            elif k == 'fan_speed':
                msgToDevice['fan_speed'] = postmsg.get('fan_speed')
            elif k == 'BedroomAir':
                msgToDevice['_id'] = self._id_AirBedroom
            elif k == 'LivingroomAir1':
                msgToDevice['_id'] = self._id_AirLiving1
            elif k == 'LivingroomAir2':
                msgToDevice['_id'] = self._id_AirLiving2
            elif k == 'mode':
                if postmsg.get('mode') == "cool":
                    msgToDevice['mode'] = 0
                elif postmsg.get('mode') == "fan":
                    msgToDevice['mode'] = 1
                elif postmsg.get('mode') == "dry":
                    msgToDevice['mode'] = 2
                elif postmsg.get('mode') == "heat":
                    msgToDevice['mode'] = 3
                elif postmsg.get('mode') == "auto":
                    msgToDevice['mode'] = 4
            elif k =='status':
                if postmsg.get('status') == "ON":
                    msgToDevice['status'] = 1
                elif postmsg.get('status') == "OFF":
                    msgToDevice['status'] = 0
            else:
                msgToDevice[k] = v
        return msgToDevice

def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    Airsaijo = API(model='Philips Hue',type='wifiLight',api='API3',address='http://192.168.1.13',username='acquired username',agent_id='LightingAgent')
    Airsaijo.getDeviceStatus({"LivingroomAir2":"0"})
    #Airsaijo.setDeviceStatus({"status":"ON", "LivingroomAir1":"0"})
    #time.sleep(10)
    #Airsaijo.setDeviceStatus({"BedroomAir":"0","fan_speed": "2", "temp" : "23"})
   # time.sleep(10)
    #Airsaijo.setDeviceStatus({"BedroomAir":"0","mode": "fan"})
    #time.sleep(10)
    #Airsaijo.setDeviceStatus({"temp": "18"})



    #Airsaijo.identifyDevice()


if __name__ == "__main__": main()