'''
Created on Jun 26, 2014

@author: Warodom Khamphanchai
'''
#!/usr/bin/python2.7
'''
This API1 class is for an agent that want to communicate/monitor/control
devices that compatible with Radio Thermostat Wi-Fi USNAP Module API Version 1.3 March 22, 2012
http://www.radiothermostat.com/documents/rtcoawifiapiv1_3.pdf
Warodom Khamphanchai 3/25/2014
'''
import urllib2
import json
import time
import base64

#__version__ "1.0"

debug = False

class API:
    #1. constructor : gets call everytime when create a new class
    #requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs): #default color is white
        #Initialized common attributes
        self.variables = kwargs

    #These set and get methods allow scalability
    def set_variable(self,k,v): #k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None) #default of get_variable is none

    #2. Attributes from Attributes table
    '''
    Attributes:
    GET: temp, override, tstate, fstate, t_type_post
    GET/POST: time=[day, hour, minute], tmode, t_heat, t_cool, fmode, hold
    POST: energy_led
    ------------------------------------------------------------------------------------------
    temp            GET              current temp(deg F)
    override        GET              target temp temporary override (0:disabled, 1:enabled)
    tstate          GET              HVAC operating state (0:OFF,1:HEAT,2:COOL)
    fstate          GET              fan operating state (0:OFF, 1:ON)
    t_type_post
    time            GET    POST      Thermostat's internal time (day:int,hour:int,minute:int)
    tmode           GET    POST      Thermostat operating mode (0:OFF,1:HEAT,2:COOL,3:AUTO)
    t_heat          GET    POST      temporary target heat setpoint (floating point in deg F)
    t_cool          GET    POST      temporary target
    .cool setpoint (floating point in deg F)
    fmode           GET    POST      fan operating mode (0:AUTO,1:AUTO/CIRCULATE,2:ON)
    hold            GET    POST      target temp hold status (0:disabled, 1:enabled)
    energy_led             POST      energy LED status code (0:OFF,1:Green,2:Yellow,4:Red)
    ------------------------------------------------------------------------------------------
    '''

    #3. Capabilites (methods) from Capabilities table
    '''
    API1 available methods:
    1. getDeviceModel(url) GET
    2. getDeviceStatus(url) GET
    3. setDeviceStatus(url, postmsg) POST
    4. identifyDevice(url, idenmsg) POST
    '''
    def discoverHub(self, username, password):
        # ACCESS_TOKEN = "ce49226a-5383-42dc-832d-12d2017569ca"
        body = 'https://graph.api.smartthings.com/api/hubs'
        _request = urllib2.Request(body)
        print "123"
        print _request.
        # _request.add_header("Content-Type","application/json;charset=UTF-8")
        # username = 'kwarodom@hotmail.com'
        # password = 'w3300136'
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        _request.add_header("Authorization", "Basic %s" % base64string)
        print "456"
        print _request.data
        deviceInfoUrl = urllib2.urlopen(_request)  # when include data this become a POST command
        print(" {0}Agent is querying SmartThings Hub Info please wait ...".format(self.variables.get('agent_id',None)))
        if deviceInfoUrl.getcode()==200:
            x = deviceInfoUrl.read().decode("utf-8")
            self.getHubInfoJson(x)
            self.printHubInfo()

    def getHubInfoJson(self, data):
        # Use the json module to load the string data into a dictionary
        _theJSON = json.loads(data)
        # print _theJSON[0]
        for k, v in _theJSON[0].items():
            if debug: print (k, v)
            self.set_variable('hub_'+str(k), v)
        #TODO find way to get hub_ip and hub_macaddress
        if self.get_variable('hub_zigbeeId') == 'D052A80027000001':
            self.set_variable('hub_ip_address', '38.68.239.90')
            self.set_variable('hub_macaddress', 'D052A8002700')

    def printHubInfo(self):
        print(" The current SmartThings Hub Info is as follows:")
        for k, v in self.variables.items():
            if str(k).find('hub_') == 0:
                print(" {} = {}".format(k, self.get_variable(k)))

    def getHubDevices(self, username, password):
        body = 'https://graph.api.smartthings.com/api/hubs/'+str(self.get_variable('hub_id'))+'/devices'
        print body
        _request = urllib2.Request(body)
        # _request.add_header("Content-Type","application/json;charset=UTF-8")
        # username = 'kwarodom@hotmail.com'
        # password = 'w3300136'
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        _request.add_header("Authorization", "Basic %s" % base64string)
        deviceInfoUrl = urllib2.urlopen(_request) #when include data this become a POST command
        print(" {0}Agent is querying SmartThings Hub Devices please wait ...".format(self.variables.get('agent_id',None)))
        if deviceInfoUrl.getcode() == 200:
            x = deviceInfoUrl.read().decode("utf-8")
            self.getHubDevicesJson(x)
            # self.printHubDevices()
        return self.newSmartThingsDevices

    def getHubDevicesJson(self, data):
        # Use the json module to load the string data into a dictionary
        _theJSON = json.loads(data)
        # print len(_theJSON)
        num_devices = len(_theJSON)
        self.newSmartThingsDevices = list()
        print "SmartThings >> there are {} devices registered for the hub name {}:"\
            .format(num_devices, self.get_variable('hub_name'))
        for index in range(0, num_devices):
            _theDeviceJSON = _theJSON[index]
            for k, v in _theDeviceJSON.items():
                if k == 'id':
                    device_id = str(v)
                    self.newSmartThingsDevices.append(device_id)
            for k, v in _theDeviceJSON.items():
                if debug: print (k, v)
                if k != 'currentStates':
                    self.set_variable('hub_device_'+device_id+'_'+str(k), v)
                elif k == 'currentStates':
                    # print _theDeviceJSON['currentStates']
                    size_currentStates = len(_theDeviceJSON['currentStates'])
                    for index in range(0, size_currentStates):
                        # print _theDeviceJSON['currentStates'][index]
                        _data_point = _theDeviceJSON['currentStates'][index]['name']
                        _data_value = _theDeviceJSON['currentStates'][index]['value']
                        self.set_variable('hub_device_'+device_id+'_currentStates_'+str(_data_point), _data_value)
            else:
                    pass
            self.printHubDevice(device_id)
            print '---------------------------------------'

    def printHubDevice(self, _device_id):
        print " The current SmartThings parameters for device {} are as follows:".format(_device_id)
        for k, v in self.variables.items():
            if str(k).find('hub_device_'+_device_id) == 0:
                print(" {} = {}".format(k, self.get_variable(k)))

    #method2: GET Open the URL and read the data
    def getDeviceStatus(self):
        # ACCESS_TOKEN = "ce49226a-5383-42dc-832d-12d2017569ca"
        body = self.get_variable("address_get")
        # body = self.get_variable("address") + "switches/currentStatus"
        # body = 'https://graph.api.smartthings.com/api/smartapps/installations/c0d1e845-fd65-4b30-a1ed-03c75a5a9d60/switches/currentStatus'
        _request = urllib2.Request(body)
        base64string = base64.encodestring('%s:%s' % (self.get_variable("smt_username"),
                                                      self.get_variable("smt_password"))).replace('\n', '')
        _request.add_header("Authorization", "Basic %s" % base64string)
        # _request.add_header("Content-Type", "application/json;charset=UTF-8")
        # _request.add_header("Authorization","Bearer %s" % ACCESS_TOKEN)
        # _request.add_header("Authorization", self.get_variable('auth_header'))
        deviceSummaryUrl = urllib2.urlopen(_request)  # when include data this become a POST command
        print(" {0}Agent is querying its current status please wait ...".format(self.variables.get('agent_id',None)))
        if deviceSummaryUrl.getcode() == 200:
            x = deviceSummaryUrl.read().decode("utf-8")
            self.getDeviceStatusJson(x)
            self.printDeviceStatus()

    def getDeviceStatusJson(self, data):
        # Use the json module to load the string data into a dictionary
        _theJSON = json.loads(data)
        print len(_theJSON)
        print _theJSON['status']
        print _theJSON['device']['status']
        self.set_variable('device_type', _theJSON['device']['name'])
        if self.get_variable('device_type') == 'CentraLite Switch':
            self.set_variable('device_type', "plugload")
        self.set_variable('device_network_status', _theJSON['device']['status'])
        self.set_variable('factory_id', _theJSON['device']['id'])
        self.set_variable('nick_name', _theJSON['device']['label'])
        print '_theJSON_device_name' + _theJSON['device']['name']
        if _theJSON['device']['name'] == 'CentraLite Switch':
            try:
                if _theJSON['device']['currentStates'][0]['value'] == "on":
                    # print _theJSON['device']['currentStates'][0]['value']
                    self.set_variable('status', "ON")
                elif _theJSON['device']['currentStates'][0]['value'] == "off":
                    # print _theJSON['device']['currentStates'][0]['value']
                    self.set_variable('status', "OFF")
            except KeyError: pass
        elif _theJSON['device']['name'] == 'SmartSense Motion':
            # print _theJSON['device']
            try:
                for index in range(0, len(_theJSON['device']['currentStates'])):
                    # print _theJSON['device']['currentStates'][index]['name']
                    # print _theJSON['device']['currentStates'][index]['value']
                    if _theJSON['device']['currentStates'][index]['name'] == "motion":
                         if _theJSON['device']['currentStates'][index]['value'] == 'active':
                             self.set_variable('motion', True)
                         elif _theJSON['device']['currentStates'][index]['value'] == 'inactive':
                             self.set_variable('motion', False)
                         else:
                             pass
                    else:
                        self.set_variable(_theJSON['device']['currentStates'][index]['name'],
                                          _theJSON['device']['currentStates'][index]['value'])
                        # print self.get_variable(_theJSON['device']['currentStates'][index]['name'])
            except KeyError: pass
        elif _theJSON['device']['name'] == 'SmartSense Presence':
            # print _theJSON['device']
            try:
                for index in range(0, len(_theJSON['device']['currentStates'])):
                    self.set_variable(_theJSON['device']['currentStates'][index]['name'],
                                      _theJSON['device']['currentStates'][index]['value'])
            except KeyError: pass
        elif _theJSON['device']['name'] == 'SmartSense Multi':
            # print _theJSON['device']
            try:
                for index in range(0, len(_theJSON['device']['currentStates'])):
                    self.set_variable(_theJSON['device']['currentStates'][index]['name'],
                                      _theJSON['device']['currentStates'][index]['value'])
            except KeyError: pass
        elif _theJSON['device']['name'] == 'Mobile Presence':
            # print _theJSON['device']
            try:
                for index in range(0, len(_theJSON['device']['currentStates'])):
                    self.set_variable(_theJSON['device']['currentStates'][index]['name'],
                                      _theJSON['device']['currentStates'][index]['value'])
            except KeyError: pass
        else:
            pass

    def printDeviceStatus(self):
        print(" The current SmartThings Device status is as follows:")
        print(" device type = {}".format(self.get_variable('device_type')))
        print(" device network status = {}".format(self.get_variable('device_network_status')))
        print(" factory id = {}".format(self.get_variable('factory_id')))
        print(" nick name = {}".format(self.get_variable('nick_name')))
        print(" status = {}".format(self.get_variable('status')))
        print(" power = {}".format(self.get_variable('power')))
        print(" contact = {}".format(self.get_variable('contact')))
        print(" battery = {}".format(self.get_variable('battery')))
        print(" motion = {}".format(self.get_variable('motion')))
        print(" presence = {}".format(self.get_variable('presence')))
        print(" temperature = {}".format(self.get_variable('temperature')))
        print(" lqi = {}".format(self.get_variable('lqi')))
        print(" rssi = {}".format(self.get_variable('rssi')))
        print(" threeAxis = {}".format(self.get_variable('threeAxis')))
        print(" acceleration = {}".format(self.get_variable('acceleration')))

    #method3: POST Change thermostat parameters
    def setDeviceStatus(self, putmsg):
        setDeviceStatusResult = True
        _urlData = self.get_variable("address_put")
        # _urlData = self.get_variable("address") + "switches/"
        # print '_urlData = ' + self.get_variable("address_put")
        self.isPutMsgValid = True
        if self.isPutMsgValid == True: #check if the data is valid
            # ACCESS_TOKEN = "ce49226a-5383-42dc-832d-12d2017569ca"
            if self.get_variable('device_type') == 'plugload':
                _msg_to_device = self.convertPutMsg(putmsg)
            else:
                _msg_to_device = putmsg
            _data = json.dumps(_msg_to_device)
            _data = _data.encode(encoding='utf_8')
            _request = urllib2.Request(_urlData)
            _request.add_header('Content-Type', 'application/json')
            _request.add_header("Authorization", self.get_variable('auth_header'))
            _request.get_method = lambda: 'PUT'
            try:
                _f = urllib2.urlopen(_request, _data)  # when include data this become a PUT command
                print(" {0}Agent for {1} is changing its status with {2} please wait ..."
                .format(self.variables.get('agent_id', None), self.variables.get('model', None), putmsg))
                print(" after send a PUT request: {}".format(_f.read().decode('utf-8')))
            except:
                print("ERROR: classAPI_SmartThings connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The PUT message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostmsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        for k,v in postmsg.items():
            if k == 'thermostat_mode':
                if postmsg.get('thermostat_mode') == "HEAT":
                    for k,v in postmsg.items():
                        if k == 'cool_setpoint':
                            dataValidity = False
                            break
                elif postmsg.get('thermostat_mode') == "COOL":
                    for k,v in postmsg.items():
                        if k == 'heat_setpoint':
                            dataValidity = False
                            break
        return dataValidity

    def convertPutMsg(self,postmsg):
        for k,v in postmsg.items():
            if k == 'status':
                if postmsg.get('status') == "ON":
                    # self.set_variable("status",1)
                    # self.set_variable("t_heat",postmsg.get("heat_setpoint"))
                    msgToDevice = {"command": "on"}
                elif postmsg.get('status') == "OFF":
                    # self.set_variable("tmode",2)
                    # self.set_variable("t_cool",postmsg.get("cool_setpoint"))
                    msgToDevice = {"command": "off"}
        return msgToDevice

    #method4: Identify this device (Physically)
    def identifyDevice(self):
        identifyDeviceResult = False
        if self.get_variable('status') == 'ON':
            self.setDeviceStatus({"status":"OFF"})
            self.timeDelay(10)
            self.setDeviceStatus({"status":"ON"})
        elif self.get_variable('status') == 'OFF':
            self.setDeviceStatus({"status":"ON"})
            self.timeDelay(10)
            self.setDeviceStatus({"status":"OFF"})
        else:
            self.setDeviceStatus({"status":"ON"})
            self.timeDelay(2)
            self.setDeviceStatus({"status":"OFF"})
            self.timeDelay(2)
            self.setDeviceStatus({"status":"ON"})
            self.timeDelay(2)
            self.setDeviceStatus({"status":"OFF"})
        identifyDeviceResult = True
        return identifyDeviceResult

    #method6: time delay
    def timeDelay(self,time_iden): #specify time_iden for how long to delay the process
        t0 = time.time()
        self.seconds = time_iden
        while time.time() - t0 <= time_iden:
            self.seconds = self.seconds - 1
            print("wait: {} sec".format(self.seconds))
            time.sleep(1)

#This main method will not be executed when this class is used as a module
def main():
    #Utilization: test methods
    #Step1: create an object with initialized data from DeviceDiscovery Agent
    #requirements for instantiation1. model, 2.type, 3.api, 4. address
    # SmartThings = API(model='switch', agent_id='SmartThingsSwitch1', api='API1',
    #                   auth_header='Bearer 59d232be-bf95-4d53-bd9a-df5e4d6dea96',
    #                   address='https://graph.api.smartthings.com/api/smartapps/installations/'
    #                           'be64201d-8a74-47b5-9126-b1a18a9d8488/switches/cca19281-b6cc-4bb1-b642-a7e17a98bb93')
    SmartThings = API(model='switch', agent_id='SmartThingsSwitch1', api='API1',
                      auth_header='Bearer 0291cb9f-168e-490e-b337-2d1a31abdbf4', smt_username='smarthome.pea@gmail.com', smt_password='28Sep1960',
                      # address_get='https://graph.api.smartthings.com/api/devices/3e5ecfcc-ac44-4fd2-8935-ad275b114be9',
                      address_get='https://graph.api.smartthings.com/api/smartapps/installations/'
                                  'be64201d-8a74-47b5-9126-b1a18a9d8488/switches/cca19281-b6cc-4bb1-b642-a7e17a98bb93',
                      address_put='https://graph.api.smartthings.com/api/smartapps/installations/'
                                  'be64201d-8a74-47b5-9126-b1a18a9d8488/switches/cca19281-b6cc-4bb1-b642-a7e17a98bb93')

    print("{0}agent is initialzed for {1} using API={2} at {3}".format(SmartThings.get_variable('agent_id'),SmartThings.get_variable('model'),SmartThings.get_variable('api'),SmartThings.get_variable('address_get')))

    #Step2: acquire a device model number from the API
    SmartThings.discoverHub('smarthome.pea@gmail.com', '28Sep1960')
    SmartThings.getHubDevices('smarthome.pea@gmail.com', '28Sep1960')

    # SmartThings.getDeviceStatus()
    #
    # SmartThings.setDeviceStatus({"status": "OFF"})

    # SmartThings.identifyDevice()

if __name__ == "__main__": main()