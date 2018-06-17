# -*- coding: utf-8 -*-


from datetime import datetime
import logging
import sys
import os
import subprocess as sp
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
import settings


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'

try:
    config = {
      "apiKey": "AIzaSyD4QZ7ko7uXpNK-VBF3Qthhm3Ypzi_bxgQ",
      "authDomain": "hive-rt-mobile-backend.fi+rebaseapp.com",
      "databaseURL": "https://hive-rt-mobile-backend.firebaseio.com",
      "storageBucket": "bucket.appspot.com",
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
    if model == "Philips hue bridge":
        hue_username = get_config('username')
    else:
        hue_username = ''
    device_type = get_config('type')
    # device = get_config('device')
    # bearer = get_config('bearer')
    # url = get_config('url')
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

    # DATABASES
    # print settings.DEBUG
    # db_host = settings.DATABASES['default']['HOST']
    # db_port = settings.DATABASES['default']['PORT']
    # db_database = settings.DATABASES['default']['NAME']
    # db_user = settings.DATABASES['default']['USER']
    # db_password = settings.DATABASES['default']['PASSWORD']
    # db_table_ac = settings.DATABASES['default']['TABLE_ac']
    # db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
    # db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
    # db_table_alerts_notificationchanneladdress = settings.DATABASES['default']['TABLE_alerts_notificationchanneladdress']
    # db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
    # db_table_priority = settings.DATABASES['default']['TABLE_priority']

    # construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    topic_device_control = '/ui/agent/update/'+_topic_Agent_UI_tail
    print(topic_device_control)
    gateway_id = 'hivecdf12345'

    # 5. @params notification_info
    send_notification = True
    # email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
    # email_username = settings.NOTIFICATION['email']['username']
    # email_password = settings.NOTIFICATION['email']['password']
    # email_mailServer = settings.NOTIFICATION['email']['mailServer']
    # notify_heartbeat = settings.NOTIFICATION['heartbeat']

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
            # self.url = url
            # self.device = device
            # self.bearer = bearer
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.AC = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self._agent_id
                                )

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
            # self.iotmodul = importlib.import_module("hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))
            #os.system("python '/home/pea/workspace/hive_os/volttron/hive_lib/broadlink-http-rest/server.py';")
            sp.Popen('python /home/pea/workspace/hive_os/volttron/hive_lib/broadlink-http-rest/server.py', shell=True)
        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):

            self.AC.getDeviceStatus()

            self.StatusPublish(self.AC.variables)

            # TODO update local postgres
            # self.publish_postgres()

            # update firebase
            self.publish_firebase()

            # self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)

        # @Core.periodic(60)
        # def deviceMonitorBehavior2(self):
        #
        #     self.AC.getDeviceStatus()
        #     self.publish_azure_iot_hub()

        def publish_firebase(self):

            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('devices').child(agent_id).child("STATUS").set(self.AC.variables['status'])
                db.child(gateway_id).child('devices').child(agent_id).child("TEMPERATURE").set(self.AC.variables['current_temperature'])
                db.child(gateway_id).child('devices').child(agent_id).child("SET_TEMPERATURE").set(self.AC.variables['set_temperature'])
                db.child(gateway_id).child('devices').child(agent_id).child("SET_HUMIDITY").set(self.AC.variables['set_humidity'])
                db.child(gateway_id).child('devices').child(agent_id).child("MODE").set(self.AC.variables['mode'])
            except Exception as er:
                print er

        def publish_postgres(self):

            postgres_url = settings.POSTGRES['postgres']['url']
            postgres_Authorization = settings.POSTGRES['postgres']['Authorization']


            m = MultipartEncoder(
                fields={
                    "status": str(self.AC.variables['status']),
                    "device_id": str(self.AC.variables['agent_id']),
                    "device_type": "airconditioner",
                    "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
                    # "current_temperature": str(self.AC.variables['current_temperature']),
                    # "set_temperature": str(self.AC.variables['set_temperature']),
                    # "mode": str(self.AC.variables['mode']),
                }
            )

            r = requests.put(postgres_url,
                             data=m,
                             headers={'Content-Type': m.content_type,
                                      "Authorization": postgres_Authorization,
                                      })
            print r.status_code

        def StatusPublish(self, commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/agent/zmq/update/hive/999/' + str(self.AC.variables['agent_id']))
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)


        def publish_azure_iot_hub(self, activity_type, username):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            x = {}
            x["device_id"] = str(self.AC.variables['agent_id'])
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["device_status"] = str(self.AC.variables['status'])
            x["unixtime"] = int(time.time())
            x["current_temperature"] = str(self.AC.variables['current_temperature'])
            x["set_temperature"] = str(self.AC.variables['set_temperature'])
            x["set_humidity"] = str(self.AC.variables['set_humidity'])
            x["mode"] = str(self.AC.variables['mode'])
            x["activity_type"] = activity_type
            x["username"] = username
            x["device_name"] = 'MY DAIKIN'
            x["device_type"] = 'airconditioner'
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))

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
            self.publish_azure_iot_hub(activity_type='devicecontrol', username=str(message['username']))


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
