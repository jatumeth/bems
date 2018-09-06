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
import psycopg2
import psycopg2.extras
import pyrebase
import time
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests

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

    # List of all keywords for a ac agent
    agentAPImapping = dict(status=[], brightness=[], color=[], saturation=[], power=[])
    log_variables = dict(status='text', brightness='double', hexcolor='text', power='double', offline_count='int')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_monitor_time = config.get('device_monitor_time', DEFAULT_MONITORING_TIME)
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    # if model == "Philips hue bridge":
    #     hue_username = get_config('username')
    # else:
    #     hue_username = ''
    device_type = get_config('type')
    device = get_config('device')
    bearer = get_config('bearer')
    url = get_config('url')
    api = get_config('api')
    username = get_config('username')
    address = get_config('address')
    address = get_config('address')
    address = get_config('address')
    address = "http://192.168.1.106:80"


    # construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    topic_device_control = '/ui/agent/update/'+_topic_Agent_UI_tail
    print(topic_device_control)
    gateway_id = settings.gateway_id

    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class LightingAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(LightingAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.model = model
            self.device_type = device_type
            self.username = username
            self.address = address
            self.user = url
            self.url = url
            self.device = device
            self.bearer = bearer
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Light = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self._agent_id,
                                         bearer=self.bearer, device=self.device, url=self.url,username=self.username,address=self.address)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            self.gettoken()
            self.status_old = ""
            self.status_old2 = ""
            self.status_old3 = ""
            _log.debug("VERSION IS: {}".format(self.core.version()))

        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):

            self.Light.getDeviceStatus()
            self.StatusPublish(self.Light.variables)
            # TODO update local postgres
            # self.publish_postgres()
            # update firebase , posgres , azure
            if (self.Light.variables['status'] != self.status_old or
                    self.Light.variables['brightness'] != self.status_old2 or
                    self.Light.variables['color'] != self.status_old3):
                self.publish_firebase()
                self.publish_postgres()
                self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)
            else:
                pass
            self.status_old = self.Light.variables['status']
            self.status_old2 = self.Light.variables['brightness']
            self.status_old3 = self.Light.variables['color']

        def publish_firebase(self):
            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('devices').child(agent_id).child("device_status").set(self.Light.variables['status'])
                db.child(gateway_id).child('devices').child(agent_id).child("brightness").set(self.Light.variables['brightness'])
                db.child(gateway_id).child('devices').child(agent_id).child("color").set(self.Light.variables['color'])
                print('--------------firebase_update-----------------')
            except Exception as er:
                print er

        def publish_azure_iot_hub(self, activity_type, username):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.Light.variables)
            x = {}
            x["device_id"] = self.Light.variables['agent_id']
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["unixtime"] = int(time.time())
            x["device_status"] = self.Light.variables['status']
            x["color"] = str(self.Light.variables['color'])
            x["brightness"] = self.Light.variables['brightness']
            x["activity_type"] = activity_type
            x["username"] = username
            x["device_name"] = 'MY HUE'
            x["device_type"] = 'lighting'
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))
            print('-----------------Azure_update---------------')

        def StatusPublish(self, commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/agent/zmq/update/hive/999/' + str(self.Light.variables['agent_id']))
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))
            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)
        def publish_postgres(self):

            postgres_url = 'https://peahivemobilebackends.azurewebsites.net/api/v2.0/devices/'
            postgres_Authorization = 'Token '+self.api_token
            m = MultipartEncoder(
                fields={
                    "status": str(self.Light.variables['status']),
                    "device_id": str(self.Light.variables['agent_id']),
                    "device_type": "lighting",
                    "brightness": str(self.Light.variables['brightness']),
                    "color": str(self.Light.variables['color']),
                    "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
                }
            )
            r = requests.put(postgres_url,
                             data=m,
                             headers={'Content-Type': m.content_type,
                                      "Authorization": postgres_Authorization,
                                      })
            print r.status_code

        def gettoken(self):
            conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                    password=db_password)
            self.conn = conn
            self.cur = self.conn.cursor()
            self.cur.execute("""SELECT * FROM token """)
            rows = self.cur.fetchall()
            for row in rows:
                if row[0] == gateway_id:
                    self.api_token =  row[1]
            self.conn.close()

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            message = json.loads(message)

            if 'status' in message:
                self.Light.variables['status'] = str(message['status'])
            if 'color' in message:
                self.Light.variables['color'] = message['color']
            if 'brightness' in message:
                self.Light.variables['brightness'] = message['brightness']
            self.Light.setDeviceStatus(message)
            time.sleep(2)
            self.Light.getDeviceStatus()
            self.publish_firebase()
            self.publish_postgres()

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
