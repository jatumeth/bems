# -*- coding: utf-8 -*-
#UDP server responds to broadcast packets
#you can have only one instance of this running as a BEMOSS core!!
import os
import sys
os.chdir(os.path.expanduser("~/workspace/bemoss_os/"))  # = ~/workspace/bemoss_os
current_working_directory = os.getcwd()
sys.path.append(current_working_directory)
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
from zmqhelper.ZMQHelper.zmq_pub import ZMQ_PUB
import requests
import json
import time
import logging
import os
from volttron.platform.agent import utils, matching
from uuid import getnode as get_mac


utils.setup_logging()  # setup logger for debugging
_log = logging.getLogger(__name__)

PUSH_SOCKET = "ipc:///home/tpponmat/.volttron/run/publish"
SUB_SOCKET = "ipc:///home/tpponmat/.volttron/run/subscribe"

kwargs = {'subscribe_address': SUB_SOCKET, 'publish_address': PUSH_SOCKET}
zmq_pub = ZMQ_PUB(**kwargs)

sbs = ServiceBusService(
                service_namespace='peahiveservicebus',
                shared_access_key_name='RootManageSharedAccessKey',
                shared_access_key_value='vOjEoWzURJCJ0bAgRTo69o4BmLy8GAje4CfdXkDiwzQ=')

def deviceMonitorBehavior():

    agent_id = "devicediscoveryagent"

    os.system(  # ". env/bin/activate"
        "volttron-ctl stop --tag " + agent_id +
        ";volttron-ctl start --tag " + agent_id +
        ";volttron-ctl status")
    print "1"
    time.sleep(60)

    os.system(  # ". env/bin/activate"
        "volttron-ctl stop --tag " + agent_id +
        ";volttron-ctl status")

def send_requeston():
    # scene
    # PUT https://api.netpie.io/topic/P1Site/SMH
    try:
        response = requests.put(
            url="https://api.netpie.io/topic/P1Site/SMH",
            params={
                "retain": "OFF",
                "auth": "U0Qa6TlkPIjpwXP:tXk4e5hra3OFGt1aZyaAnu0rP",
            },
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "id": "C1",
                "state": "on",
                "site": "7727a0190f32d6bc59a52a26c69b3336b49be7bcc1c4",
                "agent": "N2",
                "branch": "control",
                "sender": "webview"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def send_requestoff():
    # scene
    # PUT https://api.netpie.io/topic/P1Site/SMH
    try:
        response = requests.put(
            url="https://api.netpie.io/topic/P1Site/SMH",
            params={
                "retain": "OFF",
                "auth": "U0Qa6TlkPIjpwXP:tXk4e5hra3OFGt1aZyaAnu0rP",
            },
            headers={
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "id": "C1",
                "state": "off",
                "site": "7727a0190f32d6bc59a52a26c69b3336b49be7bcc1c4",
                "agent": "N2",
                "branch": "control",
                "sender": "webview"
            })
        )
        print('Response HTTP Status Code: {status_code}'.format(
            status_code=response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content=response.content))
    except requests.exceptions.RequestException:
        print('HTTP Request failed')





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

    print "99999999999999999999999999999"

    topic = '/ui/agent/AC/update/bemoss/999/1ACD1200138'
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

mac = hex(get_mac())[0:10]
print mac

while True:

    try:

	print "mqtt server is waiting for message from Azure"
        msg = sbs.receive_subscription_message(str(mac), 'client1', peek_lock=False)

        print msg.body
        commsg = eval(msg.body)

        if (commsg['devicediscovery'] == True):
            print "777"
            deviceMonitorBehavior()
        else:
            print ""

        print("message MQTT received")

        for k, v in commsg.items():
            if k == 'device':
                if (commsg['device']) == "2HUEH":
                    hue(commsg)
                elif (commsg['device']) == "3WSP2":
                    try :
                        if (commsg['status']) == "ON":
                            print "on"
                            send_requeston()
                        else:
                            print "off"
                            send_requestoff()
                    except:
                        print ""

                elif (commsg['device']) == "16SCH":
                    wemo(commsg)
                elif (commsg['device']) == "1DAIK":
                    daikin(commsg)
                elif (commsg['device']) == "11LG1":
                    lg(commsg)
                elif (commsg['device']) == "11LG2":
                    lg(commsg)
                elif (commsg['device']) == "7FAN":
                    fan(commsg)

                elif (commsg['device']) == "1SAJ1":
                    saijo1(commsg)
                    time.sleep(3)
                    saijo1(commsg)
                elif (commsg['device']) == "1SAJ2":
                    saijo2(commsg)
                    time.sleep(3)
                    saijo2(commsg)
                elif (commsg['device']) == "1SAJ3":
                    saijo3(commsg)
                    time.sleep(3)
                    saijo3(commsg)
                elif (commsg['device']) == "2HUEL":
                    living(commsg)
                elif (commsg['device']) == "2HUEK":
                    kitchen(commsg)
                else:
                    print ""
            elif k == 'scene':
                HC(commsg)
            else:
                print ""
    except Exception as er:
        print er



