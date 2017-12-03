# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright (c) 2013, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the FreeBSD Project.
#

# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization
# that has cooperated in the development of these materials, makes
# any warranty, express or implied, or assumes any legal liability
# or responsibility for the accuracy, completeness, or usefulness or
# any information, apparatus, product, software, or process disclosed,
# or represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does
# not necessarily constitute or imply its endorsement, recommendation,
# r favoring by the United States Government or any agency thereof,
# or Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830


#Author : Payyoh
#}}}

from soco import SoCo
sonos = SoCo('192.168.1.110')
from datetime import datetime
import logging
import sys
import json
import time

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings


utils.setup_logging()
_log = logging.getLogger(__name__)


class ListenerAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(ListenerAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # test control air
        # self.publish_heartbeat()
        # Always call the base class setup()
        super(ListenerAgent, self).setup()


    @matching.match_exact('/ui/agent/homescence/update/bemoss/999/HC001')
    def on_777(self,topic,headers,message,match):
        '''Use match_all to receive all messages and print them out.'''

        print "Topic: {}".format(topic)
        print "Message: {}".format(message)
        received_message = json.loads(message[0])
        scene = str(received_message['scene'])

        if str(scene) == "Good Morning":
            self.Morning()
        elif str(scene) == "Good Night":
            self.Night()
        elif str(scene) == "Good Bye":
            self.Bye()
        elif (str(scene) == "I'm Back") or (str(scene) == "I am Back"):
            self.Back()
        elif str(scene) == "ECO MODE":
            self.eco()
        else:
            print""

    def Morning(self):
        '''Use match_all to receive all messages and print them out.'''
        print "change mode to morning"
        sonos.play_uri(

            'https://dl.dropboxusercontent.com/s/8x4i9c91e4aozfk/goodmorning.m4a?dl=0')

        track = sonos.get_current_track_info()

        print track['title']
        sonos.play()

        self.somfy_on()
        self.yale_off()
        # self.living_on()
        # self.kitchen_on()
        self.hue_on()
        self.AC1_temp20()
        # time.sleep(1)
        # self.AC2_temp20()
        # self.AC3_off()
        self.tv_on()
        # self.fan_off()
        # time.sleep(1)
        self.plug_off()
        time.sleep(1)
        # self.living_on()
        # time.sleep(1)
        # self.kitchen_on()

    def Night(self):
        '''Use match_all to receive all messages and print them out.'''
        print "change mode to night"
        sonos.play_uri(

            'https://dl.dropboxusercontent.com/s/dy38rmyqncfowww/goodnight.m4a?dl=0')

        track = sonos.get_current_track_info()

        print track['title']
        sonos.play()

        self.somfy_off()
        # self.living_off()
        self.yale_on()
        self.hue_off()
        time.sleep(1)
        self.AC1_off()
        time.sleep(1)
        # self.AC2_off()
        # self.AC3_temp20()
        # time.sleep(1)
        self.tv_off()
        # self.fan_off()
        self.plug_on()
        # self.living_off()
        # self.kitchen_off()

    def Bye(self):
        '''Use match_all to receive all messages and print them out.'''

        sonos.play_uri(

            'https://dl.dropbox.com/s/yv82s4q7c7jmlju/goodbye.m4a?dl=0')

        track = sonos.get_current_track_info()

        print track['title']
        sonos.play()

        self.somfy_off()
        print "change mode to bye"
        # self.living_off()
        self.yale_on()
        self.hue_off()
        self.AC1_off()
        # time.sleep(1)
        # self.AC2_off()
        # self.AC3_off()
        time.sleep(1)
        self.tv_off()
        # self.fan_off()
        self.plug_off()
        # self.living_off()
        # self.kitchen_off()

    def Back(self):
        '''Use match_all to receive all messages and print them out.'''
        print "change mode to back"

        sonos.play_uri(

            'https://dl.dropboxusercontent.com/s/bpdgpong5y66nnb/welcomback.m4a')

        track = sonos.get_current_track_info()

        print track['title']
        sonos.play()
        self.somfy_on()
        # self.living_on()
        # time.sleep(1)
        self.yale_off()
        self.hue_on()
        self.AC1_temp20()
        # time.sleep(1)
        # self.AC2_temp20()
        # self.AC3_temp20()
        self.tv_on()
        self.fan_off()
        self.plug_on()
        # self.living_on()
        # self.kitchen_off()

    def eco(self):
        '''Use match_all to receive all messages and print them out.'''

        sonos.play_uri(

            'https://dl.dropbox.com/s/0lq6qy2l5zjkvt4/ecomode.m4a?dl=0')

        track = sonos.get_current_track_info()

        print track['title']
        sonos.play()

        print "change mode to eco"
        # self.living_off()
        self.hue_dim()
        self.AC1_temp27()
        time.sleep(1)
        # self.AC2_temp27()
        # self.AC3_temp27()
        self.tv_on()
        # self.fan_on()
        self.plug_off()
        # self.living_off()
        # self.kitchen_off()

    def AC1_temp20(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "20", "mode": "3"})
        self.publish(topic, headers, message)
        print ("AC1 turned on : temp 20")

    def AC2_temp20(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"LivingroomAir2":"0","status": "ON", "temp": "20","fan_speed": "4"})
        self.publish(topic, headers, message)
        print ("AC2 turned on : temp 20")

    def AC3_temp20(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"BedroomAir":"0","status": "ON", "temp": "20","fan_speed": "4"})
        # print ("message{}".format(message))
        self.publish(topic, headers, message)
        print ("AC3 turned on : temp 20")

    def AC1_temp27(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "20", "mode": "3"})
        self.publish(topic, headers, message)
        print ("AC1 turned on : temp 27")

    def AC1_off(self):
        # TODO this is example how to write an app to control AC

        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "20", "mode": "3"})
        self.publish(topic, headers, message)
        print ("AC1 turned off")
    #
    def AC2_temp27(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"LivingroomAir2":"0","status": "ON", "temp": "27","fan_speed": "1"})
        self.publish(topic, headers, message)
        print ("AC2 turned on : temp 27")

    def AC2_off(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"LivingroomAir2":"0","status": "OFF"})
        self.publish(topic, headers, message)
        print ("AC2 turned off")

    def AC3_temp27(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"BedroomAir":"0","status": "ON", "temp": "27","fan_speed": "1"})
        self.publish(topic, headers, message)
        print ("AC3 turned on : temp 27")
    #
    def AC3_off(self):
        # TODO this is example how to write an app to control AC
        topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000003'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"BedroomAir":"0","status": "OFF"})
        self.publish(topic, headers, message)
        print ("AC3 turned off")

    #

    def ChangeActor(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"actor": "demand_respond",})
        # print ("message{}".format(message))


    def hue_on(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("HUE turn ON")
        print ("topic{}".format(topic))
        print ("message{}".format(message))

    def hue_off(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("HUE turn OFF")
    #
    def hue_dim(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "brightness": 10})
        self.publish(topic, headers, message)
        print ("HUE DIM brightness by DR, eco or Comfort mode ")

    def hue_max(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "brightness": 100})
        self.publish(topic, headers, message)
        print ("HUE DIM brightness")



    def plug_on(self):
        # TODO this is example how to write an app to control plugload EV
        topic = "/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("plug EV turn ON")
    #
    def plug_off(self):
        # TODO this is example how to write an app to control plugload EV
        topic = "/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("plug EV turn OFF")


    def fan_on(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/relaysw/update/bemoss/999/1FN221445K1200138"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("FAN turn ON")


    def fan_off(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/relaysw/update/bemoss/999/1FN221445K1200138"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("FAN turn OFF")


    def tv_on(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/1LG221445K1200137"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("TV turn ON")


    def tv_off(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/1LG221445K1200137"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("TV turn OFF")


    def yale_on(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/18DOR06"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("Yale turn ON")

    def yale_off(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/18DOR06"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("Yale turn OFF")

    def somfy_on(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/3WSP221445K1200328"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("Yale turn ON")

    def somfy_off(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/tv/update/bemoss/999/3WSP221445K1200328"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("Yale turn OFF")



    def kitchen_on(self):
        # TODO this is example how to write an app to control FAN
        topic = '/ui/agent/light/update/bemoss/999/1KR221445K1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("kitchen turn ON")

    def kitchen_off(self):
        # TODO this is example how to write an app to control FAN
        topic = '/ui/agent/light/update/bemoss/999/1KR221445K1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("kitchen turn OFF")

    def living_on(self):
        # TODO this is example how to write an app to control FAN
        topic = '/ui/agent/light/update/bemoss/999/1LR221445K1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("living turn ON")

    def living_off(self):
        # TODO this is example how to write an app to control FAN
        topic = '/ui/agent/light/update/bemoss/999/1LR221445K1200138'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("living turn OFF")


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(ListenerAgent,
                           description='Example VOLTTRON platform™ heartbeat agent',
                           argv=argv)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass