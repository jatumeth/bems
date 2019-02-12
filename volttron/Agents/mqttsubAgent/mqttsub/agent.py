# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
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


from Queue import Queue
from threading import Thread
import logging
from volttron.platform.agent import utils, matching
import settings
import sqlite3
import json
from os.path import expanduser

TOPICHEAD = "/hiveos"

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
    servicebus_topic = settings.gateway_id
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
            self.azure_queue = Queue()
            self.azure_thread = None

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self._agent_id = self.config.get('agentid')

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            # Start Azure thread
            self.azure_thread = Thread(target=self._azure_get, )
            self.azure_thread.setDaemon(True)
            self.azure_thread.start()

        def _azure_get(self):

            _log.debug("Starting Thread")

            while True:
                try:
                    msg = sbs.receive_subscription_message(servicebus_topic, 'client1', peek_lock=False)
                    _log.debug("Got Azure messages")
                    if msg.body is not None:
                        commsg = eval(msg.body)
                        self.azure_queue.put(commsg)
                except:
                    _log.debug("Error whilst waiting for Azure message.")
                    pass

        @Core.periodic(1)
        def process_azure_messages(self):
            # _log.debug("Looking for Azure messages")
            while not self.azure_queue.empty():
                try:
                    print ("")
                    commsg = self.azure_queue.get()

                    _log.debug("Processing Azure message : {}".format(commsg))
                    # print("message MQTT received datas")
                    type_msg = str(commsg.get('type', None))

                    if type_msg.startswith('scene'):  # TODO : Recheck condition again
                        # print('Found scene')
                        print("pub to sence agrnt")
                        self.VIPPublishApplication(commsg, type_msg)

                    elif type_msg == 'service':
                        # Execute Device Control Function
                        # print("Device Cintrol Event")
                        if commsg['service'] == 'provisioning':
                            self.VIPPublishpro(commsg)
                        elif commsg['service'] == 'discover':
                            self.VIPPublishdis(commsg)

                    elif type_msg == 'devicecontrol':
                        print "move device control to iot hub"


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
                        pass
                except Exception as er:
                    print er

        def VIPPublishApplication(self, commsg, type_msg):
            topic = str('/ui/agent/update/hive/999/') + str(type_msg)
            message = json.dumps(commsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'HiVE Application to Gateway'}, message)

        def VIPPublishpro(self, commsg):
            topic = str(TOPICHEAD + '/service/provision')
            cmdmsg = {"type": "command", "command": "provision", "parameter": {}}
            for x in ["ssid", "passphrase"]:
                cmdmsg["parameter"][x] = commsg[x]
            message = json.dumps(cmdmsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'HiVE Application to Gateway'}, message)

        def VIPPublishdis(self, commsg):
            topic = str(TOPICHEAD + '/service/discover')
            cmdmsg = {"type": "command", "command": "discover", "parameter": {}}
            if "devicetype" in commsg:
                cmdmsg["parameter"]["devicetype"] = commsg["devicetype"]
            message = json.dumps(cmdmsg)
            print ("topic {}".format(topic))
            print ("message {}".format(message))

            self.vip.pubsub.publish(
                'pubsub', topic,
                {'Type': 'HiVE Application to Gateway'}, message)

        def VIPPublishDevice(self, commsg):
            topic = str('/ui/agent/update/hive/999/' + str(commsg['device']))
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
