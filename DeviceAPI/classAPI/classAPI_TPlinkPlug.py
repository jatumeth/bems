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

        getDeviceStatusResult = True

        r0 = requests.post(
            url="https://wap.tplinkcloud.com/",
            params={
                "token": "1a6b68f0-2ad615fdb4134d728e72e77",
            },
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "method": "getDeviceList"
            })
        )
        w = json.loads(r0.text)
        status = w['result']['deviceList'][0]['status']
        r = requests.post(
            url="https://wap.tplinkcloud.com/",
            params={
                "token": "1a6b68f0-2ad615fdb4134d728e72e77",
            },
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "method": "passthrough",
                "params": {
                    "requestData": "{\"emeter\":{\"get_realtime\":{}}}",
                    "deviceId": "8006B1A9D3F4176D0B2B9F18A2BA0BB417A7DD7F"
                }
            })
        )

        b = json.loads(r.text)
        c = b['result']['responseData']
        d = json.loads(c)
        current = d['emeter']['get_realtime']['current']
        volt = d['emeter']['get_realtime']['voltage']
        power = d['emeter']['get_realtime']['power']

        self.set_variable('status', status)
        self.set_variable('current', current)
        self.set_variable('voltage', volt)
        self.set_variable('power', power)

        try:
            print ""




        except Exception as er:
            print er
            print('ERROR: classAPI_PhilipsHue failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)
        self.printDeviceStatus()
    def getDeviceStatusJson(self, data):

        conve_json = json.loads(data)
        self.set_variable('label', str(conve_json["label"]))
        if str(conve_json["status"]) == "on":
            self.set_variable('status', "ON")
        else:
            self.set_variable('status', "OFF")
        self.set_variable('unitTime', conve_json["unitTime"])
        self.set_variable('type', str(conve_json["type"]))

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" status = {}".format(self.get_variable('status')))
        print(" current = {}".format(self.get_variable('current')))
        print(" volt = {}".format(self.get_variable('volt')))
        print(" power = {}".format(self.get_variable('power')))
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True


        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            _data = json.dumps(self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            print _data
            command = postmsg['status'].lower()
            try:
                if command == 'on':
                    print "on"
                    r = requests.post(
                        url="https://wap.tplinkcloud.com/",
                        params={
                            "token": "1a6b68f0-2ad615fdb4134d728e72e77",
                        },
                        headers={
                            "Content-Type": "application/json",
                        },
                        data=json.dumps({
                            "method": "passthrough",
                            "params": {
                                "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}",
                                "deviceId": "8006B1A9D3F4176D0B2B9F18A2BA0BB417A7DD7F"
                            }
                        })
                    )

                elif command == 'off':
                    print "off"
                    r = requests.post(
                        url="https://wap.tplinkcloud.com/",
                        params={
                            "token": "1a6b68f0-2ad615fdb4134d728e72e77",
                        },
                        headers={
                            "Content-Type": "application/json",
                        },
                        data=json.dumps({
                            "method": "passthrough",
                            "params": {
                                "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}",
                                "deviceId": "8006B1A9D3F4176D0B2B9F18A2BA0BB417A7DD7F"
                            }
                        })
                    )
            except:
                print("ERROR: classAPI_TPlinkPlug connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The POST message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        if 'status' in postmsg.keys():
            msgToDevice['command'] = str(postmsg['status'].lower())
        return msgToDevice

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address

    TPlinkPlug = API(model='TPlinkPlug', type='tv', api='API3', agent_id='TPlinkPlugAgent',url = 'https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/314fe2f7-1724-42ed-86b6-4a8c03a08601/switches/', bearer = 'Bearer ebb37dd7-d048-4cf6-bc41-1fbe9f510ea7',device = '5500e07f-1f41-4716-b89c-723c98cc2c0e')


    import time
    TPlinkPlug.setDeviceStatus({"status": "ON"})
    TPlinkPlug.getDeviceStatus()
    #
    # time.sleep(10)
    #
    # TPlinkPlug.setDeviceStatus({"status": "Off"})
    #
    # time.sleep(10)
    #
    # TPlinkPlug.setDeviceStatus({"status": "ON"})
    #
    # time.sleep(10)
    #
    # TPlinkPlug.setDeviceStatus({"status": "OFF"})
    #
    # time.sleep(10)
    #
    # TPlinkPlug.setDeviceStatus({"status": "ON"})

if __name__ == "__main__": main()