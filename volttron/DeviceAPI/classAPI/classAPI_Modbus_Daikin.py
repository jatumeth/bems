# -*- coding: utf-8 -*-
'''

#__author__ = "HiVETeam"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "HiVE Team"
#__email__ = "peahive@gmail.com"
#__website__ = "www.peahive.github.io"
#__created__ = "2018-09-12 12:04:50"
#__lastUpdated__ = "2018-03-14 11:23:33"
print
'''

import requests
import time
import time

from pymodbus.client.sync import ModbusTcpClient
# from pymodbus.constants.Defaults import ModbusTcpClient
from pymodbus.constants import Defaults


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
        url = str(self.get_variable("url"))
        parity = str(self.get_variable("party"))
        baudrate = str(self.get_variable("baudrate"))
        port = str(self.get_variable("port"))
        startregis = int(self.get_variable("startregisr"))
        
        Defaults.Parity = str(parity)
        Defaults.Baudrate = int(baudrate)
        client = ModbusTcpClient(str(url), port=int(port))
        client.connect()
        print(client.connect())
        # print ModbusTcpClient.port
        # request = client.read_holding_registers(0, 8, unit=1,parity= str(parity),stopbits=1,bytesize=8,baudrate=int(baudrate))
        # request = client.read_holding_registers(startregis, 32, unit=1)
        startregis = startregis
        result1 = client.read_input_registers(startregis, 5, unit=1)
        getstatus = str(hex(result1.registers[0])[-1])
        getswing = str(hex(result1.registers[0])[-3])
        getmode = str(hex(result1.registers[1])[-1])
        client.close()
        print result1.registers


        if(getmode == '0'):
            mode = 'FAN'
        if(getmode == '2'):
            mode = 'COLD'
        if(getmode == '7'):
            mode = 'DEHUMDIFICATOR'
        if(getstatus == '1'):
            status = 'ON'
        if (getstatus == '0'):
            status = 'OFF'
        if (getswing == '7'):
            swing = 'ON'
        if (getswing == '4'):
            swing = 'OFF'


        try:
            getspeed = str(hex(result1.registers[0])[-4])
            if str(getspeed) == 'x':
                fan = 'AUTO'

            if (getspeed == '1'):
                fan = '1'
            if (getspeed == '2'):
                fan = '2'
            if (getspeed == '3'):
                fan = '3'
            if (getspeed == '4'):
                fan = '4'
            if (getspeed == '5'):
                fan = '5'
            if (getspeed == '0'):
                fan = 'AUTO'
        except:

            print ""


        stemp = (int(result1.registers[2])/10)
        ctemp = (float(result1.registers[4]/10))
        set_humidity = '70'

        self.set_variable('status', status)
        self.set_variable('current_temperature', ctemp)
        self.set_variable('set_temperature', stemp)
        self.set_variable('set_humidity', set_humidity)
        self.set_variable('mode', mode)

        try:
            self.set_variable('fan', fan)
        except:
            print "er"
        # self.set_variable('swing', swing)

        self.printDeviceStatus()

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" status = {}".format(self.get_variable('status')))
        print(" current_temperature = {}".format(self.get_variable('current_temperature')))
        print(" set_temperature = {}".format(self.get_variable('set_temperature')))
        print(" set_humidity = {}".format(self.get_variable('set_humidity')))
        print(" mode = {}".format(self.get_variable('mode')))
        print(" swing = {}".format(self.get_variable('swing')))

        try:
            print(" fan = {}".format(self.get_variable('fan')))
        except:
            print "er"


        print("")
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        
        url = str(self.get_variable("url"))
        parity = str(self.get_variable("party"))
        baudrate = str(self.get_variable("baudrate"))
        port = str(self.get_variable("port"))
        startregis = int(self.get_variable("startregis"))


        for k, v in postmsg.items():
            if k == 'status':
                if (postmsg['status']) == "ON":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '5761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    print startregis
                    print firtdec
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()
                    print "on"


                elif (postmsg['status']) == "OFF":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '5760'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    print startregis
                    print firtdec
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()
                    print "off"

            if k == 'mode':

                if (postmsg['mode']) =="COOL":
                     Defaults.Parity = str(parity)
                     Defaults.Baudrate = int(baudrate)
                     client = ModbusTcpClient(str(url), port=int(port))
                     client.connect()
                     startregis = startregis
                     secondhex = '0202'  # input in HEX
                     seconddec = int(secondhex, 16)
                     result = client.write_register((startregis + 1), seconddec,
                                                    unit=1)  # mode  2 == cooling  7 == dry mode 0207  #512==FAN  #514 == Cool  #519=Dry

                     client.close()

                elif (postmsg['mode']) =="DEHUMDIFICATOR":
                     Defaults.Parity = str(parity)
                     Defaults.Baudrate = int(baudrate)
                     client = ModbusTcpClient(str(url), port=int(port))
                     client.connect()
                     startregis = startregis
                     secondhex = '0207'  # input in HEX
                     seconddec = int(secondhex, 16)
                     result = client.write_register((startregis + 1), seconddec,
                                                    unit=1)
                     client.close()



                elif (postmsg['mode']) =="FAN":
                     Defaults.Parity = str(parity)
                     Defaults.Baudrate = int(baudrate)
                     client = ModbusTcpClient(str(url), port=int(port))
                     client.connect()
                     startregis = startregis
                     secondhex = '0200'  # input in HEX
                     seconddec = int(secondhex, 16)
                     print('second in dec: {}'.format(seconddec))
                     result = client.write_register((startregis + 1), seconddec,
                                                    unit=1)
                     client.close()

            if k == 'fan':
                if (postmsg['fan']) == "1":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '1761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close

                    client.close()

                elif (postmsg['fan']) == "2":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '2761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close

                    client.close()

                elif (postmsg['fan']) == "3":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '3761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()

                elif (postmsg['fan']) == "4":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '4761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()

                elif (postmsg['fan']) == "5":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '5761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close

                    client.close()

                elif (postmsg['fan']) == "AUTO":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '0761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()

                elif (postmsg['fan']) == "SILENT":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '0761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()

            if k == 'swing':
                if (postmsg['swing']) == "ON":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '0761'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close

                    client.close()

                elif (postmsg['swing']) == "OFF":
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    firsthex = '0661'  # input in HEX  Fan speed high =5061  Fan speed low =1061
                    firtdec = int(firsthex, 16)
                    result = client.write_register(startregis, firtdec, unit=1)  # open /close
                    client.close()
                    
            if k == 'stemp':
                    stemp = postmsg['stemp']
                    Defaults.Parity = str(parity)
                    Defaults.Baudrate = int(baudrate)
                    client = ModbusTcpClient(str(url), port=int(port))
                    client.connect()
                    startregis = startregis
                    result = client.write_register(startregis + 2, (int(stemp)*10), unit=1)  # temp 25 == 250
                    client.close()


    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity


# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address


    AC = API(model='daikin', type='AC', api='API', agent_id='ACAgent',url ='192.168.1.104',port=502,parity ='E',baudrate=9600,startregis=2006,startregisr=2012 )
    # AC.setDeviceStatus({'swing':'ON','device': '1DAIK1200138'})

    # AC.setDeviceStatus({"status": "ON", "device": "1DAIK", "mode": "COLD", "username":"hive5"})
    # time.sleep(2)
    # AC.setDeviceStatus({"status": "OFF", "device": "1DAIK", "mode": "COLD", "username": "hive5"})
    # AC.setDeviceStatus({'stemp': '21', 'device': '1DAIK1200138'})
    # AC.setDeviceStatus({'fan': '1', 'device': '1DAIK1200138'})
    # AC.setDeviceStatus({"status": "ON"})
    time.sleep(5)
    AC.getDeviceStatus()

    # AC.setDeviceStatus({"status": "OFF", "device": "1DAIK", "mode": "COLD", "username":"hive5"})



if __name__ == "__main__": main()

