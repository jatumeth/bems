# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

import time
import json
import requests
import time

class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
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

    # 2. Attributes from Attributes table

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
     ------------------------------------------------------------------------------------------

    '''
    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDeviceStatus() GET
    '''    

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        url_get_append = self.variables['address']+"/get"
        getDeviceStatusResult = True
        try:
            r = requests.get(url_get_append)
            print("{0} Agent is querying its current status (status:{1}) please wait ...".format(self.get_variable('agent_id'), r.status_code))
            format(self.variables.get('agent_id', None), str(r.status_code))
            print (" status = {}".format(r.status_code))
            if r.status_code == 200:
                self.getDeviceStatusJson(r.text)
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
            print('ERROR: classAPI_PhilipsHue failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def getDeviceStatusJson(self, data):

        conve_json = json.loads(data)
        self.set_variable('Relay0_status', conve_json["Relay0_status"])
        self.set_variable('Relay1_status', conve_json["Relay1_status"])
        self.set_variable('Relay2_status', conve_json["Relay2_status"])
        self.set_variable('Relay3_status', conve_json["Relay3_status"])
        self.set_variable('Relay4_status', conve_json["Relay4_status"])
        self.set_variable('Relay5_status', conve_json["Relay5_status"])
        self.set_variable('Relay6_status', conve_json["Relay6_status"])
        self.set_variable('Relay7_status', conve_json["Relay7_status"])

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" The current status are as follows:")
        print(" Relay0_status = {}".format(self.get_variable('Relay0_status')))
        print(" Relay1_status = {}".format(self.get_variable('Relay1_status')))
        print(" Relay2_status = {}".format(self.get_variable('Relay2_status')))
        print(" Relay3_status = {}".format(self.get_variable('Relay3_status')))
        print(" Relay4_status = {}".format(self.get_variable('Relay4_status')))
        print(" Relay5_status = {}".format(self.get_variable('Relay5_status')))
        print(" Relay6_status = {}".format(self.get_variable('Relay6_status')))
        print(" Relay7_status = {}".format(self.get_variable('Relay7_status')))
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        for k,v in postmsg.items():
            if k == 'Relay0':
                command =self.convertPostMsg(postmsg["Relay0"])
                relay_command = {"contact_num":"0","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay1':
                command =self.convertPostMsg(postmsg["Relay1"])
                relay_command = {"contact_num":"1","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay2':
                command =self.convertPostMsg(postmsg["Relay2"])
                relay_command = {"contact_num":"2","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay3':
                command =self.convertPostMsg(postmsg["Relay3"])
                relay_command = {"contact_num":"3","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay4':
                command =self.convertPostMsg(postmsg["Relay4"])
                relay_command = {"contact_num":"4","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay5':
                command =self.convertPostMsg(postmsg["Relay5"])
                relay_command = {"contact_num":"5","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay6':
                command =self.convertPostMsg(postmsg["Relay6"])
                relay_command = {"contact_num":"6","status":command}
                self.setrelay(relay_command)
            elif k == 'Relay7':
                command =self.convertPostMsg(postmsg["Relay7"])
                relay_command = {"contact_num":"7","status":command}
                self.setrelay(relay_command)
            else:
                print "Wrong msg"

    def setrelay(self, postmsg):
        self.status = self.convertPostMsg(postmsg["status"])

        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            try:
                print "Sending requests put"
                print ("Contract Number = {} , Status = {}".format(postmsg["contact_num"],self.status))
                url_set_append = self.variables['address'] + "/" + self.status + postmsg["contact_num"]
                put_requests = requests.put(url_set_append)
            except:
                print("ERROR: classAPI_RCRelay connection failure! @ setDeviceStatus")
        else:
            print("The POST message is invalid, try again\n")

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgtolower = str(postmsg.lower())
        return msgtolower

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address

    RCRelay = API(model='DCRelay8channel', type='DCRelay', api='API3', agent_id='relay02',address='http://192.168.1.35')
    RCRelay.getDeviceStatus()

    # RCRelay.setDeviceStatus({"Relay0": "on","Relay1": "on","Relay2": "on","Relay3": "on","Relay4": "on","Relay5": "on","Relay6": "on","Relay7": "on"})
    # RCRelay.setDeviceStatus({"Relay0": "off", "Relay1": "on", "Relay2": "on", "Relay3": "on", "Relay4": "on", "Relay5": "on","Relay6": "on", "Relay7": "on"})

if __name__ == "__main__": main()