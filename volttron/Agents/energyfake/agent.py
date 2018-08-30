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

db_host = settings.DATABASES['default']['HOST']
db_port = settings.DATABASES['default']['PORT']
db_database = settings.DATABASES['default']['NAME']
db_user = settings.DATABASES['default']['USER']
db_password = settings.DATABASES['default']['PASSWORD']

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
def ac_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_monitor_time = config.get('device_monitor_time', DEFAULT_MONITORING_TIME)
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    device_type = get_config('type')
    api = get_config('api')
    address = get_config('ipaddress')
    _address = address.replace('http://', '')
    _address = address.replace('https://', '')
    identifiable = get_config('identifiable')

    # construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    topic_device_control = '/ui/agent/update/'+_topic_Agent_UI_tail
    print(topic_device_control)

    gateway_id = settings.gateway_id

    class DaikinAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(DaikinAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.model = model
            self.device_type = device_type
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.AC = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self._agent_id)

            self.an1 = 100.1
            self.an2 = 4
            self.an3 = 30.3
            self.an4 = 34
            self.an5 = 55.6
            self.an6 = 34.3

            self.day1 = 100.1
            self.day2 = 4
            self.day3 = 30.3
            self.day4 = 34
            self.day5 = 55.6
            self.day6 = 34.3
            self.day7 = 34.3
            self.day8 = 34.3
            self.day9 = 34.3
            self.day10 = 34.3
            self.day11 = 34.3

            self.mon1 = 100.1
            self.mon2 = 4
            self.mon3 = 30.3
            self.mon4 = 34
            self.mon5 = 55.6
            self.mon6 = 34.3






        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))

        @Core.periodic(3)
        def deviceMonitorBehavior(self):

            import random
            x = random.random()
            y = round(x, 3)
            print y

            self.an1 = round((self.an1 + y), 3)
            self.an2 = round((self.an2 + y), 3)
            self.an3 = round((self.an3 + y), 3)
            self.an4 = round((self.an4 + y), 3)
            self.an5 = round((self.an5 + y), 3)
            self.an6 = round((self.an6 + y), 3)


            self.day1 = round((self.day1 + y), 3)
            self.day2 = round((self.day2 + y), 3)
            self.day3 = round((self.day3 + y), 3)
            self.day4 = round((self.day4 + y), 3)
            self.day5 = round((self.day5 + y), 3)
            self.day6 = round((self.day6 + y), 3)
            self.day7 = round((self.day7 + y), 3)
            self.day8 = round((self.day8 + y), 3)
            self.day9 = round((self.day9 + y), 3)
            self.day10 = round((self.day10 + y), 3)


            self.mon1 = round((self.mon1 + y), 3)
            self.mon2 = round((self.mon2 + y), 3)
            self.mon3 = round((self.mon3 + y), 3)
            self.mon4 = round((self.mon4 + y), 3)
            self.mon5 = round((self.mon5 + y), 3)
            self.mon6 = round((self.mon6 + y), 3)

            db.child('hivedevhub7').child('energy').child("annual_energy").child("gridimportbill").set(self.an2*3)
            db.child('hivedevhub7').child('energy').child("annual_energy").child("gridimportenergy").set(self.an2)


            db.child('hivedevhub7').child('energy').child("annual_energy").child("loadbill").set((self.an6+self.an2)*3)
            db.child('hivedevhub7').child('energy').child("annual_energy").child("loadenergy").set(self.an6+self.an2)


            db.child('hivedevhub7').child('energy').child("annual_energy").child("solarbill").set(self.an6*3)
            db.child('hivedevhub7').child('energy').child("annual_energy").child("solarenergy").set(self.an6)


            db.child('hivedevhub7').child('energy').child("daily_energy").child("grid_avg_power").set(self.day1)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("gridimportbill").set(self.day3*3)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("gridimportenergy").set(self.day3)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("load_avg_power").set(self.day4)

            db.child('hivedevhub7').child('energy').child("daily_energy").child("solar_avg_power").set(self.day6)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("load_avg_power").set(self.day7)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("solarbill").set(self.day9*3)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("solarenergy").set(self.day9)


            load= self.day3+ self.day9
            db.child('hivedevhub7').child('energy').child("daily_energy").child("loadbill").set(load * 3)
            db.child('hivedevhub7').child('energy').child("daily_energy").child("loadenergy").set(load)


            loadm = self.mon2+ self.mon6
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("gridimportbill").set(self.mon2*3)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("gridimportenergy").set(self.mon2)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("loadbill").set(loadm*3)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("loadenergy").set(loadm)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("solarbill").set(self.mon6*3)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("solarenergy").set(self.mon6)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("grid_avg_power").set(self.mon6)
            db.child('hivedevhub7').child('energy').child("monthly_energy").child("load_avg_power").set(self.mon6)


            g = round((1000+(y*1000)), 3)
            s = round((2000 + (y * 1000)), 3)

            l = g+ s

            db.child('hiveC83A35CDBEAB').child('1PV221445K1200100').child("grid_activePower").set(g)
            db.child('hiveC83A35CDBEAB').child('1PV221445K1200100').child("inverter_activePower").set(s)
            db.child('hiveC83A35CDBEAB').child('1PV221445K1200100').child("load_activePower").set(l)

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            message = json.loads(message)
            if 'status' in message:
                self.AC.variables['status'] = str(message['status'])
            if 'set_temperature' in message:
                self.AC.variables['set_temperature'] = str(message['set_temperature'])
            if 'set_humidity' in message:
                self.AC.variables['set_humidity'] = str(message['set_humidity'])
            if 'mode' in message:
                self.AC.variables['mode'] = str(message['mode'])
            self.AC.setDeviceStatus(message)

            time.sleep(2)
            self.AC.getDeviceStatus()
            if(self.AC.variables['status'] != self.status_old or
                    self.AC.variables['current_temperature'] != self.status_old2 or
                    self.AC.variables['set_temperature'] != self.status_old3 or
                    self.AC.variables['set_humidity'] != self.status_old4 or
                    self.AC.variables['mode'] != self.status_old5):
                self.publish_firebase()
                self.publish_postgres()
            else:
                time.sleep(1)
                self.AC.getDeviceStatus()
                if (self.AC.variables['status'] != self.status_old or
                        self.AC.variables['current_temperature'] != self.status_old2 or
                        self.AC.variables['set_temperature'] != self.status_old3 or
                        self.AC.variables['set_humidity'] != self.status_old4 or
                        self.AC.variables['mode'] != self.status_old5):
                    self.publish_firebase()
                    self.publish_postgres()
                else:
                    time.sleep(1)
                    self.AC.getDeviceStatus()
                    if (self.AC.variables['status'] != self.status_old or
                            self.AC.variables['current_temperature'] != self.status_old2 or
                            self.AC.variables['set_temperature'] != self.status_old3 or
                            self.AC.variables['set_humidity'] != self.status_old4 or
                            self.AC.variables['mode'] != self.status_old5):
                        self.publish_firebase()
                        self.publish_postgres()
                    else:
                        pass
            self.status_old = self.AC.variables['status']
            self.status_old2 = self.AC.variables['current_temperature']
            self.status_old3 = self.AC.variables['set_temperature']
            self.status_old4 = self.AC.variables['set_humidity']


    Agent.__name__ = '01DAI_ACAgent'
    return DaikinAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(ac_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script

    sys.exit(main())
