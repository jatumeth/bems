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


from datetime import datetime
import logging
import sys
import json

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

    @matching.match_start('/ui/agent/airconditioner/')
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        _log.debug("Topic: {topic}, Headers: {headers}, "
                         "Message: {message}".format(
                         topic=topic, headers=headers, message=message))
        print("")


    #test multisensor
    # @matching.match_exact('/agent/ui/MultiSensor/device_status_response/bemoss/999/1MS221445K1200132')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     # _log.debug("Topic: {topic}, Headers: {headers}, "
    #     #            "Message: {message}".format(
    #     #     topic=topic, headers=headers, message=message))
    #     print "MultiSensor----------"
    #     print "Topic: {}".format(topic)
    #     print "Headers: {}".format(headers)
    #     #print "Message: {}".format(message)
    #     received_message = json.loads(message[0])
    #     print received_message
    #     print"---------------------------------------------------"

    #test Weathers
    # @matching.match_exact('/agent/ui/Weathers/device_status_response/bemoss/999/1WE221445K1200132')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     # _log.debug("Topic: {topic}, Headers: {headers}, "
    #     #            "Message: {message}".format(
    #     #     topic=topic, headers=headers, message=message))
    #     print "Weathers----------"
    #     print "Topic: {}".format(topic)
    #     print "Headers: {}".format(headers)
    #     #print "Message: {}".format(message)
    #     received_message = json.loads(message[0])
    #     print received_message
    #     print"---------------------------------------------------"

        # test Fan
    # @matching.match_exact('/agent/ui/fan/device_status_response/bemoss/999/1FN221445K1200138')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     # _log.debug("Topic: {topic}, Headers: {headers}, "
    #     #            "Message: {message}".format(
    #     #     topic=topic, headers=headers, message=message))
    #     print "Fan---------"
    #     print "Topic: {}".format(topic)
    #     print "Headers: {}".format(headers)
    #     # print "Message: {}".format(message)
    #     received_message = json.loads(message[0])
    #     print received_message
    #     print"---------------------------------------------------"

    # #fridge
    # @matching.match_exact('/agent/ui/refridgerator/device_status_response/bemoss/999/1FR221445K1200111')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     # _log.debug("Topic: {topic}, Headers: {headers}, "
    #     #            "Message: {message}".format(
    #     #     topic=topic, headers=headers, message=message))
    #     print "fridge---------"
    #     print "Topic: {}".format(topic)
    #     print "Headers: {}".format(headers)
    #     # print "Message: {}".format(message)
    #     received_message = json.loads(message[0])
    #     print received_message
    #     print"---------------------------------------------------"

    #LGTV
    @matching.match_exact('/agent/ui/lgtvagent/device_status_response/bemoss/999/1LG221445K1200137')
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        print "LGTV---------"
        print "Topic: {}".format(topic)
        print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        print received_message
        print"---------------------------------------------------"


    # @matching.match_start("/ui/agent/")
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # Demonstrate periodic decorator and settings access
    # @periodic(settings.HEARTBEAT_PERIOD)
    # @periodic(10)
    # def publish_heartbeat(self):
    #     '''Send heartbeat message every HEARTBEAT_PERIOD seconds.
    #
    #     HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
    #     '''
    #
    #     # TODO this is example how to write an app to control AC
    #     # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000002'
    #     # now = datetime.utcnow().isoformat(' ') + 'Z'
    #     # headers = {
    #     #     'AgentID': self._agent_id,
    #     #     headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #     #     headers_mod.DATE: now,
    #     # }
    #     # import time
    #     # # message = json.dumps({"status": "OFF"});
    #     # # self.publish(topic, headers, message)
    #     # # time.sleep(30)
    #     # message = json.dumps({"status": "ON"});
    #     # self.publish(topic, headers, message)
    #
    #     # TODO this is example how to write an app to control Refrigerator
    #     topic = '/ui/agent/refridgerator/update/bemoss/999/1FR221445K1200111'
    #     now = datetime.utcnow().isoformat(' ') + 'Z'
    #     headers = {
    #         'AgentID': self._agent_id,
    #         headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #         headers_mod.DATE: now,
    #     }
    #     message = json.dumps({"temp":"-5"})
    #     self.publish(topic, headers, message)

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