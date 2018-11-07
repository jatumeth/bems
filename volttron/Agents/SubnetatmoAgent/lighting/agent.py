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

    agent_id = get_config('agent_id')
    message = get_config('message')
    model = get_config('model')
    api = get_config('api')
    identifiable = get_config('identifiable')
    # construct _topic_Agent_UI based on data obtained from DB
    topic_device_control = '/agent/zmq/update/hive/999/03WSP1234568'
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
            self.count = None
            self.msg_log = None

        def stream_handler(self, message):
            print(message["event"])  # put
            print(message["path"])  # /-K7yGTTEp7O549EzTYtI
            print(message["data"])  # {'title': 'Pyrebase', "body": "etc..."}
            hue = db.child('hivedevhub13').child('devices').child('02HUE1234500').child('device_status').get()
            hue = (hue.pyres)
            print("huestatus = {}".format(hue))

            if hue == "OFF":
                self.track = True
                # self.name = 'unknownpeople'
                # db.child('hivedevhub13').child('people').child('current_detected').set('unknownpeople')
                self.peoplecheck = False
            if hue == "ON":
                # self.name = 'unknown'
                # db.child('hivedevhub13').child('people').child('current_detected').set('unknown')
                self.track = False

            if self.track == True:
                self.name = db.child('hivedevhub13').child('people').child('current_detected').get()
                self.name = (self.name.pyres)
                print("name = {}".format(self.name))
                if self.name != 'unknown':
                    self.onhue()
                    self.acon()
                    self.peoplecheck = True

            number = db.child('hivedevhub13').child('people').child('number').get()
            number = (number.pyres)

            print self.peoplecheck
            print("number = {}".format(number))

            if self.peoplecheck == True:
                if number < 1 and self.reset1 == True:
                    self.offhue()
                    self.acoff()
                    self.reset1 = False
                    self.reset2 = True
                    self.reset3 = True

                elif number < 3 and self.reset2 == True:
                    self.blue2()
                    self.acon()
                    self.reset1 = True
                    self.reset2 = False
                    self.reset3 = True

                elif number > 5 and self.reset3 == True:
                    self.blue3()
                    self.acon()
                    self.reset1 = True
                    self.reset2 = True
                    self.reset3 = False



        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self.flag1 = True
            self.flag2 = True
            self.flag3 = True
            # self.name = db.child('hivedevhub13').child('people').child('current_detected').get()
            # self.namestart = (self.name.pyres)
            self.track = False
            self.peoplecheck = False
            self.reset1 = True
            self.reset2 = True
            self.reset3 = True
            my_stream = db.child("hivedevhub13").child("people").stream(self.stream_handler)

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            # _log.debug("VERSION IS: {}".format(self.core.version()))
            self.count = 0
            self.msg_log = {}
            # self.Publish1()

        # @Core.periodic(5)
        # def deviceMonitorBehavior(self):

            # hue = db.child('hivedevhub13').child('devices').child('02HUE1234500').child('device_status').get()
            # hue = (hue.pyres)
            # print("huestatus = {}".format(hue))
            #
            # if hue == "OFF":
            #     self.track = True
            #     # self.name = 'unknownpeople'
            #     # db.child('hivedevhub13').child('people').child('current_detected').set('unknownpeople')
            #     self.peoplecheck = False
            # if hue == "ON":
            #     # self.name = 'unknown'
            #     # db.child('hivedevhub13').child('people').child('current_detected').set('unknown')
            #     self.track = False
            #
            # if self.track == True:
            #     self.name = db.child('hivedevhub13').child('people').child('current_detected').get()
            #     self.name = (self.name.pyres)
            #     print("name = {}".format(self.name))
            #     if self.name != 'unknown':
            #         self.onhue()
            #         self.acon()
            #         self.peoplecheck = True
            #
            # number = db.child('hivedevhub13').child('people').child('number').get()
            # number = (number.pyres)
            #
            # print self.peoplecheck
            # print("number = {}".format(number))
            #
            # if self.peoplecheck == True:
            #     if number < 1 and self.reset1 == True :
            #         self.offhue()
            #         self.acoff()
            #         self.reset1 = False
            #         self.reset2 = True
            #         self.reset3 = True
            #
            #     elif number < 3 and self.reset2 == True :
            #         self.blue2()
            #         self.acon()
            #         self.reset1 = True
            #         self.reset2 = False
            #         self.reset3 = True
            #
            #     elif number > 5 and self.reset3 == True :
            #         self.blue3()
            #         self.acon()
            #         self.reset1 = True
            #         self.reset2 = True
            #         self.reset3 = False




            # if self.name == 'pear':
            #     self.flag2 = True
            #     self.flag3 = True
            #     if self.flag1 == True:
            #         self.ac25()
            #         self.violethue()
            #         print "pear"
            #         self.flag1 = False
            #
            # elif self.name == 'momo':
            #     self.flag1 = True
            #     self.flag3 = True
            #     if self.flag2 == True:
            #         self.ac23()
            #         self.pinkhue()
            #         print "momo"
            #         self.flag2 = False
            # elif self.name == 'guide':
            #     self.flag1 = True
            #     self.flag2 = True
            #     if self.flag3 == True:
            #         self.ac23()
            #         self.redhue()
            #         print "momo"
            #         self.flag3 = False
            #
            # else :
            #     self.flag1 = True
            #     self.flag2 = True
            #     self.flag3 = True


        def blue1(self):
            # TODO this is example how to write an app to control AC
            commsg = {"STATUS": "ON", "color": u'(224,255,255)'}

            topic = str('/ui/agent/update/hive/999/02HUE1234500')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def onhue(self):
            # TODO this is example how to write an app to control AC
            commsg = {"STATUS": "ON", "color": u'(255, 255, 255)'}

            topic = str('/ui/agent/update/hive/999/02HUE1234500')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def offhue(self):
            # TODO this is example how to write an app to control AC
            commsg = {"STATUS": "OFF", "color": u'(255, 255, 255)'}

            topic = str('/ui/agent/update/hive/999/02HUE1234500')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def blue2(self):
            # TODO this is example how to write an app to control AC
            commsg = {"STATUS": "ON", "color": u'(0, 153, 255)'}

            topic = str('/ui/agent/update/hive/999/02HUE1234500')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def blue3(self):
            # TODO this is example how to write an app to control AC
            commsg = {"STATUS": "ON", "color": u'(0, 0, 255)'}

            topic = str('/ui/agent/update/hive/999/02HUE1234500')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def ac25(self):
            # TODO this is example how to write an app to control AC
            commsg = {"stemp": "25", "device": "01DAI1200110", "username": "pean1", "type": "devicecontrol"}

            topic = str('/ui/agent/update/hive/999/01DAI1200110')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def ac23(self):
            # TODO this is example how to write an app to control AC
            commsg = {"stemp": "23", "device": "01DAI1200110", "username": "pean1", "type": "devicecontrol"}

            topic = str('/ui/agent/update/hive/999/01DAI1200110')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def acoff(self):
            # TODO this is example how to write an app to control AC
            commsg = {"status": "OFF", "device": "01DAI1200110", "username": "pean1", "type": "devicecontrol"}

            topic = str('/ui/agent/update/hive/999/01DAI1200110')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

        def acon(self):
            # TODO this is example how to write an app to control AC
            commsg = {"status": "OFF", "device": "01DAI1200110", "username": "pean1", "type": "devicecontrol"}

            topic = str('/ui/agent/update/hive/999/01DAI1200110')
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'pub device status to ZMQ'}, message)

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