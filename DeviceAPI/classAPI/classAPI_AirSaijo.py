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
import psycopg2

class API:
    # 1. constructor : gets call every time when create a new class
    # requirements for instantiation1. model, 2.type, 3.api, 4. address
    def __init__(self,**kwargs):

        #,model,device_type,api,address,macaddress,agent_id,db_host,db_port,db_user,db_password,db_database,config_path,device_id):
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval', 6000)
        self.only_white_bulb = None
        self.change = True
        self.powerStat = 0
        self.mode = 0
        self.setTemp = 25
        self.roomTemp = 30
        self.setRH = 40
        self.roomRH = 0
        self.inFan = 0
        self.louPos = 0
        self.Opt1 = 0b10000
        self.LogError = [0, 0, 0, 0, 0]
        self.ETToffset = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.FacReReq = 0
        self.systemPowerInput = 0
        self.inExv = [0, 0]
        self.timeOnOff = [0, 0, 0, 0]
        self.runtimeCleaning = [0, 0]
        self.temp = []

        self.powerStatO = 0
        self.modeO = 0
        self.setTempO = 25
        self.setRHO = 40
        self.inFanO = 0
        self.louPosO = 0
        self.data33 = ""
    def renewConnection(self):
        pass
    #
    #
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
    def gettoken(self):

        url = "https://saijom2s.ddns.net/check_login.php"
        post_data = {'cus_email': 'tisanaluk@hotmail.com', 'cus_password': 'testair'}
        try:

            r = requests.post(url, data=post_data, verify=False)
            print("{0} Agent is querying its current status (status:{1}) please wait ...".format(self.get_variable('agent_id'), r.status_code))
            format(self.variables.get('agent_id', None), str(r.status_code))
            if r.status_code == 200:
                content0 = eval(r.content.decode().replace('null', 'None').replace('true', 'True').replace('false', 'False'))
                self.token = content0['data']['cus_token']
            else:
                print (" Received an error from server, cannot retrieve results")
        except Exception as er:
            print er
            print('ERROR: classAPI_PhilipsHue failed to getDeviceStatus')

        file = open('token.txt', 'w')
        file.write(self.token)
        file.close()
        f1 = open("token.txt", "r")
        self.TXTtoken =f1.readline()
        f1.close()
        print "New Token"
        print self.TXTtoken

    def getDeviceStatus(self):

        #self.gettoken()
        self.getDeviceStatusJson()
        self.printDeviceStatus()

    def getDeviceStatusJson(self):

        temp =[]
        temp.append(ord('R'))
        temp.append(ord('E'))
        temp.append(ord('Q'))
        temp.append(ord('+'))

        temp.append(self.powerStat)
        temp.append(self.mode)
        temp.append(int(self.setTemp * 2))#Airsaijo.setDeviceStatus({"temp" : "26","fan_speed": "3",'status':'ON'})
        temp.append(self.setRH)
        temp.append(self.inFan)
        temp.append(self.louPos)
        temp.append(0b10000)


        for i in range(39):
            temp.append(0)

        data22 = ''

        for i in temp:
            data22 += format(i, '02x')

        try:
            # f1 = open("token.txt", "r")
            # self.TXTtoken = f1.readline()
            # f1.close()
            self.TXTtoken = "41d1ddcee2f7d9f4af323d18ffd4ca87583bf1f20fa4c"

            print "Token is .."
            print self.TXTtoken

            post_url2 = 'https://saijom2s.ddns.net/cmd_data.php'
            post_data2 = {'cus_email': "tisanaluk@hotmail.com", 'cus_token': self.TXTtoken, 'air_command': data22,
                          'air_serial': self.variables['air_serial']}
            r2 = requests.post(post_url2, data=post_data2, verify=False)
            content = eval(r2.content.decode().replace('null', 'None').replace('true', 'True').replace('false', 'False'))
            print content['status']
            if content['status'] == 200:
                print ("content['status'] == 200")
                print (" Get / Received from server is OK")
            else:
                print "Token is change"
                #self.gettoken()
                post_url2 = 'https://saijom2s.ddns.net/cmd_data.php'
                post_data2 = {'cus_email': "tisanaluk@hotmail.com", 'cus_token': self.TXTtoken, 'air_command': data22,
                              'air_serial': self.variables['air_serial']}
                r2 = requests.post(post_url2, data=post_data2, verify=False)
                content = eval(r2.content.decode().replace('null', 'None').replace('true', 'True').replace('false', 'False'))
                print (" Get / Received an error from server, cannot retrieve results")
        except Exception as er:
                print er
                print('Get / ERROR: classAPI_PhilipsHue failed to getDeviceStatus')
        #
        indoor = content["data"]['indoor']
        print "Start Get /  --------------++++++++++++++++++---------"
        data = indoor

        powerStat = int(data[:2], 16)
        data = data[2:]
        mode = int(data[:2], 16)
        data = data[2:]
        setTemp = int(data[:2], 16) * 0.5
        data = data[2:]
        roomTemp = int(data[:2], 16) * 0.25
        data = data[2:]
        setRH = int(data[:2], 16)
        data = data[2:]
        roomRH = int(data[:2], 16)
        data = data[2:]
        inFan = int(data[:2], 16)
        data = data[2:]
        louPos = int(data[:2], 16)
        data = data[2:]
        Opt1 = int(data[:2], 16)
        data = data[2:]

        temp = []
        for i in range(3):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(6):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(2):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(5):
            temp.append(int(data[:2], 16))
            data = data[2:]

        FacReReq = int(data[:2], 16)
        data = data[2:]

        temp = []
        for i in range(2):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(2):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(4):
            temp.append(int(data[:2], 16))
            data = data[2:]

        temp = []
        for i in range(50):
            temp.append(int(data[:2], 16))
            data = data[2:]

        self.powerStatO = int(powerStat)
        self.modeO = int(mode)
        self.setTempO = int(setTemp)
        self.setRHO = int(setRH)
        self.inFanO = int(inFan)
        self.louPosO = int(louPos)

        if int(powerStat) == 0:
            self.set_variable('status', "OFF")
        elif int(powerStat) == 1:
            self.set_variable('status', "ON")
        self.set_variable('current_temperature', int(roomTemp))
        self.set_variable('set_temperature', int(setTemp))
        self.set_variable('current_humidity', int(roomRH))
        self.set_variable('set_humidity', int(setRH))
        self._mode = int(mode)
        if self._mode == 0 :
            self.set_variable('mode', "Cool")
        elif self._mode == 1 :
            self.set_variable('mode', "Fan")
        elif self._mode == 2 :
            self.set_variable('mode', "Dry")
        elif self._mode == 3 :
            self.set_variable('mode', "Heat")
        elif self._mode == 4 :
            self.set_variable('mode', "Auto")
        self.set_variable('fan_speed', int(inFan))
        self.set_variable('fin_angle', int(louPos))

        # print("power stat " + str(powerStat))
        # print("mode " + str(mode))
        # print("setTemp " + str(setTemp))
        # print("roomTemp " + str(int(powerStat)))
        # print("in Fan " + str(inFan))


        print "End Get /  --------------++++++++++++++++++---------"

    def printDeviceStatus(self):

        print(" status = {}".format(self.get_variable('status')))
        print(" current_temperature = {}".format(self.get_variable('current_temperature')))
        print(" set_temperature = {}".format(self.get_variable('set_temperature')))
        print(" current_humidity = {}".format(self.get_variable('current_humidity')))
        print(" mode = {}".format(self.get_variable('mode')))
        print(" fan_speed = {}".format(self.get_variable('fan_speed')))
        print(" fin_angle = {}".format(self.get_variable('fin_angle')))
        print("-------------------------")
        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        print "---start Set ---  ---start Set ---  ---start Set ---"

        self.getDeviceStatus()
        postmsg2 = self.convertPostMsg(postmsg)
        self.powerStat = self.powerStatO
        self.mode = self.modeO
        self.setTemp = self.setTempO
        postmsg2['setRHO'] = self.setRHO
        self.inFan = self.inFanO
        postmsg2['louPos'] = self.louPosO

        for k,v in postmsg2.items():
            if k == 'temp':
                self.setTemp = int((postmsg2['temp']))
            elif k == 'status':
                self.powerStat = int((postmsg2['status']))

            elif k == 'mode':
                self.mode = int((postmsg2['mode']))

            elif k == 'fan_speed':
                self.inFan = int((postmsg2['fan_speed']))
            else:
                m = 1

        temps = []
        temps.append(ord('C'))
        temps.append(ord('M'))
        temps.append(ord('D'))
        temps.append(ord('+'))

        temps.append(int(self.powerStat))
        temps.append(int(self.mode))
        temps.append(int(self.setTemp * 2))
        temps.append(int(self.setRH))
        temps.append(int(self.inFan))
        temps.append(int(self.louPos))
        temps.append(0b10000)

        for i in range(39):
            temps.append(0)

        self.data33 = ''

        for i in temps:
            self.data33 += format(i, '02x')

        try:
            print "*********************"
            print "---Start Set Air SAIJO---   ---Start Set Air SAIJO---  ---Start Set Air SAIJO---"

            post_url3 = 'https://saijom2s.ddns.net/cmd_data.php'
            post_data3 = {'cus_email': "tisanaluk@hotmail.com", 'cus_token': self.TXTtoken, 'air_command': self.data33,
                          'air_serial': self.variables['air_serial']}
            r3 = requests.post(post_url3, data=post_data3, verify=False)

            print "End Set"
            print r3.status_code

            if r3.status_code == 200:
                print (" Received from server is OK")
            else:
                print (" Received an error from server, cannot retrieve results")
        except Exception as er:
            print er
            print('ERROR: classAPI_Air')

        print "---End Set Air SAIJO---   ---End Set Air SAIJO---   ---End Set Air SAIJO---"

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        print "StartconvertPostMsg"
        msgToDevice = {}
        for k,v in postmsg.items():
            if k == 'temp':
                temp1 = str(postmsg.get('temp'))
                msgToDevice['temp'] = int(temp1)
            elif k == 'humidity':
                msgToDevice['humidity'] = postmsg.get('humidity')
            elif k == 'fin_angle':
                msgToDevice['fin_angle'] = postmsg.get('fin_angle')
            elif k == 'fan_speed':
                fan_speed = str(postmsg.get('fan_speed'))
                msgToDevice['fan_speed'] = int(fan_speed)
            elif k == 'mode':
                if postmsg.get('mode') == "cool":
                    msgToDevice['mode'] = 0
                elif postmsg.get('mode') == "fan":
                    msgToDevice['mode'] = 1
                elif postmsg.get('mode') == "dry":
                    msgToDevice['mode'] = 2
                elif postmsg.get('mode') == "heat":
                    msgToDevice['mode'] = 3
                elif postmsg.get('mode') == "auto":
                    msgToDevice['mode'] = 4
            elif k =='status':
                if postmsg.get('status') == "ON":
                    msgToDevice['status'] = 1
                elif postmsg.get('status') == "OFF":
                    msgToDevice['status'] = 0
            else:
                msgToDevice[k] = v

        print(" end convert massage = {}".format(msgToDevice))
        return msgToDevice

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address

    Airsaijo = API(model='Saijo Denki GPS', type='airconditioner', api='classAPI_KMITL_testNetAirSaijo',
                   address='http://192.168.1.13', username='acquired username', agent_id='ACAgent1',
                   device_id="LivingroomAir1",air_serial="1608F00680620")

    #Airsaijo.getDeviceStatus()
    #Airsaijo.setDeviceStatus({"temp" : "24","fan_speed": "1",'status':'ON'})
    #Airsaijo.setDeviceStatus({"status": "ON"})

    # 1   "air_serial": "1608F00680620",  2# "air_serial": "1608F00680619",  Bed     "air_serial": "1604F00640667",



    # 'BedroomAir' or 'LivingroomAir1' or 'LivingroomAir2'

if __name__ == "__main__": main()