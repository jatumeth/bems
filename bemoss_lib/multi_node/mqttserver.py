# -*- coding: utf-8 -*-
#UDP server responds to broadcast packets
#you can have only one instance of this running as a BEMOSS core!!

import os
import json
import sys
os.chdir(os.path.expanduser("~/workspace/bemoss_os/"))  # = ~/workspace/bemoss_os
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
from bemoss_lib.databases.cassandraAPI import cassandraDB
import settings
import psycopg2
import datetime
import netifaces as ni
import fcntl, socket, struct
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
from volttron.platform.messaging import headers as headers_mod
from zmqhelper.ZMQHelper.zmq_pub import ZMQ_PUB

PUSH_SOCKET = "ipc:///home/dell-hive01/.volttron/run/publish"
SUB_SOCKET = "ipc:///home/dell-hive01/.volttron/run/subscribe"

kwargs = {'subscribe_address': SUB_SOCKET, 'publish_address': PUSH_SOCKET}
zmq_pub = ZMQ_PUB(**kwargs)

sbs = ServiceBusService(
                service_namespace='hiveservicebus',
                shared_access_key_name='RootManageSharedAccessKey',
                shared_access_key_value='vZmK7ee4YhIbaUEW5e/sgT0S8JV09LnToCOEqIU+7Qw=')


def hue(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
    # now = datetime.utcnow().isoformat(' ') + 'Z'
    # headers = {
    #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #     headers_mod.DATE: now,
    # }
    message = json.dumps(commsg)
    print type(message)

    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def wemo(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = '/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321'
    # now = datetime.utcnow().isoformat(' ') + 'Z'
    # headers = {
    #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #     headers_mod.DATE: now,
    # }
    message = json.dumps(commsg)
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def daikin(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = '/ui/agent/AC/update/bemoss/999/ACD1200138'
    # {"status": "OFF"}
    # now = datetime.utcnow().isoformat(' ') + 'Z'
    # headers = {
    #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #     headers_mod.DATE: now,
    # }
    message = json.dumps(commsg)
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def fan(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = '/ui/agent/fan/update/bemoss/999/1FN221445K1200138'
    # {"status": "OFF"}
    # now = datetime.utcnow().isoformat(' ') + 'Z'
    # headers = {
    #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #     headers_mod.DATE: now,
    # }
    message = json.dumps(commsg)
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


while True:
    try:
        print("message MQTT received")
        msg = sbs.receive_subscription_message('home1', 'client1', peek_lock=False)
        print msg.body

        commsg = json.loads(msg.body)
        device = str(commsg['device'])

        if str(device) == "hue1":  # check if the data is valid
            hue(commsg)
        elif str(device) == "wemo1":
            wemo(commsg)

        elif str(device) == "daikin1":
            daikin(commsg)

        elif str(device) == "fan1":
            fan(commsg)
        else:
            print "Receiving message not in HiVE IoT Device "
    except:
        print ""

