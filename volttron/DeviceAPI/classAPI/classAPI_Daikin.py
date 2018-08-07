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

import requests
import time
class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True


    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none

    # 2. Attributes from Attributes table

    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    status               GET,SET      open/close airconditioner
    set_temperature      GET,SET      change set temperature
    current_temperature  GET          show current temperature
    mode                 GET,SET      represents the operating mode
    set_humidity         GET          represents the target humidity
     ------------------------------------------------------------------------------------------

    '''
    # 3. Capabilites (methods) from Capabilities table
    '''
    API3 available methods:
    1. getDeviceStatus() GET
    2. setDeviceStatus() SET
    '''

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        # getDeviceStatusResult = True

        try:
            r = requests.get("http://192.168.1.110/aircon/get_control_info",
                              timeout=20);

            print("{0} Agent is querying its current status (status:{1}) please wait ...".format(self.get_variable('agent_id'), r.status_code))
            format(self.variables.get('agent_id', None), str(r.status_code))

            q = requests.get("http://192.168.1.110/aircon/get_sensor_info",
                              timeout=20);

            if r.status_code == 200:

                self.getDeviceStatusJson(r, q)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                getDeviceStatusResult = False

        except Exception as er:
            print er
            print('ERROR: classAPI_PhilipsHue failed to getDeviceStatus')


    def getDeviceStatusJson(self, r, q):

        statusraw = (r.text.split(','))[1].split('=')[1]
        if statusraw == "1":
            status = "ON"
        elif statusraw == "0":
            status = "OFF"
        else:
            status = "ON"
        mode = str(r.text.split(',')[2].split('=')[1])

        if mode == '3':
            strmode = 'COLD'
        if mode == '2':
            strmode = 'DEHUMDIFICATOR'
        if mode == '4':
            strmode = 'HOT'
        if mode == '6':
            strmode = 'FAN'
        if mode == '1' or mode == '0' or mode == '7':
            strmode = 'AUTO'

        set_temperature = (r.text.split(','))[4].split('=')[1]
        set_humidity = (r.text.split(','))[5].split('=')[1]

        if set_temperature == '--':
            set_temperature = '20'

        if set_humidity == '--':
            set_humidity = '70'

        self.set_variable('status', status)
        self.set_variable('current_temperature', (q.text.split(','))[1].split('=')[1])
        self.set_variable('set_temperature', set_temperature)
        self.set_variable('set_humidity', set_humidity)
        self.set_variable('mode', strmode)

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" status = {}".format(self.get_variable('status')))
        print(" current_temperature = {}".format(self.get_variable('current_temperature')))
        print(" set_temperature = {}".format(self.get_variable('set_temperature')))
        print(" set_humidity = {}".format(self.get_variable('set_humidity')))
        print(" mode = {}".format(self.get_variable('mode')))
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        self.getDeviceStatus()
        setDeviceStatusResult = True
        postmsg = str(postmsg)
        print(" postmsg = {}".format(postmsg))
        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid

            status = format(self.get_variable('status'))
            stemp = format(self.get_variable('set_temperature'))
            mode = format(self.get_variable('mode'))
            if mode == 'COLD':
                mode = '3'
            if mode == 'DEHUMDIFICATOR':
                mode = '2'
            if mode == 'HOT':
                mode = '4'
            if mode == 'AUTO':
                mode = '1'
            if mode == 'FAN':
                mode = '6'

            if  type(postmsg)== str:
                postmsg = eval(postmsg)

            for k, v in postmsg.items():
                if k == 'status':
                    if (postmsg['status']) == "ON":
                        status = "1"
                    elif (postmsg['status']) == "OFF":
                        status = "0"
                elif k == 'stemp':
                    stemp = str((postmsg['stemp']))
                elif k == 'mode':
                    if (postmsg['mode']) == 'COLD':
                        mode = '3'
                    if (postmsg['mode']) == 'DEHUMDIFICATOR':
                        mode = '2'
                    if (postmsg['mode']) == 'HOT':
                        mode = '4'
                    if (postmsg['mode']) == 'AUTO':
                        mode = '1'
                    if (postmsg['mode']) == 'FAN':
                        mode = '6'
                else:
                    m = 1
            try:
                stemp = dict(stemp)
            except:
                stemp = '25'
            data=str("pow="+status+"&stemp="+stemp+"&mode="+mode+"&shum=0&f_rate=B&f_dir=3")
            print data
            try:
                print "sending requests put"
                r = requests.post(
                    "http://192.168.1.110/aircon/set_control_info",
                    headers={"Authorization": "Bearer b73d52c8-1b73-448e-9ff2-eda53d60944b "}, data= data, timeout=20);
                print(" {0}Agent for {1} is changing its status with {2} please wait ..."
                      .format(self.variables.get('agent_id', None), self.variables.get('model', None), postmsg))
                print(" after send a POST request: {}".format(r.status_code))
            except:
                print("ERROR: classAPI_Fan connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The POST message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity


# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address

    AC = API(model='daikin', type='AC', api='API', agent_id='ACAgent')

    #
    AC.setDeviceStatus({'status': 'OFF', 'device': '1DAIK1200138'})
    # time.sleep(5)
    AC.getDeviceStatus()
    # AC.setDeviceStatus({"status": "OFF", "device": "1DAIK", "mode": "COLD", "username":"hive5"})
    # AC.setDeviceStatus({'status': 'OFF', 'stemp':'24','device': '1DAIK1200138'})

if __name__ == "__main__": main()
