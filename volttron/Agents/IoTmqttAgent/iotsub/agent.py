# -*- coding: utf-8 -*-
from __future__ import absolute_import
# from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
from datetime import datetime
import logging
import sys
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

import time
import sys
import iothub_client
from iothub_client import IoTHubClient, IoTHubClientError, IoTHubTransportProvider, IoTHubClientResult
from iothub_client import IoTHubMessage, IoTHubMessageDispositionResult, IoTHubError
import json

RECEIVE_CONTEXT = 0
WAIT_COUNT = 10
RECEIVED_COUNT = 0
RECEIVE_CALLBACKS = 0

# choose AMQP or AMQP_WS as transport protocol
PROTOCOL = IoTHubTransportProvider.MQTT
CONNECTION_STRING = "HostName=peahiveiotv2.azure-devices.net;DeviceId=MyPythonDevice;SharedAccessKey=p3dQOhW/2jIIIj5cturyC8qmnTG1fWkH6QMYbLOu4Xc="

TOPICHEAD = "/hiveos"

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'HELLO'


# service_namespace = settings.AZURE['servicebus']['service_namespace']
# shared_access_key_name = settings.AZURE['servicebus']['shared_access_key_name']
# shared_access_key_value = settings.AZURE['servicebus']['shared_access_key_value']
# servicebus_topic = settings.gateway_id
# sbs = ServiceBusService(
#     service_namespace=service_namespace,
#     shared_access_key_name=shared_access_key_name,
#     shared_access_key_value=shared_access_key_value)

# Step1: Agent Initialization
def iothubsub_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    class iothubsubAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(iothubsubAgent, self).__init__(**kwargs)
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

        def receive_message_callback(self, message, counter):
            global RECEIVE_CALLBACKS
            message_buffer = message.get_bytearray()
            size = len(message_buffer)
            print("Received Message [%d]:" % counter)
            print("    Data: <<<%s>>> & Size=%d" % (message_buffer[:size].decode('utf-8'), size))
            data = json.loads(message_buffer[:size].decode('utf-8'))
            # print(type(data))
            # print(data)
            commsg = data['message']
            type_msg = str(commsg.get('type', None))

            if type_msg.startswith('scene'):  # TODO : Recheck condition again
                # print('Found scene')
                self.VIPPublishApplication(commsg, type_msg)

            elif type_msg == 'service':
                # Execute Device Control Function
                # print("Device Cintrol Event")
                if commsg['service'] == 'provisioning':
                    self.VIPPublishpro(commsg)
                elif commsg['service'] == 'discover':
                    self.VIPPublishdis(commsg)

            elif type_msg == 'devicecontrol':
                self.VIPPublishDevice(commsg)

            elif type_msg == 'automationcreate':
                # Execute Create Automation Function
                # print("Create Automation Event")
                self.VIPPublishApplication(commsg, type_msg)

            elif type_msg == 'automationdelete':
                # Execute Delete Automation Function
                # print("Delete Automation Event")
                self.VIPPublishApplication(commsg, type_msg)

            elif type_msg == 'automationupdate':
                # Execute Update Automation Function
                # print("Update Automation Event")
                self.VIPPublishApplication(commsg, type_msg)

            else:
                pass

            # self.azure_queue.put(data)  # <----------------- check!!!
            map_properties = message.properties()
            key_value_pair = map_properties.get_internals()
            print("    Properties: %s" % key_value_pair)
            counter += 1
            RECEIVE_CALLBACKS += 1
            print("    Total calls received: %d" % RECEIVE_CALLBACKS)
            return IoTHubMessageDispositionResult.ACCEPTED

        def iothub_client_init(self):
            client = IoTHubClient(CONNECTION_STRING, PROTOCOL)

            client.set_message_callback(self.receive_message_callback, RECEIVE_CONTEXT)

            return client

        def print_last_message_time(self, client):
            try:
                last_message = client.get_last_message_receive_time()
                print("Last Message: %s" % time.asctime(time.localtime(last_message)))
                print("Actual time : %s" % time.asctime())
            except IoTHubClientError as iothub_client_error:
                if iothub_client_error.args[0].result == IoTHubClientResult.INDEFINITE_TIME:
                    print("No message received")
                else:
                    print(iothub_client_error)

        def _azure_get(self):

            _log.debug("Starting Thread")

            try:
                client = self.iothub_client_init()

                while True:
                    print("IoTHubClient waiting for commands, press Ctrl-C to exit")

                    status_counter = 0
                    while status_counter <= WAIT_COUNT:
                        status = client.get_send_status()
                        print("Send status: %s" % status)
                        time.sleep(10)
                        status_counter += 1

            except IoTHubError as iothub_error:
                print("Unexpected error %s from IoTHub" % iothub_error)
                return
            except KeyboardInterrupt:
                print("IoTHubClient sample stopped")

            self.print_last_message_time(client)

        # @Core.periodic(1)
        # def process_azure_messages(self):
        #     # _log.debug("Looking for Azure messages")
        #     while not self.azure_queue.empty():
        #         try:
        #             print ("")
        #             msg = self.azure_queue.get()
        #
        #             commsg = commsg['message']
        #
        #             _log.debug("Processing Azure message : {}".format(commsg))
        #             # print("message MQTT received datas")
        #             type_msg = str(commsg.get('type', None))
        #
        #             if type_msg.startswith('scene'):  # TODO : Recheck condition again
        #                 # print('Found scene')
        #                 self.VIPPublishApplication(commsg, type_msg)
        #
        #             elif type_msg == 'service':
        #                 # Execute Device Control Function
        #                 # print("Device Cintrol Event")
        #                 if commsg['service'] == 'provisioning':
        #                     self.VIPPublishpro(commsg)
        #                 elif commsg['service'] == 'discover':
        #                     self.VIPPublishdis(commsg)
        #
        #             elif type_msg == 'devicecontrol':
        #                 self.VIPPublishDevice(commsg)
        #
        #             elif type_msg == 'automationcreate':
        #                 # Execute Create Automation Function
        #                 # print("Create Automation Event")
        #                 self.VIPPublishApplication(commsg, type_msg)
        #
        #             elif type_msg == 'automationdelete':
        #                 # Execute Delete Automation Function
        #                 # print("Delete Automation Event")
        #                 self.VIPPublishApplication(commsg, type_msg)
        #
        #             elif type_msg == 'automationupdate':
        #                 # Execute Update Automation Function
        #                 # print("Update Automation Event")
        #                 self.VIPPublishApplication(commsg, type_msg)
        #
        #             else:
        #                 pass
        #         except Exception as er:
        #             print(er)

        def VIPPublishApplication(self, commsg, type_msg):
            topic = str('/ui/agent/update/hive/999/') + str(type_msg)
            message = json.dumps(commsg)
            # print ("topic {}".format(topic))
            # print ("message {}".format(message))

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
    return iothubsubAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(iothubsub_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())