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
    def getDeviceStatus(self):

        try:
            url_l = 'http://Smappee1006003343.local/gateway/apipublic/logon'
            head_l = "admin"
            requests.post(url_l, data=head_l)
            request = requests.get("http://Smappee1006003343.local/gateway/apipublic/reportInstantaneousValues")
            checkconnect = request.status_code
            print(" {0} Agent is querying its current status (status:{1}) please wait ...".format(self.variables.get('agent_id', None), str(checkconnect)))

            if checkconnect == 200:
                self.getDeviceStatusJson(request.content)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                url_l = 'http://Smappee1006003343.local/gateway/apipublic/logon'
                head_l = "admin"
                requests.post(url_l, data=head_l)
            # Check the connectivity
        except Exception as er:
            print er
            print('ERROR: classAPI_PowerMeter failed to getDeviceStatus')

    def getDeviceStatusJson(self,data):

        x = json.loads(data, "utf-8")
        volttage = float((x['report'].split('<BR>'))[1][8:13])
        self.set_variable('volttage', volttage)
        ts = time.time()
        self.set_variable('time', ts)

        # Grid
        z1 = ((x['report'].split('<BR>'))[4]).split(',')
        grid_current = float(((z1[0].split('='))[1]).split(' ')[0])
        grid_activePower = float(((z1[1].split('='))[1]).split(' ')[0])
        grid_reactivePower = float(((z1[2].split('='))[1]).split(' ')[0])
        grid_apparentPower = float(((z1[3].split('='))[1]).split(' ')[0])
        grid_powerfactor = float((z1[4].split('='))[1].split(' ')[0]) / 100
        grid_quadrant = float((z1[5].split('='))[1].split(' ')[0])
        grid_phaseshift = float((z1[6].split('='))[1].split(' ')[0])
        grid_phasediff = float((z1[7].split('='))[1].split(' ')[0])

        self.set_variable('grid_current', grid_current)
        self.set_variable('grid_activePower', grid_activePower)
        self.set_variable('grid_reactivePower', grid_reactivePower)
        self.set_variable('grid_apparentPower', grid_apparentPower)
        self.set_variable('grid_powerfactor', grid_powerfactor)
        self.set_variable('grid_quadrant', grid_quadrant)
        self.set_variable('grid_phaseshift', grid_phaseshift)
        self.set_variable('grid_phasediff', grid_phasediff)

        # Solar
        z2 = ((x['report'].split('<BR>'))[7]).split(',')
        solar_current = float(((z2[0].split('='))[1]).split(' ')[0])
        solar_activePower = float(((z2[1].split('='))[1]).split(' ')[0])
        solar_reactivePower = float(((z2[2].split('='))[1]).split(' ')[0])
        solar_apparentPower = float(((z2[3].split('='))[1]).split(' ')[0])
        solar_powerfactor = float((z2[4].split('='))[1].split(' ')[0]) / 100
        solar_quadrant = float((z2[5].split('='))[1].split(' ')[0])
        solar_phaseshift = float((z2[6].split('='))[1].split(' ')[0])
        solar_phasediff = float((z2[7].split('='))[1].split(' ')[0])

        self.set_variable('solar_current', solar_current)
        # self.set_variable('solar_activePower', solar_activePower)
        self.set_variable('solar_reactivePower', solar_reactivePower)
        self.set_variable('solar_apparentPower', solar_apparentPower)
        self.set_variable('solar_powerfactor', solar_powerfactor)
        self.set_variable('solar_quadrant', solar_quadrant)
        self.set_variable('solar_phaseshift', solar_phaseshift)
        self.set_variable('solar_phasediff', solar_phasediff)

        # Load

        #z3 = ((x['report'].split('<BR>'))[10]).split(',')
        #z3 change with new configuration
        z3 = ((x['report'].split('<BR>'))[7]).split(',')
        load_current = float(((z3[0].split('='))[1]).split(' ')[0])
        load_activePower = float(((z3[1].split('='))[1]).split(' ')[0])
        load_reactivePower = float(((z3[2].split('='))[1]).split(' ')[0])
        load_apparentPower = float(((z3[3].split('='))[1]).split(' ')[0])
        load_powerfactor = float((z3[4].split('='))[1].split(' ')[0]) / 100
        load_quadrant = float((z3[5].split('='))[1].split(' ')[0])
        load_phaseshift = float((z3[6].split('='))[1].split(' ')[0])
        load_phasediff = float((z3[7].split('='))[1].split(' ')[0])

        self.set_variable('load_current', load_current)
        self.set_variable('load_activePower', load_activePower)
        self.set_variable('load_reactivePower', load_reactivePower)
        self.set_variable('load_apparentPower', load_apparentPower)
        self.set_variable('load_powerfactor', load_powerfactor)
        self.set_variable('load_quadrant', load_quadrant)
        self.set_variable('load_phaseshift', load_phaseshift)
        self.set_variable('load_phasediff', load_phasediff)

        self.set_variable('solar_activePower', load_activePower - grid_activePower)


    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" Time(Unix) = {}".format(self.get_variable('time')))
        print(" Volttage(V) = {}".format(self.get_variable('volttage')))

        print ("current grid status--------------------------------")
        print(" Current(A) = {}".format(self.get_variable('grid_current')))
        print(" ActivePower(W) = {}".format(self.get_variable('grid_activePower')))
        print(" ReactivePower(Var) = {}".format(self.get_variable('grid_reactivePower')))
        print(" ApparentPower(VA) = {}".format(self.get_variable('grid_apparentPower')))
        print(" Powerfactor = {}".format(self.get_variable('grid_powerfactor')))
        print(" quadrant = {}".format(self.get_variable('grid_quadrant')))
        print(" phaseshift = {}".format(self.get_variable('grid_phaseshift')))
        print(" phasediff = {}".format(self.get_variable('grid_phasediff')))

        print ("current solar status------------------------------")
        print(" Current(A) = {}".format(self.get_variable('solar_current')))
        print(" ActivePower(W) = {}".format(self.get_variable('solar_activePower')))
        print(" ReactivePower(Var) = {}".format(self.get_variable('solar_reactivePower')))
        print(" ApparentPower(VA) = {}".format(self.get_variable('solar_apparentPower')))
        print(" Powerfactor = {}".format(self.get_variable('solar_powerfactor')))
        print(" quadrant = {}".format(self.get_variable('solar_quadrant')))
        print(" phaseshift = {}".format(self.get_variable('solar_phaseshift')))
        print(" phasediff = {}".format(self.get_variable('solar_phasediff')))

        print ("current load status-------------------------------")
        print(" Current(A) = {}".format(self.get_variable('load_current')))
        print(" ActivePower(W) = {}".format(self.get_variable('load_activePower')))
        print(" ReactivePower(Var) = {}".format(self.get_variable('load_reactivePower')))
        print(" ApparentPower(VA) = {}".format(self.get_variable('load_apparentPower')))
        print(" Powerfactor = {}".format(self.get_variable('load_powerfactor')))
        print(" quadrant = {}".format(self.get_variable('load_quadrant')))
        print(" phaseshift = {}".format(self.get_variable('load_phaseshift')))
        print(" phasediff = {}".format(self.get_variable('load_phasediff')))

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    PowerMeter = API(model='Smappee', type='PowerMeter', api='API3', agent_id='Smappee')
    PowerMeter.getDeviceStatus()

if __name__ == "__main__": main()
