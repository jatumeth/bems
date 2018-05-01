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

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Listener Message'
DEFAULT_AGENTID = "listener"
DEFAULT_HEARTBEAT_PERIOD = 5
DEFAULT_MONITORING_TIME = 5
oat_point = 'devices/Building/LAB/Device/OutsideAirTemperature'
all_topic = 'devices/Building/LAB/Device/all'
test = 'test/1'
test2 = 'test/2'


from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
# from zmqhelper.ZMQHelper.zmq_pub import ZMQ_PUB
import requests
import json
import time
import logging
import os
from volttron.platform.agent import utils, matching
from uuid import getnode as get_mac
import fcntl, socket, struct
import settings

class mqttsubAgent(Agent):
    """Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    """

    def __init__(self, config_path, **kwargs):
        super(mqttsubAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

        # TODO get database parameters from settings.py, add db_table for specific table

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        # Demonstrate accessing a value from the config file
        _log.info(self.config.get('message', DEFAULT_MESSAGE))
        self._agent_id = self.config.get('agentid')

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        _log.debug("VERSION IS: {}".format(self.core.version()))


        print "start"
        sbs = ServiceBusService(
            service_namespace='peahiveservicebus',
            shared_access_key_name='RootManageSharedAccessKey',
            shared_access_key_value='vOjEoWzURJCJ0bAgRTo69o4BmLy8GAje4CfdXkDiwzQ=')
        topic = settings.gateway_id

        while True:
            try:
                msg = sbs.receive_subscription_message(topic, 'client1', peek_lock=False)
                commsg = eval(msg.body)
                print commsg
                print("message MQTT received")
                for k, v in commsg.items():
                    if k == 'device':
                        print ""
                        self.VIPPublish(commsg)

                    elif k == 'scene':
                        Scene(commsg)
                        print "Scene Agent"
                    else:
                        print ""
            except Exception as er:
                print er

    def VIPPublish(self,commsg):
        # TODO this is example how to write an app to control AC
        topic = str('/ui/agent/update/hive/999/' + str(commsg['device']))
        message = json.dumps(commsg)
        print ("topic {}".format(topic))
        print ("message {}".format(message))

        self.vip.pubsub.publish(
            'pubsub', topic,
            {'Type': 'HiVE App to Gateway'},message)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(mqttsubAgent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
