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

    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
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
    #
    # AC1_off("")
    # time.sleep(1)
    # AC2_off("")
    # time.sleep(1)
    # AC3_off("")
    #
    # AC1_off("")
    # time.sleep(1)
    # AC2_off("")
    # time.sleep(1)
    # AC3_off("")
    #
    AC1_on("")
    time.sleep(1)
    AC2_on("")
    time.sleep(1)
    AC3_on("")

    AC1_on("")
    time.sleep(1)
    AC2_on("")
    time.sleep(1)
    AC3_on("")


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


def wemo_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321'
    message = json.dumps({"status": "ON"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def wemo_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def hue_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b'
    message = json.dumps({"status": "ON","brightness": "100"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def hue_dim(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b'
    message = json.dumps({"status": "ON", "brightness": "50"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def hue_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def tv_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/tv/update/bemoss/999/1LG221445K1200137'
    message = json.dumps({"status": "ON"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def tv_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/tv/update/bemoss/999/1LG221445K1200137'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def fan_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1FN221445K1200138'
    message = json.dumps({"status": "ON"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def fan_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1FN221445K1200138'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def kitchen_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1KR221445K1200138'
    message1 = json.dumps({"status": "ON"})
    zmq_pub.requestAgent(topic, message1, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message1))

def kitchen_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1KR221445K1200138'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def living_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1LR221445K1200138'
    message1 = json.dumps({"status": "ON"})
    zmq_pub.requestAgent(topic, message1, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message1))

def living_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/fan/update/bemoss/999/1LR221445K1200138'
    message = json.dumps({"status": "OFF"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC1_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
    message = json.dumps({"1608F00680620":"0","status": "ON", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC2_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
    message = json.dumps({"1608F00680619":"0","status": "ON", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def AC3_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
    message = json.dumps({"1604F00640667":"0","status": "ON", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC4_on(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/ACD1200138'
    message = json.dumps({"1604F00640667":"0","status": "ON", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def AC1_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
    message = json.dumps({"1608F00680620":"0","status": "OFF", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC2_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
    message = json.dumps({"1608F00680619":"0","status": "OFF", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC3_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
    message = json.dumps({"1604F00640667":"0","status": "OFF", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC4_off(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/ACD1200138'
    message = json.dumps({"1604F00640667":"0","status": "OFF", "temp": "20","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC1_eco(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
    message = json.dumps({"1608F00680620":"0","status": "OFF", "temp": "26","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC2_eco(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
    message = json.dumps({"1608F00680619":"0","status": "OFF", "temp": "26","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))

def AC3_eco(commsg):
    print commsg
    # TODO this is example how to write an app to control AC
    topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
    message = json.dumps({"1604F00640667":"0","status": "OFF", "temp": "26","fan_speed": "4"})
    zmq_pub.requestAgent(topic, message, "text/plain", "UI")
    print ("topic{}".format(topic))
    print ("message{}".format(message))


def goodnight():
    print ""

def goodbye():
    print ""

def imback():
    print ""

def ecomode():
    print ""

while True:
    try:
        print("message MQTT received")
        msg = sbs.receive_subscription_message('home1', 'client1', peek_lock=False)
        print msg.body

        try:
            commsg = json.loads(msg.body)
            print(commsg)
        except:
            received_scene = msg.body[10:-2]
            print received_scene



        try:
            try:
                print ""
                scene = str(commsg['scene'])
            except:
                scene = received_scene
                commsg = "commsg"


            if str(scene) == "Good Morning":

                # sonos.play_uri(
                #
                #     'https://dl.dropbox.com/s/pus8oswb8ic4443/morning.m4a?dl=0')
                #
                # track = sonos.get_current_track_info()
                #
                # print track['title']
                # sonos.play()

                print "change mode to morning"
                living_on(commsg)
                time.sleep(1)
                kitchen_off(commsg)
                time.sleep(1)
                hue_on(commsg)
                time.sleep(1)
                AC1_on(commsg)
                time.sleep(1)
                AC2_on(commsg)
                time.sleep(1)
                AC3_off(commsg)
                time.sleep(1)
                tv_on(commsg)
                time.sleep(1)
                fan_off(commsg)
                time.sleep(1)
                wemo_off(commsg)
                time.sleep(1)
                living_on(commsg)
                time.sleep(1)
                kitchen_off(commsg)

                # time.sleep(1)
                # AC1_on(commsg)
                # time.sleep(1)
                # AC2_on(commsg)
                # time.sleep(1)
                # AC3_off(commsg)



            elif str(scene) == "Good Night":
                print "change mode to night"
                # sonos.play_uri(
                #
                #     'https://dl.dropbox.com/s/ozj0vjmj1n3dp8g/night.m4a?dl=0')
                #
                # track = sonos.get_current_track_info()
                #
                # print track['title']
                # sonos.play()

                living_off(commsg)
                time.sleep(1)
                hue_off(commsg)
                time.sleep(1)
                AC1_off(commsg)
                time.sleep(1)
                AC2_off(commsg)
                time.sleep(1)
                AC3_on(commsg)
                time.sleep(1)
                tv_off(commsg)
                # time.sleep(1)
                fan_off(commsg)
                # time.sleep(1)
                wemo_on(commsg)


                # time.sleep(1)
                # living_off(commsg)
                # time.sleep(1)
                # kitchen_off(commsg)
                # time.sleep(1)
                # AC1_off(commsg)
                # time.sleep(1)
                # AC2_off(commsg)
                # time.sleep(1)
                # AC3_on(commsg)

            elif str(scene) == "Good Bye":
                print "change mode to bye"
                living_off(commsg)
                time.sleep(1)
                hue_off(commsg)
                time.sleep(1)
                AC1_off(commsg)
                time.sleep(1)
                AC2_off(commsg)
                time.sleep(1)
                AC3_off(commsg)
                # time.sleep(1)
                tv_off(commsg)
                # time.sleep(1)
                fan_off(commsg)
                # time.sleep(1)
                wemo_off(commsg)
                # time.sleep(1)
                # living_off(commsg)
                # time.sleep(1)
                # kitchen_off(commsg)
                #
                # time.sleep(1)
                # AC1_off(commsg)
                # time.sleep(1)
                # AC2_off(commsg)
                # time.sleep(1)
                # AC3_off(commsg)

            elif (str(scene) == "I'm Back") or (str(scene) == "I am Back"):

                # sonos.play_uri(
                #
                #     'https://dl.dropbox.com/s/rhh2qtjtoic9kfm/back.m4a?dl=0')
                #
                # track = sonos.get_current_track_info()
                #
                # print track['title']
                # sonos.play()

                print "change mode to back"
                living_on(commsg)
                time.sleep(1)
                hue_on(commsg)
                time.sleep(1)
                AC1_on(commsg)
                time.sleep(1)
                AC2_on(commsg)
                time.sleep(1)
                AC3_on(commsg)
                time.sleep(1)
                # tv_on(commsg)
                time.sleep(1)
                fan_off(commsg)
                # time.sleep(1)
                wemo_on(commsg)
                # time.sleep(1)
                # living_on(commsg)
                # time.sleep(1)
                # kitchen_off(commsg)
                #
                time.sleep(1)
                AC1_on(commsg)
                time.sleep(1)
                AC2_on(commsg)
                time.sleep(1)
                AC3_on(commsg)

            elif str(scene) == "ECO MODE":
                print "change mode to eco"
                living_off(commsg)
                time.sleep(1)
                hue_dim(commsg)
                time.sleep(1)
                AC1_eco(commsg)
                time.sleep(1)
                AC2_eco(commsg)
                time.sleep(1)
                AC3_eco(commsg)
                time.sleep(1)
                tv_on(commsg)
                # time.sleep(1)
                fan_on(commsg)
                # time.sleep(1)
                wemo_off(commsg)
                # time.sleep(1)
                # living_off(commsg)
                # time.sleep(1)
                # kitchen_off(commsg)
                #
                # time.sleep(1)
                # AC1_eco(commsg)
                # time.sleep(1)
                # AC2_eco(commsg)
                # time.sleep(1)
                # AC3_eco(commsg)

            else:
                print(str(scene))
                print "--------------------------------------"
        except:
            print "no scene"


        try:
            device = str(commsg['device'])
            if str(device) == "hue1":  # check if the data is valid
                hue(commsg)
            elif str(device) == "wemo1":
                wemo(commsg)

            elif str(device) == "daikin1":
                daikin(commsg)

            elif str(device) == "lgtv1":
                lg(commsg)

            elif str(device) == "fan1":
                fan(commsg)
            else:
                print "Receiving message not in HiVE IoT Device "
        except:
            print "no device"

    except:
        print "dasdasdsaasadssaadsd"



