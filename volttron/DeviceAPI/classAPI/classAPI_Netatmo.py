# -*- coding: utf-8 -*-
from __future__ import division
'''
Copyright © 2014 by Virginia Polytechnic Institute and State University
All rights reserved

Virginia Polytechnic Institute and State University (Virginia Tech) owns the copyright for the BEMOSS software and its
associated documentation (“Software”) and retains rights to grant research rights under patents related to
the BEMOSS software to other academic institutions or non-profit research institutions.
You should carefully read the following terms and conditions before using this software.
Your use of this Software indicates your acceptance of this license agreement and all terms and conditions.

You are hereby licensed to use the Software for Non-Commercial Purpose only.  Non-Commercial Purpose means the
use of the Software solely for research.  Non-Commercial Purpose excludes, without limitation, any use of
the Software, as part of, or in any way in connection with a product or service which is sold, offered for sale,
licensed, leased, loaned, or rented.  Permission to use, copy, modify, and distribute this compilation
for Non-Commercial Purpose to other academic institutions or non-profit research institutions is hereby granted
without fee, subject to the following terms of this license.

Commercial Use If you desire to use the software for profit-making or commercial purposes,
you agree to negotiate in good faith a license with Virginia Tech prior to such profit-making or commercial use.
Virginia Tech shall have no obligation to grant such license to you, and may grant exclusive or non-exclusive
licenses to others. You may contact the following by email to discuss commercial use: vtippatents@vtip.org

Limitation of Liability IN NO EVENT WILL VIRGINIA TECH, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO
LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE
OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS), EVEN IF VIRGINIA TECH OR OTHER PARTY HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGES.

For full terms and conditions, please visit https://bitbucket.org/bemoss/bemoss_os.

Address all correspondence regarding this license to Virginia Tech’s electronic mail address: vtippatents@vtip.org

__author__ = "Warodom Khamphanchai"
__credits__ = ""
__version__ = "1.2.1"
__maintainer__ = "Warodom Khamphanchai"
__email__ = "kwarodom@vt.edu"
__website__ = "kwarodom.wordpress.com"
__status__ = "Prototype"
__created__ = "2014-6-26 09:12:00"
__lastUpdated__ = "2015-02-11 22:29:53"
'''


import json
import requests
import datetime

class API:

    def __init__(self,**kwargs):  # default color is wh     ite
        # Initialized common attributes
        self.variables = kwargs

    # These set and get methods allow scalability
    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none


    '''
    Device Attributes:
    GET: AbsolutePressure (mbar), time_utc (Linux time), Noise (dB), Temperature (C), Humidity (%), Pressure (mbar),
         CO2 (ppm), date_max_temp (Linux time), date_min_temp (Linux time), min_temp (C), max_temp (C)
    Module Attributes:
    GET: time_utc (Linux time), Temperature (C), Humidity (%),
         date_max_temp (Linux time), date_min_temp (Linux time), min_temp (C), max_temp (C)
    '''
    '''
    Attributes:
    indoor device
        noise
        temperature
        humidity
        pressure
        co2
        date_max_temp
        date_min_temp
        max_temp
        min_temp
    
    outdoor module
        outdoor_temperature
        outdoor_humidity
        outdoor_date_max_temp
        date_min_temp
        outdoor_max_temp
        outdoor_min_temp

    '''

    '''
    API available methods:
    1. getDeviceModel(url) GET
    2. getDeviceStatus(url) GET  ****
    3. setDeviceStatus(url, postmsg) POST
    4. identifyDevice(url, idenmsg) POST
    '''


    def getDeviceStatus(self):

        try:

            self.get_variable('url')
            self.get_variable('content')
            self.get_variable('client_id')
            self.get_variable('username')

            self.get_variable('password')
            self.get_variable('scope')
            self.get_variable('client_secret')
            self.get_variable('grant_type')

            r = requests.post(
                url= self.get_variable('url'),
                headers = {
                    "Content-Type":self.get_variable('content'),
                },
                data = {
                    "client_id":self.get_variable('client_id'),
                    "username":self.get_variable('username'),
                    "password":self.get_variable('password'),
                    "scope":self.get_variable('scope'),
                    "client_secret":self.get_variable('client_secret'),
                    "grant_type":self.get_variable('grant_type'),
                    "device_type":self.get_variable('device_type')

                },
                verify = False
            )


            print "{0} Agent is querying its current status (status:{1}) at {2} please wait ...".format(self.variables.get('agent_id',None),
                                                                                                       r.status_code,
                                                                                                       datetime.datetime.now())
            if r.status_code == 200:  # 200 means successfully
                self.getAccessTokenJson(r.content)  # convert string data to JSON object
                # My API (3) (GET https://api.netatmo.net/api/devicelist)
                try:
                    r = requests.get(
                        url="https://api.netatmo.net/api/devicelist",
                        params = {
                            "access_token": self.get_variable("access_token"),
                        },
                        verify = False
                    )

                    self.getDeviceStatusJson(r.content)
                    self.printDeviceStatus()
                except requests.exceptions.RequestException as e:
                    print('HTTP Request failed')
            else:
                print " Received an error from server, cannot retrieve results {}".format(r.status_code)
        except requests.exceptions.RequestException as e:
            print('HTTP Request failed')

    def getAccessTokenJson(self, data):

        _theJSON = json.loads(data)
        try:
            self.set_variable("access_token", _theJSON["access_token"])
            self.set_variable("refresh_token", _theJSON["access_token"])
            self.set_variable("scope", _theJSON["scope"][0])
            self.set_variable("expire_in", _theJSON["expire_in"])
        except:
            print "Error! Netatmo @getAccessTokenJson"

    def getDeviceStatusJson(self, data):

        _theJSON = json.loads(data)
        try:
            # print data
            print _theJSON["body"]["devices"][0]["_id"]
            self.set_variable("noise", _theJSON["body"]["devices"][0]["dashboard_data"]["Noise"])  # dB
            _temperature = float(_theJSON["body"]["devices"][0]["dashboard_data"]["Temperature"])
            self.set_variable("temperature", _temperature) # C
            self.set_variable("humidity", _theJSON["body"]["devices"][0]["dashboard_data"]["Humidity"])  # %
            _pressure = float(_theJSON["body"]["devices"][0]["dashboard_data"]["Pressure"])*0.02953
            self.set_variable("pressure", _pressure)  # inHg
            self.set_variable("co2", _theJSON["body"]["devices"][0]["dashboard_data"]["CO2"])  # ppm
            self.set_variable("date_max_temp", _theJSON["body"]["devices"][0]["dashboard_data"]["date_max_temp"])
            self.set_variable("date_min_temp", _theJSON["body"]["devices"][0]["dashboard_data"]["date_min_temp"])
            _max_temperature = float(_theJSON["body"]["devices"][0]["dashboard_data"]["max_temp"])
            self.set_variable("max_temp", _max_temperature)  # C
            _min_temperature = float(_theJSON["body"]["devices"][0]["dashboard_data"]["min_temp"])
            self.set_variable("min_temp", _min_temperature)  # C
            self.set_variable("device_type", 'weather station')  # C
        except:
            print "Error! Netatmo Indoor @getDeviceStatusJson"

        try:
            _outdoor_temperature = float(_theJSON["body"]["modules"][0]["dashboard_data"]["Temperature"])
            self.set_variable("outdoor_temperature", _outdoor_temperature)  # C
            self.set_variable("outdoor_humidity", _theJSON["body"]["modules"][0]["dashboard_data"]["Humidity"])  # %
            self.set_variable("outdoor_date_max_temp",
                              _theJSON["body"]["modules"][0]["dashboard_data"]["date_max_temp"])
            self.set_variable("outdoor_date_min_temp",
                              _theJSON["body"]["modules"][0]["dashboard_data"]["date_min_temp"])
            _outdoor_max_temperature = float(_theJSON["body"]["modules"][0]["dashboard_data"]["max_temp"])
            self.set_variable("outdoor_max_temp", _outdoor_max_temperature)  # C
            _outdoor_min_temperature = float(_theJSON["body"]["modules"][0]["dashboard_data"]["min_temp"])
            self.set_variable("outdoor_min_temp", _outdoor_min_temperature)  # C
        except:
            print "Error! Netatmo Outdoor @getDeviceStatusJson"



    def printDeviceStatus(self):
        print " Netatmo indoor device"
        print("     noise = {} dB".format(self.get_variable('noise')).upper())
        print("     temperature = {} C".format(self.get_variable('temperature')).upper())
        print("     humidity = {} %".format(self.get_variable('humidity')).upper())
        print("     pressure = {} inHg".format(self.get_variable('pressure')).upper())
        print("     co2 = {} ppm".format(self.get_variable('co2')).upper())
        print("     date_max_temp = {} unix timestamp".format(self.get_variable('date_max_temp')).upper())
        print("     date_min_temp = {} unix timestamp".format(self.get_variable('date_min_temp')).upper())
        print("     max_temp = {} C".format(self.get_variable('max_temp')).upper())
        print("     min_temp = {} C".format(self.get_variable('min_temp')).upper())
        print " Netatmo outdoor module"
        print("     outdoor_temperature = {} C".format(self.get_variable('outdoor_temperature')).upper())
        print("     outdoor_humidity = {} %".format(self.get_variable('outdoor_humidity')).upper())
        print("     outdoor_date_max_temp = {} unix timestamp".format(self.get_variable('outdoor_date_max_temp')).upper())
        print("     outdoor_date_min_temp = {} unix timestamp".format(self.get_variable('outdoor_date_min_temp')).upper())
        print("     outdoor_max_temp = {} C".format(self.get_variable('outdoor_max_temp')).upper())
        print("     outdoor_min_temp = {} C".format(self.get_variable('outdoor_min_temp')).upper())

        print("     device_type = {} ".format(self.get_variable('device_type')).upper())

def main():

    Netatmo = API(model='Weather Station',agent_id='netatmo1', api='API1', address='https://api.netatmo.net/api/devicelist',device_type="weather station",
                  url="https://api.netatmo.net/oauth2/token",client_id="592fc89f743c360b3a8b53e9",username='smarthome.pea@gmail.com',password = '28Sep1960',
                  scope ='read_station',client_secret = 'nPoa7wZfyq7VbCbF7Gqzo5bI1V5',grant_type = 'password',content = 'application/x-www-form-urlencoded;charset=UTF-8')
    print("{0} agent is initialzed for {1} using API={2} at {3}".format(Netatmo.get_variable('agent_id'),
                                                                        Netatmo.get_variable('model'),
                                                                        Netatmo.get_variable('api'),
                                                                        Netatmo.get_variable('address'),
                                                                        Netatmo.get_variable('url'),
                                                                        Netatmo.get_variable('client_id'),
                                                                        Netatmo.get_variable('username'),
                                                                        Netatmo.get_variable('scope'),
                                                                        Netatmo.get_variable('client_secret'),
                                                                        Netatmo.get_variable('grant_type'),
                                                                        Netatmo.get_variable('content')))


    Netatmo.getDeviceStatus()

if __name__ == "__main__": main()