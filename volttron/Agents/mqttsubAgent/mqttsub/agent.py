# -*- coding: utf-8 -*-
from __future__ import absolute_import
from datetime import datetime
import logging
import sys
import settings
from pprint import pformat
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import importlib
import random
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

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'HELLO'

# Step1: Agent Initialization
def mqttsub_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    service_namespace = settings.AZURE['servicebus']['service_namespace']
    shared_access_key_name = settings.AZURE['servicebus']['shared_access_key_name']
    shared_access_key_value = settings.AZURE['servicebus']['shared_access_key_value']
    servicebus_topic = settings.AZURE['servicebus']['topic']
    sbs = ServiceBusService(
        service_namespace=service_namespace,
        shared_access_key_name=shared_access_key_name,
        shared_access_key_value=shared_access_key_value)

    class mqttsubAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(mqttsubAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self._agent_id = self.config.get('agentid')

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))

            while True:
                try:
                    msg = sbs.receive_subscription_message(servicebus_topic, 'client1', peek_lock=False)
                    if msg.body is not None:
                        commsg = eval(msg.body)
                        print("message MQTT received datas")
                        type_msg = commsg.get('type', None)
                        if type_msg.startswith('scene'): # TODO : Recheck condition again
                            print('Found scene')
                            self.VIPPublishApplication(commsg, type_msg)

                        elif type_msg == 'devicecontrol':
                            # Execute Device Control Function
                            print("Device Cintrol Event")
                            self.VIPPublishDevice(commsg)

                        elif type_msg == 'login':
                            # Execute Token Stored Function
                            print("Renew Token Event")
                            self.VIPPublishApplication(commsg, type_msg)
                            # TODO : Pub message again to Notifier agent to Store TOKEN VALUE
                            self.vip.pubsub.publish('pubsub',
                                                    {'Type': 'Mobile Update to Gateway'},
                                                    topic='/ui/agent/update/notifier',
                                                    message=json.dumps(commsg),
                                                    )

                        elif type_msg == 'automationcreate':
                            # Execute Create Automation Function
                            print("Create Automation Event")
                            self.VIPPublishApplication(commsg, type_msg)

                        elif type_msg == 'automationdelete':
                            # Execute Delete Automation Function
                            print("Delete Automation Event")
                            self.VIPPublishApplication(commsg, type_msg)

                        elif type_msg == 'automationupdate':
                            # Execute Update Automation Function
                            print("Update Automation Event")
                            self.VIPPublishApplication(commsg, type_msg)

                        else:
                            print "---------------------------------------"
                            print('Any Topic :')
                            print servicebus_topic
                            print commsg
                            print "---------------------------------------"
                    else :
                        print servicebus_topic
                        print "No body message"

                except Exception as er:
                    print er

        def VIPPublishDevice(self,commsg):
            # TODO this is example how to write an app to control AC
            topic = str('/ui/agent/update/hive/999/' + str(commsg['device']))
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'HiVE Device to Gateway'}, message)

        def VIPPublishApplication(self, commsg, type_msg):
            topic = str('/ui/agent/update/hive/999/') + str(type_msg)
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'HiVE Application to Gateway'}, message)

    Agent.__name__ = 'mqttsubAgent'
    return mqttsubAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(mqttsub_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
