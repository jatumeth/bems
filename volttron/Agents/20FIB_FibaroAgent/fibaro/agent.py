# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime
import logging
import sys
import settings
from pprint import pformat
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import importlib
import random
import json
import socket
#import psycopg2
#import psycopg2.extras
import pyrebase
import time
import requests
# from requests_toolbelt.multipart.encoder import MultipartEncoder
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
def fibaroing_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # List of all keywords for a fibaroing agent
    agentAPImapping = dict(status=[], brightness=[], color=[], saturation=[], power=[])
    log_variables = dict(status='text', brightness='double', hexcolor='text', power='double', offline_count='int')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_monitor_time = config.get('device_monitor_time', DEFAULT_MONITORING_TIME)
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    if model == "Philips hue bridge":
        hue_username = get_config('username')
    else:
        hue_username = ''
    device_type = get_config('type')
    device = get_config('device')
    bearer = get_config('bearer')
    url = get_config('url')
    api = get_config('api')
    address = get_config('ipaddress')
    _address = address.replace('http://', '')
    _address = address.replace('https://', '')
    try:  # validate whether or not address is an ip address
        socket.inet_aton(_address)
        ip_address = _address
    except socket.error:
        ip_address = None
    identifiable = get_config('identifiable')


    # construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    topic_device_control = '/ui/agent/update/'+_topic_Agent_UI_tail
    print(topic_device_control)
    gateway_id = settings.gateway_id

    class fibaroingAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(fibaroingAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.model = model
            self.device_type = device_type
            self.url = url
            self.device = device
            self.bearer = bearer
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.fibaro = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self._agent_id,
                                         bearer=self.bearer, device=self.device, url=self.url)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            # self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")
            self.status_old = ''
            self.status_old2 = ''
            self.status_old3 = ''
            self.status_old4 = ''
            self.status_old5 = ''
            self.status_old6 = ''

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))


        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):

            self.fibaro.getDeviceStatus()
            self.StatusPublish(self.fibaro.variables)


            # TODO update local postgres
            # self.publish_local_postgres()


            if (self.fibaro.variables['STATUS'] != self.status_old or
                    self.fibaro.variables['TEMPERATURE'] != self.status_old2 or
                    self.fibaro.variables['ILLUMINANCE'] != self.status_old3 or
                    self.fibaro.variables['TAMPER'] != self.status_old4 or
                    self.fibaro.variables['BATTERY'] != self.status_old5 or
                    self.fibaro.variables['HUMIDITY'] != self.status_old6):
                self.publish_firebase()
                # self.publish_postgres()
                # self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)
            else:
                pass

            self.status_old = self.fibaro.variables['STATUS']
            self.status_old2 = self.fibaro.variables['TEMPERATURE']
            self.status_old3 = self.fibaro.variables['ILLUMINANCE']
            self.status_old4 = self.fibaro.variables['TAMPER']
            self.status_old5 = self.fibaro.variables['BATTERY']
            self.status_old6 = self.fibaro.variables['HUMIDITY']

        def publish_firebase(self):

            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(
                    datetime.now().replace(microsecond=0).isoformat())
                # db.child(gateway_id).child('devices').child(agent_id).child("device_status").set(self.motion.variables['device_status'])
                db.child(gateway_id).child('devices').child(agent_id).child("TYPE").set(
                    self.fibaro.variables['device_type'])
                db.child(gateway_id).child('devices').child(agent_id).child("TEMPERATURE").set(
                    self.fibaro.variables['TEMPERATURE'])
                db.child(gateway_id).child('devices').child(agent_id).child("TAMPER").set(
                    self.fibaro.variables['TAMPER'])
                db.child(gateway_id).child('devices').child(agent_id).child("BATTERY").set(
                    self.fibaro.variables['BATTERY'])
                db.child(gateway_id).child('devices').child(agent_id).child("ILLUMINANCE").set(
                    self.fibaro.variables['ILLUMINANCE'])
                db.child(gateway_id).child('devices').child(agent_id).child("HUMIDITY").set(
                    self.fibaro.variables['HUMIDITY'])
                db.child(gateway_id).child('devices').child(agent_id).child("STATUS").set(
                    self.fibaro.variables['STATUS'])

                db.child(gateway_id).child('global').child("indoor_temperature").set(self.fibaro.variables['TEMPERATURE'])
                print "-----------------update firebase--------------"


            except Exception as er:
                print er

        def publish_azure_iot_hub(self, activity_type, username):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.fibaro.variables)
            x = {}
            x["device_id"] = self.fibaro.variables['agent_id']
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["unixtime"] = int(time.time())
            x["device_status"] = self.fibaro.variables['STATUS']
            x["device_type"] = 'multisensor'
            x["tamper"] = self.fibaro.variables['TAMPER']
            x["temperature"] = self.fibaro.variables['TEMPERATURE']
            x["battery"] = self.fibaro.variables['BATTERY']
            x["humidity"] = self.fibaro.variables['HUMIDITY']
            x["illuminance"] = self.fibaro.variables['ILLUMINANCE']

            x["activity_type"] = 'multisensor'
            x["username"] = 'arm'
            x["device_name"] = 'MY Fibaro'

            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))

        def publish_postgres(self):
            print "update post"

            # postgres_url = settings.POSTGRES['postgres']['url']
            # postgres_Authorization = settings.POSTGRES['postgres']['Authorization']
            # postgres_Authorization = 'ad1eb50802c61eb52d8311cf3d4590c7deacff2e'
            #
            # m = MultipartEncoder(
            #     fields={
            #         "STATUS": str(self.fibaro.variables['STATUS']),
            #         "device_id": str(self.fibaro.variables['agent_id']),
            #         "device_type": "multisensor",
            #         "TAMPER": str(self.fibaro.variables['TAMPER']),
            #         "TEMPERATURE": str(self.fibaro.variables['TEMPERATURE']),
            #         "BATTERY": str(self.fibaro.variables['BATTERY']),
            #         "HUMIDITY": str(self.fibaro.variables['HUMIDITY']),
            #         "ILLUMINANCE": str(self.fibaro.variables['ILLUMINANCE']),
            #         "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
            #     }
            # )
            #
            # r = requests.put(postgres_url,
            #                  data=m,
            #                  headers={'Content-Type': m.content_type,
            #                           "Authorization": postgres_Authorization,
            #                           })
            # print r.status_code

        def StatusPublish(self,commsg):
            # TODO this is example how to write an app to control AC


            topic = str('/agent/zmq/update/hive/999/' + str(self.fibaro.variables['agent_id']))
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
            self.fibaro.setDeviceStatus(json.loads(message))

    Agent.__name__ = 'fibaroingAgent'
    return fibaroingAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(fibaroing_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
