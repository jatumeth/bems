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

import json
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
        self.only_white_bulb = None
        # to initialize the only white bulb value
        # self.getDeviceStatus()
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
    wind_speed      GET          wind_speed (m/s)
    city            GET          city
    country         GET          country
    temp_c          GET          temperature in celsius
    humidity        GET          humidity %
    observ_time     GET          observ_time in UTC
    weather         GET          weather
    location        GET          observ_time in UTC
    icon            GET          weather
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
        url = self.get_variable("url")
        try:
            r = requests.get(url, timeout=20);
            print(" {0}Agent is querying its current status (status:{1}) please wait ...")
            format(self.variables.get('agent_id', None), str(r.status_code))
            if r.status_code == 200:
                getDeviceStatusResult = False
                self.getDeviceStatusJson(r)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                getDeviceStatusResult = False
            # Check the connectivity
            if getDeviceStatusResult==True:
                self.set_variable('offline_count', 0)
            else:
                self.set_variable('offline_count', self.get_variable('offline_count')+1)
        except Exception as er:
            print er
            print('ERROR: classAPI_Weather failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def getDeviceStatusJson(self,data):

        f = data
        json_string = f.json()
        msg = {}
        location = json_string['location']['city']
        tag = 0
        lat = None
        lon = None
        for i in json_string:
            for attr in json_string[i]:

                if (i == "current_observation"):
                    if (attr == 'wind_kph'):
                        msg['wind_speed'] = str(json_string[i][attr])
                    if (attr == 'temp_c'):
                        msg['temp_c'] = str(json_string[i][attr])
                    if (attr == 'observation_time_rfc822'):
                        msg['observ_time'] = str(json_string[i][attr])
                    if (attr == 'weather'):
                        msg['weather'] = str(json_string[i][attr])
                    if (attr == 'relative_humidity'):
                        msg['humidity'] = str(json_string[i][attr])
                    if (attr == 'icon_url'):
                        msg['icon'] = str(json_string[i][attr])
                if (i == "location"):
                    if (attr == 'country_iso3166'):
                        msg['country'] = str(json_string[i][attr])
                    if (attr == 'city'):
                        msg['city'] = str(json_string[i][attr])
                    if (attr == 'lat'):
                        lat = str(json_string[i][attr])
                    if (attr == 'lon'):
                        lon = str(json_string[i][attr])
            if (lon is not None and lat is not None):
                msg['location'] = str(lat) + ", " + str(lon)

            tag = tag + 1

        self.set_variable('wind_speed', float(msg["wind_speed"]))
        self.set_variable('city', msg["city"])
        self.set_variable('country', msg["country"])
        self.set_variable('temp_c', float(msg["temp_c"]))
        self.set_variable('humidity', msg["humidity"])
        self.set_variable('observ_time', msg["observ_time"])
        self.set_variable('weather', msg["weather"])
        self.set_variable('location', msg["location"])
        self.set_variable('icon', msg["icon"])

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" wind_speed = {}".format(self.get_variable('wind_speed')))
        print(" city = {}".format(self.get_variable('city')))
        print(" country = {}".format(self.get_variable('country')))
        print(" temperature = {}".format(self.get_variable('temp_c')))
        print(" humidity = {}".format(self.get_variable('humidity')))
        print(" observ_time' = {}".format(self.get_variable('observ_time')))
        print(" weather'= {}".format(self.get_variable('weather')))
        print(" location= {}".format(self.get_variable('location')))
        print(" icon= {}".format(self.get_variable('icon')))
    # ----------------------------------------------------------------------


# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address


    Weather = API(model='Weather',type='Weather',api='API3',url = 'http://api.wunderground.com/api/380538e19b591277/geolookup/conditions/q/Thailand/Bangkok.json',username='Teerapong', agent_id='WeatherAgent')
    Weather.getDeviceStatus()


if __name__ == "__main__": main()