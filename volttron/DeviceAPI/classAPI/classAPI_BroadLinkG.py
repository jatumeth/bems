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

#__author__ = "HiVETEAM"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "HiVETEAM Team"
#__email__ = "peahive@gmail.com"
#__website__ = "www.peahive.org"
#__created__ = "2017-09-12 12:04:50"
#__lastUpdated__ = "2017-03-14 11:23:33"
'''

import time
import json
import requests


class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self, **kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count', 0)
        self.set_variable('connection_renew_interval', 6000)
        self.only_white_bulb = None

    def renewConnection(self):
        pass

    def set_variable(self, k, v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self, k):
        return self.variables.get(k, None)  # default of get_variable is none

    # 2. Attributes from Attributes table

    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label            GET          label in string
    status           GET          Status On/Off
    status           SET          Status On/Off
     ------------------------------------------------------------------------------------------

    '''
    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDeviceStatus() GET
    '''



    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" status = {}".format(self.get_variable('status')))
        print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" type= {}".format(self.get_variable('type')))
        print("---------------------------------------------")

    def getDeviceStatusJson(self, data):

        print "getdata"





    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        print('Class API trigger')
        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            _data = json.dumps(self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')

            # try:

            print(type(postmsg))

            if postmsg.has_key('mode') == False:
                mode = 'send'

            if postmsg.has_key('mode') == True:
                if postmsg.get('mode') == 'learn':
                    mode = postmsg.get('mode')
                elif postmsg.get('mode') == 'send':
                    mode = postmsg.get('mode')
                else:
                    mode = 'send'
            print mode

            if postmsg.has_key('status'):
                print('Got Status Key')
                command = 'status'+postmsg.get('status')

            elif postmsg.has_key('stemp'):
                command = 'stemp'+str(postmsg.get('stemp'))

                self.set_variable('stemp', str(postmsg.get('stemp')))

                self.set_variable('status', postmsg.get('status'))

            elif postmsg.has_key('channel'):
                print('Got Channel Key')
                command = 'status'+postmsg.get('channel')


            if mode == 'learn':
                print('Learn Mode Active')
                print('Send Request')
                remotename = str(postmsg.get('device'))[:5]
                try:
                    response = requests.get(
                        url="http://localhost:8081/learnCommand/%s%s" % (remotename, command),
                    )
                    print('Response HTTP Status Code: {status_code}'.format(
                        status_code=response.status_code))
                    print('Response HTTP Response Body: {content}'.format(
                        content=response.content))
                    # return '{status_code}'.format(status_code=response.status_code)

                except requests.exceptions.RequestException:
                    print('HTTP Request status failed')

                time.sleep(1)

                try:
                    response = requests.get(
                        url="http://localhost:8080/learnCommand/%s%s" % (remotename, command),
                    )
                    print('Response HTTP Status Code: {status_code}'.format(
                        status_code=response.status_code))
                    print('Response HTTP Response Body: {content}'.format(
                        content=response.content))
                    # return '{status_code}'.format(status_code=response.status_code)

                except requests.exceptions.RequestException:
                    print('HTTP Request status failed')

            elif mode == 'send':

                print('Send Mode Active')
                print('Send Request')
                remotename = str(postmsg.get('device'))[:5]
                print command

                try:
                    response = requests.get(
                        url="http://localhost:8081/sendCommand/%s%s" % (remotename, command),
                    )
                    print('Response HTTP Status Code: {status_code}'.format(
                        status_code=response.status_code))
                    print('Response HTTP Response Body: {content}'.format(
                        content=response.content))
                    # return '{status_code}'.format(status_code=response.status_code)

                except requests.exceptions.RequestException:
                    print('HTTP Request failed')

                time.sleep(1)
                print "next"

                try:
                    response = requests.get(
                        url="http://localhost:8080/sendCommand/%s%s" % (remotename, command),
                    )
                    print('Response HTTP Status Code: {status_code}'.format(
                        status_code=response.status_code))
                    print('Response HTTP Response Body: {content}'.format(
                        content=response.content))
                    # return '{status_code}'.format(status_code=response.status_code)

                except requests.exceptions.RequestException:
                    print('HTTP Request failed')

            else:
                print("message gg")
            # except Exception as e:
            #     print(e)
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

    BroadLink = API(model='LGTV', type='tv', api='API3', agent_id='LGTVAgent')
    # BroadLink.getDeviceStatus()
    # BroadLink.setDeviceStatus({"status": "ON", "device": "01DAI0a4f437e63c2",
    #                            "mode": "send", "remote": "AC", "vender": "broadlink"})

    BroadLink.setDeviceStatus({"mode": "send", "device": "01DAI0a4f437e63c2", "status": "ON"})

    # BroadLink.setDeviceStatus({"mode":"learn","stemp":27,"device":"01DAI0a4f437e63c2"})

    # BroadLink.setDeviceStatus({"username": "pean1", "status": "ON", "stemp": 20, "mode": 3, "device": "01DAI0a4f437e63c2",
    #  "type": "devicecontrol"})

    # BroadLink.setDeviceStatus({"status": "ON", "device": "01DAI0a4f437e63c2", "remote": "AC", "vender": "broadlink",
    #                            "command": "on"})

if __name__ == "__main__":
    main()