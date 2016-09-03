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
import urllib2
import requests

#from bemoss_lib.utils import rgb_cie
class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval',6000) #nothing to renew, right now
        # to initialize the only white bulb value
        self.getDeviceStatus()
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
    label               GET          label in string
    Time(Unix)         GET          time in unix
    Current(A)          GET          current
    ActivePower(W)      GET          Active Power
    ReactivePower(Var)  GET          Reactive Power
    ApparentPower(VA)   GET          Apparent Power
    Powerfactor         GET          Power factor

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

        #login
        urlDatal = self.get_variable("addressl")
        hue_usernamel = self.get_variable("usernamel")

        #Url for queliy data
        urlData = self.get_variable("addressq")
        hue_username = self.get_variable("usernameq")

        try:
            requests.post(urlDatal, data=hue_usernamel)
            request = urllib2.Request(urlData, headers=hue_username) #addtime out
            contents = urllib2.urlopen(request).read()
            print(" {0}Agent is querying its current status (status:{1}) please wait ...")
            checkconnect = urllib2.urlopen(request).getcode()
            format(self.variables.get('agent_id', None), str(checkconnect))

            if checkconnect == 200:
                getDeviceStatusResult = False
                self.getDeviceStatusJson(contents)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                getDeviceStatusResult = False
            # Check the connectivity
            if getDeviceStatusResult==True:
                self.wset_variable('offline_count', 0)
            else:
                self.set_variable('offline_count', self.get_variable('offline_count')+1)
        except Exception as er:
            print er
            print('ERROR: classAPI_PowerMeter failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def getDeviceStatusJson(self,data):

        x = json.loads(data, "utf-8")
        z1 = ((x['report'].split('<BR>'))[4]).split(',')

        current1 = float(((z1[0].split('='))[1])[0:4])
        activePower1 = float(((z1[1].split('='))[1])[0:5])
        reactivePower1 = float(((z1[2].split('='))[1])[0:5])
        apparentPower1 = float(((z1[3].split('='))[1])[0:5])
        powerfactor = float((z1[4].split('='))[1]) / 100

        z2 = ((x['report'].split('<BR>'))[7]).split(',')
        current2 = float(((z2[0].split('='))[1])[0:4])
        activePower2 = float(((z2[1].split('='))[1])[0:5])
        reactivePower2 = float(((z2[2].split('='))[1])[0:5])
        apparentPower2 = float(((z2[3].split('='))[1])[0:5])

        current=current1+current2
        activePower=activePower1+activePower2
        reactivePower=reactivePower1+reactivePower2
        apparentPower=apparentPower1+apparentPower2

        ts = time.time()

        self.set_variable('time', ts)
        self.set_variable('current', current)
        self.set_variable('activePower', activePower)
        self.set_variable('reactivePower', reactivePower)
        self.set_variable('apparentPower', apparentPower)
        self.set_variable('powerfactor', powerfactor)


    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" Power Meter parameter reading  as are follows:")
        print(" Time(Unix) = {}".format(self.get_variable('time')))
        print(" Current(A) = {}".format(self.get_variable('current')))
        print(" ActivePower(W) = {}".format(self.get_variable('activePower')))
        print(" ReactivePower(Var) = {}".format(self.get_variable('reactivePower')))
        print(" ApparentPower(VA) = {}".format(self.get_variable('apparentPower')))
        print(" Powerfactor = {}".format(self.get_variable('powerfactor')))
    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    #Url for queliy data#Url for queliy data
    url_q = "http://Smappee1006003343.local/gateway/apipublic/reportInstantaneousValues"
    head_q = {"Authorization" : "admin"}

    #Url for login
    url_l = 'http://Smappee1006003343.local/gateway/apipublic/logon'
    head_l = "admin"

    PowerMeter = API(model='Smappee',type='PowerMeter',api='API3',addressq=url_q,usernameq=head_q,addressl=url_l,usernamel=head_l, agent_id='Smappee')

if __name__ == "__main__": main()