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
def curtain_agent(config_path, **kwargs):
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
    device_status = get_config('device_status')
    device = get_config('device')
    bearer = get_config('bearer')
    url = get_config('url')
    api = get_config('api')
    address = get_config('ipaddress')
    _address = address.replace('http://', '')
    _address = address.replace('https://', '')

    # construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    topic_device_control = '/ui/agent/update/'+_topic_Agent_UI_tail
    print(topic_device_control)
    gateway_id = settings.gateway_id

    class curtain(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(curtain, self).__init__(**kwargs)
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
            self.gettoken()
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Certain = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self._agent_id,
                                         bearer=self.smartthingtoken, device=self.device, url=self.url)

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


        def gettoken(self):

            self.api_token = '701308a85458bab3ec83d9a08e678c545b87ec67'
            self.smartthingtoken = '701308a85458bab3ec83d9a08e678c545b87ec67'
            smartthingtoken = db.child(gateway_id).child('smartthingtoken').get().val()
            self.smartthingtoken = str(smartthingtoken)

        # @Core.periodic(device_monitor_time)
        # def deviceMonitorBehavior(self):

            # self.Certain.getDeviceStatus()
            # self.StatusPublish(self.Certain.variables)
            # #
            # # self.StatusPublish(self.Certain.variables)
            # #
            # #
            # # self.publish_postgres()
            # #
            # # update firebase , posgres , azure
            # if (self.Certain.variables['device_status'] == self.status_old):
            #
            #     pass
            # else:
            #     #self.publish_firebase()
            #     #self.publish_postgres()
            #     self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)
            #
            # self.status_old = self.Certain.variables['device_status']
            #
            # print(self.status_old)




        # @Core.periodic(60)
        # def deviceMonitorBehavior2(self):
        #
        #     self.Certain.getDeviceStatus()
            # update Azure IoT Hub
            # self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)

        def StatusPublish(self, commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/agent/zmq/update/hive/999/' + str(self.Certain.variables['agent_id']))
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def publish_firebase(self):
            try:
                db.child(gateway_id).child('devices').child(agent_id).child("dt").set(
                    datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('devices').child(agent_id).child("DIM").set(
                    self.Certain.variables['device_status'])
                db.child(gateway_id).child('devices').child(agent_id).child("STATUS").set(
                    self.Certain.variables['device_status'])
                db.child(gateway_id).child('devices').child(agent_id).child("TYPE").set(
                    self.Certain.variables['device_type'])
            except Exception as er:
                print er

        def publish_azure_iot_hub(self, activity_type, username):
            # TODO publish to Azure IoT Hub u
            '''
            here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
            hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
            def iothub_client_telemetry_sample_run():
            '''
            print(self.Certain.variables)
            x = {}
            x["device_id"] = self.Certain.variables['agent_id']
            x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
            x["unixtime"] = int(time.time())
            x["device_status"] = self.Certain.variables['device_status']
            x["activity_type"] = activity_type
            x["username"] = username
            x["device_name"] = 'NARAI-Certain'
            x["device_type"] = 'curtain'
            discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))


        def publish_postgres(self):

            postgres_url = 'https://peahivemobilebackends.azurewebsites.net/api/v2.0/devices/'
            postgres_Authorization = 'Token ' + self.api_token

            m = MultipartEncoder(
                fields={
                    "status": str(self.Certain.variables['device_status']),
                    "device_id": str(self.Certain.variables['agent_id']),
                    "device_type": "curtain",
                    "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
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
            topic = str('/agent/zmq/update/hive/999/' + str(self.Certain.variables['agent_id']))
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

            message2 = json.loads(message)
            if 'status' in message2:
                self.Certain.variables['device_status'] = str(message2['status'])

            self.Certain.setDeviceStatus((message))
            self.publish_azure_iot_hub(activity_type='devicecontrol', username=str(message2['username']))

            try:
                if message2['dim'] == '0':
                    self.Certain.variables['device_status'] = "OFF"
                elif message2['dim'] == '100':
                    self.Certain.variables['device_status'] = "ON"
            except:
                pass

            try:
                self.Certain.variables['device_status'] = message2['status']
            except:
                pass

            self.publish_firebase()
            self.publish_postgres()
            self.publish_azure_iot_hub(activity_type='devicemonitor', username=agent_id)


    Agent.__name__ = 'curtain'
    return curtain(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(curtain_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
