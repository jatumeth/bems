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
import datetime as dt
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import psycopg2
import psycopg2.extras


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

except Exception as e :
    print(e)


# Step1: Agent Initialization
def netwelcome_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    gateway_id = settings.gateway_id

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')

    class WelcomeAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(WelcomeAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self.iotmodule = None
            self.client_id = self.config.get("client_id")
            self.client_secret = self.config.get("client_secret")
            self.username = self.config.get("username")
            self.password = self.config.get("password")
            self.grant_type = self.config.get("grant_type")
            self.scope = self.config.get("scope")
            self.access_token = None
            # initialize device object

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.iotmodule = importlib.import_module(
                "hive_lib.azure-iot-sdk-python.device.samples.iothub_client_sample")

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))
            response =self.gettoken()
            self.access_token = response.get('access_token')
            print("Access Token : " + self.access_token)

        @Core.periodic(900)
        def getoccupy(self):
            print("Who at Home ?")
            response = self.gettoken()
            self.access_token = response.get('access_token')
            try:
                response = requests.get(
                    url="https://api.netatmo.net/api/gethomedata",
                    params={
                        "access_token": self.access_token,
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    },
                    data={
                    },
                )
                print('Response HTTP Status Code: {status_code}'.format(
                    status_code=response.status_code))
                temp = json.loads(response.content)
                persons = ((temp.get('body')).get('homes')[0]).get('persons')
                persons_list = []
                for ind in range(len(persons)):
                    if persons[ind].has_key('pseudo'):
                        persons_list.append(persons[ind])
                        if not persons[ind].get('out_of_sight') :
                            print((persons[ind].get('pseudo')).encode('utf-8', 'unicode') + " at home")

                print("debug")
                self.publish_firebase(persons_list)

            except requests.exceptions.RequestException:
                print('HTTP Request failed')

        def publish_firebase(self, occupies):
            moment = dt.datetime.now()
            try:
                db.child(gateway_id).child('occupies').remove()

                for person in occupies:
                    if not person.get('out_of_sight'):
                        x = dt.datetime.fromtimestamp(person.get('last_seen'))
                        time_diff = (moment-x).total_seconds()
                        if time_diff < 3600:
                            db.child(gateway_id).child('occupies').child(person.get('pseudo')).child('last_seen').set(
                                person.get('last_seen'))
                            db.child(gateway_id).child('occupies').child(person.get('pseudo')).child('image').set(
                                str(person.get('face').get('url')))

            except Exception as er:
                print er

        # def publish_azure_iot_hub(self, activity_type, username):
        #     # TODO publish to Azure IoT Hub u
        #     '''
        #     here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
        #     hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
        #     def iothub_client_telemetry_sample_run():
        #     '''
        #     print(self.Light.variables)
        #     x = {}
        #     x["device_id"] = self.Light.variables['agent_id']
        #     x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
        #     x["unixtime"] = int(time.time())
        #     x["device_status"] = self.Light.variables['device_status']
        #     x["activity_type"] = activity_type
        #     x["username"] = username
        #     x["device_name"] = 'In-wall'
        #     x["device_type"] = "lighting"
        #     print x
        #     discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))
        #     print('--------------update azure--------------')

        # def publish_postgres(self):
        #
        #     postgres_url = 'https://peahivemobilebackends.azurewebsites.net/api/v2.0/devices/'
        #     postgres_Authorization = 'Token '+self.api_token
        #
        #     m = MultipartEncoder(
        #         fields={
        #             "status": str(self.Light.variables['device_status']),
        #             "device_id": str(self.Light.variables['agent_id']),
        #             "device_type": "lighting",
        #             "last_scanned_time": datetime.now().replace(microsecond=0).isoformat(),
        #         }
        #     )
        #
        #     r = requests.put(postgres_url,
        #                      data=m,
        #                      headers={'Content-Type': m.content_type,
        #                               "Authorization": postgres_Authorization,
        #                               })
        #     print r.status_code
        #     print('-------------------update postgres---------------')

        def gettoken(self):
            try:
                response = requests.post(
                    url="https://api.netatmo.com/oauth2/token",
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                    },
                    data={
                        "client_id": self.client_id,
                        "username": self.username,
                        "password": self.password,
                        "scope": self.scope,
                        "client_secret": self.client_secret,
                        "grant_type": self.grant_type,
                    },
                )
                print('Response HTTP Status Code: {status_code}'.format(
                    status_code=response.status_code))
                return json.loads(response.content)

            except requests.exceptions.RequestException:
                print('HTTP Request failed')

    Agent.__name__ = 'NetWelComeAgent'
    return WelcomeAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(netwelcome_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
