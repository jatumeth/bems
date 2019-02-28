# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime
import logging
import sys
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.agent import utils
import importlib
import json
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

#---Firebase config---
apiKeyconfig = settings.CHANGE['change']['apiKeyLight']
authDomainconfig = settings.CHANGE['change']['authLight']
dataBaseconfig = settings.CHANGE['change']['databaseLight']
stoRageconfig = settings.CHANGE['change']['storageLight']

#----Firebase config----
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
#----Firebase config----

# Step1: Agent Initialization
def plug_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    device_monitor_time = config.get('device_monitor_time', DEFAULT_MONITORING_TIME)
    model = get_config('model')
    device_type = get_config('type')
    deviceid = get_config('deviceid')
    api = get_config('api')
    address = get_config('ipaddress')
    port = get_config('port')

    # construct _topic_Agent_UI based on data obtained from DB
    topic_device_control = '/hiveos/devices/'+ agent_id
    print(" topic_device_control >> {}".format(topic_device_control))
    gateway_id = settings.gateway_id

    class PlugAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """
        def __init__(self, config_path, **kwargs):
            super(PlugAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self.model = model
            self.device_type = device_type
            self.address = address
            self.deviceid = deviceid
            self.port = port

            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Plug = self.apiLib.API(model=self.model, types =self.device_type, agent_id=self._agent_id,
                                           ip=self.address,port=self.port)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))
            self.status_old = ""
            self.gettoken()

        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):

            self.Plug.getDeviceStatus()
            self.StatusPublish(self.Plug.variables)

        def gettoken(self):

            self.api_token = 'c8cb977c7622c312a93fa84d7e33e8b21bf6ed78'

        def publish_firebase(self):
            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('devices').child(agent_id).child("TYPE").set(self.Plug.variables['label'])
                db.child(gateway_id).child('devices').child(agent_id).child("STATUS").set(self.Plug.variables['status'])
            except Exception as er:
                print er

        def publish_postgres(self):
            postgres_url = 'https://peahivemobilebackends.azurewebsites.net/api/v2.0/devices/'
            postgres_Authorization = 'Token '+self.api_token
            print str(self.Plug.variables['status'])
            print str(self.Plug.variables['agent_id'])

            m = MultipartEncoder(
                fields={
                    "status": str(self.Plug.variables['status']),
                    "device_id": str(self.Plug.variables['agent_id']),
                    "device_type": "switch",
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

        def publish_azure_iot_hub(self, activity_type, username):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.Plug.variables)
            datatoiothub = {}
            datatoiothub["device_id"] = self.Plug.variables['agent_id']
            datatoiothub["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            datatoiothub["unixtime"] = int(time.time())
            datatoiothub["device_status"] = self.Plug.variables['status']
            datatoiothub["device_type"] = 'plugload'
            datatoiothub["activity_type"] = activity_type
            datatoiothub["username"] = username
            datatoiothub["device_name"] = 'Smart Plug'
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(datatoiothub), 'utf8'))

        def StatusPublish(self, commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/agent/zmq/update/hive/999/' + str(self.Plug.variables['agent_id']))
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)


        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            message = json.loads(message)
            if 'status' in message:
                self.Plug.variables['status'] = str(message['status'])
            self.Plug.setDeviceStatus((message))


    Agent.__name__ = '03WSP_PlugAgent'
    return PlugAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(plug_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
