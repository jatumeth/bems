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
import urllib3
urllib3.disable_warnings()

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'

try:
    config = {
      "apiKey": "AIzaSyD4QZ7ko7uXpNK-VBF3Qthhm3Ypzi_bxgQ",
      "authDomain": "hive-rt-mobile-backend.firebaseapp.com",
      "databaseURL": "https://hive-rt-mobile-backend.firebaseio.com",
      "storageBucket": "bucket.appspot.com",
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except Exception as er:
    print er

# Step1: Agent Initialization
def Powermetering_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # List of all keywords for a Powermetering agent
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
    device_type = get_config('device_type')
    print device_type

    device = get_config('device')
    # bearer = get_config('bearer')
    url = get_config('url')
    api = get_config('api')
    address = get_config('ipaddress')
    device_id = get_config('device_id')

    # try:  # validate whether or not address is an ip address
    #     socket.inet_aton(_address)
    #     ip_address = _address
    # except socket.error:
    #     ip_address = None
    identifiable = get_config('identifiable')

    # DATABASES
    # print settings.DEBUG
    # db_host = settings.DATABASES['default']['HOST']
    # db_port = settings.DATABASES['default']['PORT']
    # db_database = settings.DATABASES['default']['NAME']
    # db_user = settings.DATABASES['default']['USER']
    # db_password = settings.DATABASES['default']['PASSWORD']
    # db_table_Powermetering = settings.DATABASES['default']['TABLE_Powermetering']
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

    class PowermeteringAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(PowermeteringAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.model = model
            self.device_type = device_type
            self.url = url
            # self.device = device
            self.device_id = device_id
            # self.bearer = bearer
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Powermeter = self.apiLib.API(model=self.model, type=self.device_type, agent_id=self._agent_id,url=self.url ,device_id=self.device_id)

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

            self.Powermeter.getDeviceStatus()

            self.StatusPublish(self.Powermeter.variables)
            # TODO update local postgres
            # self.publish_local_postgres()

            # update firebase
            self.publish_firebase()

            # update Azure IoT Hub
            # self.publish_azure_iot_hub()

        def publish_firebase(self):
            try:
                db.child(gateway_id).child(agent_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                # db.child(gateway_id).child(agent_id).child("device_status").set(self.Powermeter.variables['device_status'])
                db.child(gateway_id).child(agent_id).child("TransID(ID)").set(self.Powermeter.variables['grid_transid'])
                db.child(gateway_id).child(agent_id).child("Date(D)").set(self.Powermeter.variables['grid_date'])
                db.child(gateway_id).child(agent_id).child("Time(T)").set(self.Powermeter.variables['grid_time'])
                db.child(gateway_id).child(agent_id).child("UxTime(UT)").set(self.Powermeter.variables['grid_uxtime'])
                db.child(gateway_id).child(agent_id).child("DeviceID(DID)").set(self.Powermeter.variables['grid_device_id'])
                db.child(gateway_id).child(agent_id).child("Voltage(V)").set(self.Powermeter.variables['grid_voltage'])
                db.child(gateway_id).child(agent_id).child("Current(A)").set(self.Powermeter.variables['grid_current'])
                db.child(gateway_id).child(agent_id).child("EarthLeak(EL)").set(self.Powermeter.variables['grid_earth_leak'])
                db.child(gateway_id).child(agent_id).child("ActivePower(W)").set(self.Powermeter.variables['grid_activePower'])
                db.child(gateway_id).child(agent_id).child("ReactivePower(Var)").set(self.Powermeter.variables['grid_reactivePower'])
                db.child(gateway_id).child(agent_id).child("Powerfactor").set(self.Powermeter.variables['grid_powerfactor'])
                db.child(gateway_id).child(agent_id).child("AccumulatedEnergy(Wh)").set(self.Powermeter.variables['grid_accumulated_energy'])
                db.child(gateway_id).child(agent_id).child("Kvarh").set(self.Powermeter.variables['grid_kvarh'])
                db.child(gateway_id).child(agent_id).child("Show").set(self.Powermeter.variables['grid_cp_afci_arc_count_show'])
                db.child(gateway_id).child(agent_id).child("A0magOut").set(self.Powermeter.variables['grid_cp_a0_magoutput'])
                db.child(gateway_id).child(agent_id).child("A0rmsOut").set(self.Powermeter.variables['grid_cp_a0_rmsoutput'])
                db.child(gateway_id).child(agent_id).child("IrmsRate").set(self.Powermeter.variables['grid_cp_Irms_rate'])
                db.child(gateway_id).child(agent_id).child("DcRate").set(self.Powermeter.variables['grid_cp_dc_rate'])
                db.child(gateway_id).child(agent_id).child("B1RmsOut").set(self.Powermeter.variables['grid_cp_b1_rmsoutput'])
                db.child(gateway_id).child(agent_id).child("Afeia").set(self.Powermeter.variables['grid_afe_i_a'])
                db.child(gateway_id).child(agent_id).child("Afev").set(self.Powermeter.variables['grid_afe_v'])
                db.child(gateway_id).child(agent_id).child("PfcHigh").set(self.Powermeter.variables['grid_cp_pfci_t_high'])
                db.child(gateway_id).child(agent_id).child("OperationStatus").set(self.Powermeter.variables['grid_cp_operation_status'])
                db.child(gateway_id).child(agent_id).child("device_type").set(self.Powermeter.variables['device_type'])
            except Exception as er:
                print er

        def publish_azure_iot_hub(self):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.Powermeter.variables)
            x = {}
            x["agent_id"] = self.Powermeter.variables['agent_id']
            x["dt"] = datetime.now().replace(microsecond=0).isoformat()
            x["device_status"] = self.Powermeter.variables['device_status']
            x["device_type"] = self.Powermeter.variables['device_type']
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))
        
        def StatusPublish(self,commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/agent/zmq/update/hive/999/' + str(self.Powermeter.variables['agent_id']))
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
            self.Powermeter.setDeviceStatus(json.loads(message))

    Agent.__name__ = 'PowermeteringAgent'
    return PowermeteringAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(Powermetering_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
