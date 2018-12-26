# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import sys
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.agent import utils
import importlib
import json
import datetime
import settings
import pyrebase
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

    agent_id = get_config('agent_id')
    message = get_config('message')
    model = get_config('model')
    api = get_config('api')
    identifiable = get_config('identifiable')
    # construct _topic_Agent_UI based on data obtained from DB
    topic_device_control = '/agent/zmq/update/hive/999/03WSP060BFEA'
    send_notification = True


    class LightingAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(LightingAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self.model = model
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Light = self.apiLib.API(model=self.model, agent_id=self._agent_id)
            self.count = None
            self.msg_log = None

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.starttrade = False
            self.wh_new = 0
            self.wh_old = 0
            self.now_plus_5 = '2018-12-26 10:14:02.684188'
            self.wh = 0


        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            # _log.debug("VERSION IS: {}".format(self.core.version()))
            self.count = 0
            self.msg_log = {}
            self.starttrade = False
            self.wh_new = 0
            self.wh_old = 0
            self.now_plus_5 = '2018-12-26 10:14:02.684188'
            self.wh = 0

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            msg =json.loads(message)
            status = msg['status']
            print("Trading status = {}".format(status))
            now = datetime.datetime.now()

            if self.starttrade == False and status == 'ON':
                self.starttrade = True
                self.now_plus_5 = now + datetime.timedelta(minutes=5)
                print "start trade"
                print("Next cal blockchain = {}".format(self.now_plus_5))
                self.readmeterold()

            if self.starttrade == True and status == 'ON':
                now = datetime.datetime.now()
                print("time now            = {}".format(now ))
                print("Next cal blockchain = {}".format(self.now_plus_5))

                if now > self.now_plus_5:
                    self.starttrade = False
                    print "complete block"
                    self.readmeternew()
                    cal = (self.wh_new - self.wh_old)/1000
                    self.wh = round(cal, 4)
                    print("Watt hour = {}".format(self.wh))
                    self.block()

            if status == 'OFF':
                self.starttrade = False

        def readmeterold(self):
            number = db.child('hivec83a35cdbeab').child('devices').child('05CRE270121594').child('AccumulatedEnergy(Wh)').get()
            number = (number.pyres)
            self.wh_old = float(number)

        def readmeternew(self):

            number = db.child('hivec83a35cdbeab').child('devices').child('05CRE270121594').child('AccumulatedEnergy(Wh)').get()
            number = (number.pyres)
            self.wh_new = (float(number))

        def block(self):


            response = requests.post(
                url="http://pea-ledger.southeastasia.cloudapp.azure.com:3000/api/EnergyToCoins",
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                },
                data=json.dumps({
                    "$class": "org.decentralized.energy.network.EnergyToCoins",
                    "energyInc": "resource:org.decentralized.energy.network.Energy#0011",
                    "energyRate": str(self.wh),
                    "coinsInc": "resource:org.decentralized.energy.network.Coins#0010",
                    "energyValue": "1",
                    "coinsDec": "resource:org.decentralized.energy.network.Coins#0011",
                    "energyDec": "resource:org.decentralized.energy.network.Energy#0010"
                })
            )
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                content=response.content))

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
