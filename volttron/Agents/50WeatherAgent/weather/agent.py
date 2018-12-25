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
import requests
import settings
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
def weathering_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # List of all keywords for a weathering agent
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
    username = get_config('username')
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

    class weatheringAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(weatheringAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.model = model
            # self.device_type = device_type
            self.url = url
            # self.device = device
            self.username = username
            # self.bearer = bearer
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.weather = self.apiLib.API(model=self.model, agent_id=self._agent_id, url=self.url,username=self.username)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))

            # setup connection with db -> Connect to local postgres
            # try:
            #     self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
            #                                 password=db_password)
            #     self.cur = self.con.cursor()  # open a cursor to perfomm database operations
            #     _log.debug("{} connected to the db name {}".format(agent_id, db_database))
            # except:
            #     _log.error("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))
            # connect to Azure IoT hub
            self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))

        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):

            self.weather.getDeviceStatus()

            # TODO update local postgres
            # self.publish_local_postgres()

            # update firebase
            self.publish_firebase()

            # update Azure IoT Hub
            self.publish_azure_iot_hub()
            print('success')


        def publish_firebase(self):
            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                # db.child(gateway_id).child('devices').child(agent_id).child("device_status").set(self.weather.variables['device_status'])
                db.child(gateway_id).child('devices').child(agent_id).child("wind_speed").set(self.weather.variables['wind_speed'])
                db.child(gateway_id).child('devices').child(agent_id).child("temperature").set(self.weather.variables['temp_c'])
                db.child(gateway_id).child('devices').child(agent_id).child("city").set(self.weather.variables['city'])
                db.child(gateway_id).child('devices').child(agent_id).child("country").set(self.weather.variables['country'])
                db.child(gateway_id).child('devices').child(agent_id).child("location").set(self.weather.variables['location'])
                db.child(gateway_id).child('devices').child(agent_id).child("humidity").set(self.weather.variables['humidity'])
                db.child(gateway_id).child('devices').child(agent_id).child("icon").set(self.weather.variables['icon'])

                print self.weather.variables['humidity']
                print self.weather.variables['temp_c']
                print gateway_id
                humid = self.weather.variables['humidity'].replace('%','')

                db.child(gateway_id).child('global').child("humidity").set(humid)
                db.child(gateway_id).child('global').child("outdoor_temperature").set(self.weather.variables['temp_c'])

                print self.weather.variables['temp_c']
                print humid
            except Exception as er:
                   print er

        def publish_azure_iot_hub(self):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.weather.variables)
            x = {}
            x["device_id"] = self.weather.variables['agent_id']
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["unixtime"] = int(time.time())
            x["country"] = self.weather.variables['country']
            x["city"] = self.weather.variables['city']
            x["location"] = self.weather.variables['location']
            x["temperature"] = self.weather.variables['temp_c']
            x["humidity"] = self.weather.variables['humidity']
            x["windspeed"] = self.weather.variables['wind_speed']
            x["weather_detail"] = self.weather.variables['weather']
            x["observation_time"] = self.weather.variables['observ_time']
            x["activity_type"] = 'devicemonitor'
            x["username"] = 'arm'
            x["device_name"] = 'Weatherwunderground'
            x["device_type"] = 'weatherwunderground'
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))


        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            self.weather.setDeviceStatus(json.loads(message))

    Agent.__name__ = 'weatheringAgent'
    return weatheringAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(weathering_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
