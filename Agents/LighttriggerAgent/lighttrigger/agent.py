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

# from soco import SoCo
# sonos = SoCo('192.168.1.110')
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

    @matching.match_exact('/agent/ui/8FIB/device_status_response/bemoss/999/8MS221445K1200132')
    def test1(self, topic, headers, message, match):
        print "Fibaro: {}".format(json.loads(message[0]))
        data_fibaro = json.loads(message[0])
        illuminance = int(data_fibaro['illuminance'])
        print "illuminance: {}".format(illuminance)

        if illuminance >= 800:
            self.somfy_off()
            self.plug_off()

        elif illuminance < 70:
            self.somfy_on()
            self.plug_on()

        else:
            print('error')

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

    def somfy_on(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/03MRB/update/bemoss/999/03MRB221445K1200328"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("Sompy turn ON")

    def somfy_off(self):
        # TODO this is example how to write an app to control FAN
        topic = "/ui/agent/03MRB/update/bemoss/999/03MRB221445K1200328"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("Sompy turn OFF")

    def plug_on(self):
        # TODO this is example how to write an app to control plugload EV
        topic = "/ui/agent/3WSP2/update/bemoss/999/3WSP221445K1200321"
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
        topic = "/ui/agent/3WSP2/update/bemoss/999/3WSP221445K1200321"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("plug EV turn OFF")


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