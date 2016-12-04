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
#!/usr/bin/python3
'''
This API class is for an agent that want to communicate/monitor/control
devices that compatible with Prolon VC1000 or M1000
Avijit Saha 10/10/2014
'''

from pymodbus.client.sync import ModbusTcpClient
import csv
import os
import json


class API:
    #1. constructor : gets call everytime when create a new class
    #requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs): #default color is white
        #Initialized common attributes
        self.variables = kwargs
        address_parts = self.get_variable('address').split(':')
        self.set_variable('address',address_parts[0])
        self.set_variable('slave_id',int(address_parts[1]))
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval',6000) #nothing to renew
        self.client = '1'
        self.li_key = []
        self.li_val = []
        self.msg = ''
        self.msg_connect_fail = 'can not connect to Inverter'
        self.msg_get_fail = 'can not get Inverter status'
        self.result_fail = 'Fail'
        self.result_success = 'Success'
        self.li_factor = []

    def renewConnection(self):
        pass

    def set_variable(self,k,v): #k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None) #default of get_variable is none


    #2. Attributes from Attributes table
    '''
    Attributes:
    ------------------------------------------------------------------------------------------

    ------------------------------------------------------------------------------------------
    '''


    #3. Capabilites (methods) from Capabilities table
    '''
    API available methods:
    1. getDeviceStatus() Read
    2. setDeviceStatus(parameter,value) Write
    3. identifyDevice() Write
    '''

    #method1: GET Open the port and read the data

    def getDeviceStatus(self):

        try:
            self.connect(25201, 23)
            self.get_variable = {'Name': '3kwInverter'}
            self.get_variable['workState'] = self.request.getRegister(0) * 1
            self.get_variable['acVoltageGrade'] = self.request.getRegister(1) * 1
            self.get_variable['ratedPower'] = self.request.getRegister(2) * 1
            self.get_variable['reserved'] = self.request.getRegister(3) * 0.1
            self.get_variable['batteryVoltage'] = self.request.getRegister(4) * 0.1
            self.get_variable['solarVoltage'] = self.request.getRegister(5) * 0.1
            self.get_variable['gridVoltage'] = self.request.getRegister(6) * 0.1
            self.get_variable['busVoltage'] = self.request.getRegister(7) * 0.1
            self.get_variable['controlCurrent'] = self.request.getRegister(8) * 0.1
            self.get_variable['InverterCurrent'] = self.request.getRegister(9) * 0.1
            self.get_variable['gridCurrent'] = self.request.getRegister(10) * 0.1
            self.get_variable['loadCurrent'] = self.request.getRegister(11) * 0.1
            self.get_variable['solarBattActivePower'] = self.request.getRegister(12) * 1
            self.get_variable['gridActivePowerold'] = self.request.getRegister(13) * 1
            self.get_variable['loadActivePower'] = self.request.getRegister(14) * 1
            self.get_variable['reserved1'] = self.request.getRegister(15) * 1
            self.get_variable['solarBattApparentPower'] = self.request.getRegister(16) * 1
            self.get_variable['gridApparentPower'] = self.request.getRegister(17) * 1
            self.get_variable['loadApparentPower'] = self.request.getRegister(18) * 1
            self.get_variable['reserved2'] = self.request.getRegister(19) * 1
            self.get_variable['solarBattReativePower'] = self.request.getRegister(20) * 1
            self.get_variable['gridReativePower'] = self.request.getRegister(21) * 1
            self.get_variable['loadReativePower'] = self.request.getRegister(22) * 1


        except Exception as er:
            print "Error connect to inverter"


        try:
            self.connect(25273, 2)
            self.get_variable['battPowerold'] = self.request.getRegister(0) * 1
            self.get_variable['battCurrent'] = self.request.getRegister(1) * 1
        except Exception as er:
            print "Error connect to inverter"

        try:
            if self.get_variable['gridActivePowerold'] < 10000:
                self.get_variable['gridActivePowerstatus'] = "solarToGrid"
                self.get_variable['gridActivePower'] = int(self.get_variable['gridActivePowerold'])
            else:
                self.get_variable['gridActivePowerstatus'] = "gridToHome"
                self.get_variable['gridActivePower'] = 65536-int(self.get_variable['gridActivePowerold'])


            if self.get_variable['battPowerold'] < 10000:
                self.get_variable['Batterystatus'] = "Discharge"
                self.get_variable['battPower'] = int(self.get_variable['battPowerold'])
                print "654654"

                self.get_variable['solarActivePower'] = (int(self.get_variable['solarBattActivePower'])-int(self.get_variable['battPower']))
            else:
                self.get_variable['Batterystatus'] = "Charge"
                self.get_variable['battPower'] = 65536-int(self.get_variable['battPowerold'])
                self.get_variable['solarActivePower'] = (int(self.get_variable['solarBattActivePower'])+int(self.get_variable['battPower']))

            self.printDeviceStatus()
        except Exception as er:
            print "Error connect to PRINT"


    def printDeviceStatus(self):

        print(" the current status is as follows:")

        print(" gridActivePower_status = {}".format(self.get_variable['gridActivePowerstatus']))
        print(" gridActivePower = {}".format(self.get_variable['gridActivePower']))
        print(" loadActivePower = {}".format(self.get_variable['loadActivePower']))
        print(" solarActivePower = {}".format(self.get_variable['solarActivePower']))
        print(" Battery_status = {}".format(self.get_variable['Batterystatus']))
        print(" battPower = {}".format(self.get_variable['battPower']))
        print(" solar+Battery = {}".format(self.get_variable['solarBattActivePower']))
        print("-----------------------------------------------------------")

        print(" workState = {}".format(self.get_variable['workState']))
        print(" acVoltageGrade = {}".format(self.get_variable['acVoltageGrade']))
        print(" ratedPower = {}".format(self.get_variable['ratedPower']))
        print(" reserved = {}".format(self.get_variable['reserved']))
        print(" batteryVoltage = {}".format(self.get_variable['batteryVoltage']))
        print(" solarVoltage = {}".format(self.get_variable['solarVoltage']))
        print(" gridVoltage = {}".format(self.get_variable['gridVoltage']))
        print(" busVoltage = {}".format(self.get_variable['busVoltage']))
        print(" controlCurrent = {}".format(self.get_variable['controlCurrent']))
        print(" InverterCurrent = {}".format(self.get_variable['InverterCurrent']))
        print(" gridCurrent = {}".format(self.get_variable['gridCurrent']))
        print(" loadCurrent= {}".format(self.get_variable['loadCurrent']))
        print(" solarBattActivePower = {}".format(self.get_variable['solarBattActivePower']))
        print(" loadActivePower = {}".format(self.get_variable['loadActivePower']))
        print(" solarBattApparentPower= {}".format(self.get_variable['solarBattApparentPower']))
        print(" busVoltage = {}".format(self.get_variable['busVoltage']))
        print(" gridApparentPower = {}".format(self.get_variable['gridApparentPower']))
        print(" loadApparentPower = {}".format(self.get_variable['loadApparentPower']))
        print(" solarBattsolarReativePower = {}".format(self.get_variable['solarBattReativePower']))
        print(" gridReativePower = {}".format(self.get_variable['gridReativePower']))
        print(" loadReativePower = {}".format(self.get_variable['loadReativePower']))
        print(" battPower = {}".format(self.get_variable['battPower']))
        print(" battCurrent = {}".format(self.get_variable['battCurrent']))
        print("-------------------------        from pymodbus.client.sync import ModbusTcpClient--------------------")


    def setDeviceStatus(self, postmsg):
        _mode = 0
        if postmsg['mode'] == "PL":
            _mode = 0
        elif postmsg['mode'] == "FL":
            _mode = 1
        elif postmsg['mode'] == "FS":
            _mode = 2
        elif postmsg['mode'] == "UPS":
            _mode = 3
        elif postmsg['mode'] == "PO":
            _mode = 4
        self.set_use_mode(_mode)

    def connect(self,start,num):
        client = ModbusTcpClient('192.168.1.49', port=502)
        self.request = client.read_holding_registers(start, num, unit=4)

#This main method will not be executed when this class is used as a module
def main():
    Inverter = API(model='VC1000',type='VAV',api='API',address='192.168.1.49:4',)
    Inverter.getDeviceStatus()

if __name__ == "__main__": main()