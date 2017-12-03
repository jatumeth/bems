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
import subprocess as sp
import time
from azure.storage.blob import ContentSettings
from azure.storage.blob import BlockBlobService
import os

RTSP_URL = 'rtsp://admin:12345678@192.168.1.107/onvif/profile2/media.smp'
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
    label            GET          label in string
    illuminance      GET          illuminance
    temperature      GET          temporary target heat setpoint (floating point in deg F)
    battery          GET          percent battery of OpenClose censor
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
    def getDeviceStatus(self):
        try:
            headers = {"Authorization": self.get_variable("bearer")}
            url = str(self.get_variable("url") + self.get_variable("device"))
            r = requests.get(url,
                             headers=headers, timeout=20);
            print(" {0}Agent is querying its current status (status:{1}) please wait ...")
            format(self.variables.get('agent_id', None), str(r.status_code))
            if r.status_code == 200:
                getDeviceStatusResult = False
                self.getDeviceStatusJson(r.text)
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
            print('ERROR: classAPI_OpenClose failed to getDeviceStatus')

    def getDeviceStatusJson(self, data):

        conve_json = json.loads(data)
        print conve_json
        self.set_variable('contact', str(conve_json["contact"]))

        if self.get_variable('contact') == 'closed':
            print "close"
        elif self.get_variable('contact') == 'open':
            print "open"
            print('Start Recorder')
            fileName = str(time.strftime('%Y%m%d')) + "-" + str(time.strftime('%H%M%s'))

            try:
                sp.call(
                    'ffmpeg -y -r 15 -rtsp_transport tcp -i rtsp://admin:12345678@192.168.1.107/onvif/profile2/media.smp -vf "scale=320:240" -c:v libx264 -crf 30 -t 30 -preset ultrafast -tune zerolatency  -b:v 64k -bufsize 192k -an -dn /home/dell-hive01/workspace/peahive_addons/cognitive-services/RecEvent/%s.mp4' % (fileName), shell=True, stdout=sp.PIPE)
                # print("Try Record")
                # sp.call('ffmpeg -y -r 20 -t 10 -f avfoundation -i 0 -vf "scale=320:240" -c:v libx264 -an -dn ./RecEvent/%s.mp4' % (fileName),shell=True, stdout=sp.PIPE)  # for FaceTime Camera
                print("Record Successful")
                print("Try to Upload into Blob")
                filename_full = fileName + ".mp4"

            except Exception as e:
                print(e)
                pass
            except IOError as e:
                print("IO Error {}".format(str(e)))
                pass

            print("Finish")
            print("Start Upload into Azure Blob")
            try:
                block_blob_service = BlockBlobService(account_name='peahivedevstorage',
                                                      account_key='xZD+d6eUa8PnfFOZkyjJn6K3BUXrqzPUm2aHzpArl2N4cP9cruM/SFVesTirn1jk91vtEG2jMc77U5y1dioPag==')

                filePath = os.path.dirname(os.path.realpath('./RecEvent/*.mp4'))
                block_blob_service.create_blob_from_path(
                    'videoclip',
                    'intrusion',
                    '/home/dell-hive01/workspace/peahive_addons/cognitive-services/RecEvent/'+filename_full,
                    content_settings=ContentSettings(content_type='video/mp4')
                )

                print("Upload Complete")

            except Exception as e:
                print("Upload Fail")
                print(e)
                pass

    def printDeviceStatus(self):

        print(" the current status is as follows:")
        print(" contact = {}".format(self.get_variable('contact')))

# This main method will not be executed when this class is used as a module
def main():
    # create an object with initialized data from DeviceDiscovery Agent
    # requirements for instantiation1. model, 2.type, 3.api, 4. address

    OpenClose = API(model='OpenClose',type='illuminance',api='API3', agent_id='OpenCloseAgent',url = 'https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/314fe2f7-1724-42ed-86b6-4a8c03a08601/contactSensors/', bearer = 'Bearer 0291cb9f-168e-490e-b337-2d1a31abdbf4',device = 'd8e492ee-18c7-49ee-af3d-4c4d65747585')
    OpenClose.getDeviceStatus()
    #OpenClose.printDeviceStatus()

if __name__ == "__main__": main()