# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime
import logging
import sys
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.agent import utils
import importlib
import json
import socket
import pyrebase
import settings
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'

apiKeyconfig = settings.CHANGE['change']['apiKeyLight']
authDomainconfig = settings.CHANGE['change']['authLight']
dataBaseconfig = settings.CHANGE['change']['databaseLight']
stoRageconfig = settings.CHANGE['change']['storageLight']

try:
    config = {
      "apiKey": apiKeyconfig,
      "authDomain": authDomainconfig,
      "databaseURL": dataBaseconfig,
      "storageBucket": stoRageconfig,
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except Exception as er:
    print er

# Step1: Agent Initialization
def lighting_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    gateway_id = settings.gateway_id

    class LightingAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(LightingAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")
            self.gettoken()

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))
            self.gettoken()

        def publish_firebase(self):

            try:

                db.child(gateway_id).child('devices').child(self.agent_id).child("dt").set(
                    datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('devices').child(self.agent_id).child("STATUS").set(self.device_status) #1111111111    +       #22222222222222222222
                db.child(gateway_id).child('devices').child(self.agent_id).child("TYPE").set('lightinglogging')
                print('------------------update firebase--------------------')
            except Exception as er:
                print er

        def publish_azure_iot_hub(self):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            x = {}
            x["device_id"] = self.agent_id
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["unixtime"] = int(time.time())
            x["device_status"] = self.device_status
            x["activity_type"] = 'devicemonitor'
            x["username"] = self.agent_id
            x["device_name"] = 'In-wall'
            x["device_type"] = "lightinglogging"
            print x
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))
            print('--------------update azure--------------')

        def publish_postgres(self):

            postgres_url = 'https://peahivemobilebackends.azurewebsites.net/api/v2.0/devices/'
            postgres_Authorization = 'Token '+self.api_token

            m = MultipartEncoder(
                fields={
                    "status": str(self.device_status),
                    "device_id": str(self.agent_id ),
                    "device_type": "lightinglogging",
                    "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
                }
            )

            r = requests.put(postgres_url,
                             data=m,
                             headers={'Content-Type': m.content_type,
                                      "Authorization": postgres_Authorization,
                                      })
            print r.status_code
            print('-------------------update postgres---------------')


        def gettoken(self):
            
            self.api_token = '701308a85458bab3ec83d9a08e678c545b87ec67'

        @PubSub.subscribe('pubsub', '/agent/zmq/update/hive/999/inwallswitchlog')
        def match_logging(self, peer, sender, bus, topic, headers, message):
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)

            message = json.loads(message)
            try:
                self.device_status = message['device_status']
                self.agent_id = message['agent_id']
                self.publish_postgres()
                self.publish_azure_iot_hub()
                self.publish_firebase()


            except Exception as er:
                print er

    Agent.__name__ = '02ORV_InwallLightingAgent'
    return LightingAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(lighting_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
