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
    temperature               GET           temperature reading (floating point in deg F)
    heat_setpoint             GET    POST   target heat setpoint (floating point in deg F)
    cool_setpoint             GET    POST   target cool setpoint (floating point in deg F)
    supply_temperature        GET           RTU supply temperature (floating point in deg F)
    return_temperature        GET           RTU supply temperature (floating point in deg F)
    flap_override             GET    POST   flap override('ON'/'OFF')
    flap_position             GET    POST   flap position, int
    outside_temperature       GET           outside temperature from RTU sensor (floating point in deg F)
    pressure                  GET           presure
    outside_damper_position   GET    POST   outside damper position, int
    bypass_damper_position    GET    POST   outside damper position, int
    fan_status                GET    POST   RTU fan status('ON'/'OFF')
    cooling_status            GET    POST   RTU cooling status('ON'/'OFF')
    cooling_mode              GET    POST   RTU cooling mode('None'/'STG1'/'STG2')
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
        getDeviceStatusResult = True
        filename = os.getcwd() + "/InvConfig .csv"
        _pointer = 0
        _step = 20
        _param = {}
        try:
            self.connect()
            _Total = self.load_reg(filename)
            while (_Total - _pointer) >= _step:
                bit_length = 0
                i = 0
                is_break = False
                while (i <= _step):
                    #print(i)
                    next_step = _pointer + 1
                    current_step = int(self.li_val[_pointer]) + 1
                    #print(self.li_val[next_step])
                    #print(current_step)
                    _pointer = _pointer + 1

                    if (int(self.li_val[next_step]) == int(current_step)):
                        #print("Next Step")
                        bit_length = bit_length + 1
                    else:
                        break
                    i = i + 1

                #print("total bit length  " + str((bit_length - 1)))
                # if (i < step):
                # pointer = pointer + 1
                mod_inv = self.get_inv_status((_pointer - (bit_length - 1)), (bit_length - 1))
                # print(mod_inv.registers)
                if (mod_inv['result'] == self.result_success):
                    li_reg = mod_inv['msg']
                else:
                    #print('Error!!  ' + mod_inv['msg'])
                    exit()
                param_key = 0

                for i in li_reg:
                    # print(i)
                    #print("name : " + str(self.li_key[(_pointer - (bit_length - 1)) + param_key]) + ",  Address : " + str(
                        #self.li_val[(_pointer - (bit_length - 1)) + param_key]))
                    _param[self.li_key[(_pointer - (bit_length - 1)) + param_key]] = i
                    param_key = param_key + 1
                # print("address:" + str(value) + ", name: " + key + " value:" + str(vv))
                # pointer = pointer + step
                #print(_pointer)
                #print _param.values()
                #print len(_param.values())
            if (_Total - _pointer < _step):
                #print("move to last group")
                mod_inv = self.get_inv_status(_pointer, _Total - _pointer)
                if (mod_inv['result'] == self.result_success):
                    li_reg = mod_inv['msg']
                else:
                    #print('Error!!  ' + mod_inv['msg'])
                    exit()
                param_key = 0
                for i in li_reg:
                    _param[self.li_key[_pointer + param_key]] = i
                    param_key = param_key + 1

                #print _param
            self.client.close()
            for k,v in _param.items():
                self.set_variable(k, v)


        except Exception as er:
            print "classAPI_KMITL_Inverter: ERROR: Reading Modbus registers at getDeviceStatus:"
            print er
            getDeviceStatusResult = False

        if getDeviceStatusResult==True:
            self.set_variable('offline_count',0)
        else:
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    #method2: POST Open the port and Change status
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




    def connect(self):
        self.client = ModbusTcpClient('esp8266-mbb.local', port=502)
        self.client.connect()

    def load_reg(self,filename):
        f = open(filename, 'r')
        reader = csv.DictReader(f)
        csvrows = list(reader)
        i = 0

        for csvdata in csvrows:
            if i >= 1:
                str_key = csvdata['Name'].replace(" ", "_")
                # param[str_key] = csvdata['Address']
                self.li_key.append(str_key)
                self.li_val.append(csvdata['Address'])
                # print(param[str_key])
                # print(csvdata['Name'])
            i = i + 1
            # print(csvdata)
            # print(str_key)
            # print(i)
        # print(param)
        return len(csvrows) - 1

    def get_inv_status(self,value, _step):

        result = {}
        try:
            self.connect()
        except Exception:
            result['result'] = self.result_fail
            result['msg'] = self.msg_connect_fail
            return result
        # get Grid voltag
        # volt = client.read_holding_registers(25207,1,unit=4)
        # print(int(li_val[value]))
        if (int(value) < 1000):
            try:
                volt = self.client.read_holding_registers(int(self.li_val[value]), _step, unit=4)
            except Exception:
                result['result'] = self.result_fail
                result['msg'] = self.msg_get_fail
                return result

        elif (int(value) > 1000):
            try:
                #print(value)
                #print(_step)
                volt = self.client.read_holding_registers(int(value), _step, unit=4)
            except Exception:
                result['result'] = self.result_fail
                result['msg'] = self.msg_get_fail
                return result

        # print(volt.registers)
        # time.sleep(2)
        result['result'] = self.result_success
        result['msg'] = volt.registers
        return result

    def set_use_mode(self,_mode):
        if (_mode > 4):
            _mode = 1
        try:
            self.connect()
        except Exception:
            result = {'result': 'Fail', 'msg': 'can not connect to Inverter'}
            return result
        self.client.write_register(20109, _mode, unit=4)
        Inv = self.get_inv_status(20109, 1)
        if (Inv['result'] == self.result_success):
            Inv_msg = Inv['msg']
            Inv_mode = int(Inv_msg[0])
        else:
            print('Error!!  ' + self.mod_inv['msg'])
            return Inv
        msg = ''
        # print(Inv_mode)
        if (Inv_mode == 0):
            msg = 'PL mode'
        elif (Inv_mode == 1):
            msg = 'FL mode'
        elif (Inv_mode == 2):
            msg = 'FS mode'
        elif (Inv_mode == 3):
            msg = 'UPS mode'
        elif (Inv_mode == 4):
            msg = 'PO mode'
        result = {'result': 'Success'}
        result['msg'] = msg
        return result

#This main method will not be executed when this class is used as a module
def main():
    Inverter = API(model='VC1000',type='VAV',api='API',address='192.168.1.60:4')

    #Inverter.getDeviceStatus()
    Inverter.setDeviceStatus({"mode":"Po"})




if __name__ == "__main__": main()