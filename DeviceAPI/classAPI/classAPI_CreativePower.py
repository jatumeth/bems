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

#__author__ = "PEA HiVE Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-12-07 16:43:35"
'''
import time
import json

import requests
import urllib3
#from bemoss_lib.utils import rgb_cie
class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self, **kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True

    def renewConnection(self):
        pass

    def set_variable(self, k, v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none

    # 2. Attributes from Attributes table

    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label              GET          label in string
    Time(Unix)         GET          time in unix
    grid_current
    grid_activePower
    grid_reactivePower
    grid_powerfactor

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

            http = urllib3.PoolManager()
            r = http.request('GET', 'https://cplservice.com/apixmobile.php/cpletrix?filter=device_id,eq,300346794&order=trans_id,desc&page=1')
            conve_json = json.loads(r.data)
            print r.data

            self.set_variable('grid_current', conve_json['cpletrix']['records'][0][6])
            self.set_variable('grid_activePower', float(conve_json['cpletrix']['records'][0][9])*-1)
            self.set_variable('grid_reactivePower', conve_json['cpletrix']['records'][0][10])
            self.set_variable('grid_powerfactor', conve_json['cpletrix']['records'][0][8])

        except Exception as er:
            print er



    def printDeviceStatus(self):

        print ("--------------------------------Creative Power status--------------------------------")
        print(" Current(A) = {}".format(self.get_variable('grid_current')))
        print(" ActivePower(W) = {}".format(self.get_variable('grid_activePower')))
        print(" ReactivePower(Var) = {}".format(self.get_variable('grid_reactivePower')))
        print(" Powerfactor = {}".format(self.get_variable('grid_powerfactor')))


    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    Creative_Power = API(model='e-Trix@Larm', type='powermeter', api='classAPI_CreativePower', agent_id='Creative_Power')
    Creative_Power.getDeviceStatus()
    Creative_Power.printDeviceStatus()
    # Creative_Power.printDeviceStatus()

if __name__ == "__main__": main()
