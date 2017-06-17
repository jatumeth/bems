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


from datetime import datetime
import logging
import sys
import json
import requests

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings


utils.setup_logging()
_log = logging.getLogger(__name__)

import microgear.client as microgear
import time
import logging

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
        self.message = ''
        # NETPIE --------------------
        appid = "RSDPEA"
        gearkey = "5xeHHg4vpGAYTzj"
        gearsecret = "N2hc2XaAriu2grlvRO0kEEglE"

        microgear.create(gearkey, gearsecret, appid, {'debugmode': True})

        # def connection():
        #     logging.debug("Now I am connected with netpie")
        #
        #
        # def subscription(self, topic, message):
        #     logging.debug(topic + " " + message)
        #     self.message = message
        #
        # def disconnect():
        #     logging.debug("disconnect is work")

        microgear.setalias("doraemons")
        microgear.on_connect = self.connection
        microgear.on_message = self.subscription
        microgear.on_disconnect = self.disconnect
        microgear.subscribe("/SMH/pushbutton")
        x = microgear.subscribe("/SMH/pushbutton")
        print "x:{}".format(x)
        microgear.connect(False)

        # ------------------------

        # test control air
        # self.publish_heartbeat()
        # self.status = "OFF"
        # Always call the base class setup()
        super(ListenerAgent, self).setup()

    def connection(self):
        logging.debug("Now I am connected with netpie")

    def subscription(self, topic, message):
        logging.debug(topic + " " + message)
        self.message = message
        print "self.message: {}".format(self.message)
        if (self.message == '1'):
            self.publish_heartbeat()
        else :
            print "pass"

    def disconnect(self):
        logging.debug("disconnect is work")

    # @matching.match_start('/ui/agent/airconditioner/')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # @periodic(10)
    # def testModal(self):
    #     self.publish_heartbeat()
    #     self.message = '1'
    #     print("publish_heartbeat message sent")

    # @periodic(5)
    # def check_PEA_DR_trigger_button(self):
    #
    #     try:
    #         r = requests.get("https://graph.api.smartthings.com/api/smartapps/installations/17244bfb-7963-41dc-beb2-f0acf9f2085c/switches/cbc76b94-35f6-4278-b231-768dd11e89e0",
    #                          headers={"Authorization": "Bearer adc2ff7d-5afe-4614-8590-fea0ad4cffcd"}, timeout=20);
    #         print("NetpieButtonAgent is querying its current status (status:{}) please wait ...".format(r.status_code))
    #         if r.status_code == 200:
    #             conve_json = json.loads(r.text)
    #             if (conve_json["status"] == "on"):
    #                 self.status = "ON"
    #                 self.message = '1'
    #                 self.publish_heartbeat()
    #             elif (conve_json["status"] == "off"):
    #                 self.status = "OFF"
    #             print (" Received status from PEA DR Trigger button as: {}".format(self.status))
    #         else:
    #             print (" Received an error from server, cannot retrieve results")
    #             getDeviceStatusResult = False
    #     except Exception as er:
    #         print er
    #         print('ERROR: Netpit button cannot get status from SmartThings PEA DR button')

    @matching.match_exact('/agent/ui/dashboard/netpiebutton')
    def on_match(self, topic, headers, message, match):
        # TODO this is example how to write an app to control Refrigerator
        # print "control: {}".format(control)
        self.message='1'
        if (self.message == '1'):
            now = datetime.utcnow().isoformat(' ') + 'Z'
            # TODO publish to dashboard
            topic = '/agent/ui/dashboard'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'data_source': "netpiebutton",
            }
            message = json.dumps({"event": "dr", "status": "enable"})
            self.publish(topic, headers, message)
            print ("sent message to UI for DR modal trigger")
            print ("topic {}".format(topic))
            print ("headers {}".format(headers))
            print ("message {}".format(message))
            # self.message = 0
        else :
            # TODO this is example how to write an app to control Lighting
            # topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            # headers = {
            #     'AgentID': self._agent_id,
            #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            #     headers_mod.DATE: now,
            # }
            # message = json.dumps({"status": "ON", "color": [0, 0, 255]})
            # self.publish(topic, headers, message)
            print ("NO MESSAGE FROM NETPIE")

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
