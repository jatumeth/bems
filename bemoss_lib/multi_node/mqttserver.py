# -*- coding: utf-8 -*-
#UDP server responds to broadcast packets
#you can have only one instance of this running as a BEMOSS core!!
# from soco import SoCo

# sonos = SoCo('192.168.1.4') # Pass in the IP of your Sonos speaker
import os
import json
import sys
os.chdir(os.path.expanduser("~/workspace/bemoss_os/"))  # = ~/workspace/bemoss_os
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
from zmqhelper.ZMQHelper.zmq_pub import ZMQ_PUB
import time




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


def kitchen(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/light/update/bemoss/999/1KR221445K1200138"
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

def living(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/light/update/bemoss/999/1LR221445K1200138"
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

def saijo1(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001"
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

def saijo2(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002"
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

def saijo3(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = "/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003"
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
    # topic = '/ui/agent/AC/update/bemoss/999/ACD1200138'
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

def lg(commsg):
    # TODO this is example how to write an app to control Lighting
    topic = '/ui/agent/tv/update/bemoss/999/1LG221445K1200137'
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

def HC(commsg):
    print commsg
    print "testhomescence"
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/homescence/update/bemoss/999/HC001'
    message = json.dumps(commsg)
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

while True:
    try:

        msg = sbs.receive_subscription_message('home1', 'client1', peek_lock=False)
        print msg.body
        commsg = json.loads(msg.body)
        print("message MQTT received")

        for k, v in commsg.items():
            if k == 'device':
                if (commsg['device']) == "hue1":
                    hue(commsg)
                elif (commsg['device']) == "wemo1":
                    wemo(commsg)
                elif (commsg['device']) == "daikin1":
                    daikin(commsg)
                elif (commsg['device']) == "lgtv1":
                    lg(commsg)
                elif (commsg['device']) == "fan1":
                    fan(commsg)
                elif (commsg['device']) == "saijo1":
                    saijo1(commsg)
                    time.sleep(3)
                    saijo1(commsg)
                elif (commsg['device']) == "saijo2":
                    saijo2(commsg)
                    time.sleep(3)
                    saijo2(commsg)
                elif (commsg['device']) == "saijo3":
                    saijo3(commsg)
                    time.sleep(3)
                    saijo3(commsg)
                elif (commsg['device']) == "living":
                    living(commsg)
                elif (commsg['device']) == "kitchen":
                    kitchen(commsg)
                else:
                    print ""
            elif k == 'scene':
                HC(commsg)
            else:
                print ""
    except Exception as er:
        print er



