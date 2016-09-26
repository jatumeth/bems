# -*- coding: utf-8 -*- {{{
from datetime import datetime
import logging
import sys

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
import settings
import json
import random

utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 5

class DeviceStatusAppAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(DeviceStatusAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self.status = "ON"
        self.statusAC1 = "ON"
        self.statusAC2 = "ON"
        self.statusAC3 = "ON"
        self.number_lamp = 13
        self.AC=3
        self.AC1=1
        self.AC2=1
        self.AC3=1




    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(DeviceStatusAppAgent, self).setup()

    # @matching.match_all
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # @matching.match_start("/ui/agent/")
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # Demonstrate periodic decorator and settings access
    @matching.match_exact('/agent/ui/lighting/device_status_response/bemoss/999/2HUE0017881cab4b')
    def on_matchlight(self, topic, headers, message, match):
        # '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        # print "Topic: {}".format(topic)
        # print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        try:
            self.status = received_message["status"]
            print "Now, Phillip HUE status : {}".format(self.status)
            if self.status=="ON":
                self.number_lamp=13
            elif self.status=="OFF":
                self.number_lamp=0
            else:
                print"Unknow Phillip HUE status"
        except:
            print "Unknow Phillip HUE status"
        print"---------------------------------------------------"

    @matching.match_exact('/agent/ui/airconditioner/device_status_response/bemoss/999/1TH20000000000001')
    def on_matchAC1(self, topic, headers, message, match):
        # '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        # print "Topic: {}".format(topic)
        # print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        try:
            self.statusAC1 = received_message["status"]
            print "Now, AC1 status : {}".format(self.statusAC1)
            if self.status=="ON":
                self.AC1=1
            elif self.status=="OFF":
                self.AC1=0
            else:
                print"Unknow AC1 status"
        except:
            print "Unknow AC1 status"
        print"---------------------------------------------------"

    @matching.match_exact('/agent/ui/airconditioner/device_status_response/bemoss/999/1TH20000000000002')
    def on_matchAC2(self, topic, headers, message, match):
        # '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        # print "Topic: {}".format(topic)
        # print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        try:
            self.statusAC2 = received_message["status"]
            print "Now, AC2 status : {}".format(self.statusAC2)
            if self.status=="ON":
                self.AC2=1
            elif self.status=="OFF":
                self.AC2=0
            else:
                print"Unknow AC1 status"
        except:
            print "Unknow AC1 status"
        print"---------------------------------------------------"

    @matching.match_exact('/agent/ui/airconditioner/device_status_response/bemoss/999/1TH20000000000003')
    def on_matchAC3(self, topic, headers, message, match):
        # '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        # print "Topic: {}".format(topic)
        # print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        try:
            self.statusAC3 = received_message["status"]
            print "Now, AC3 status : {}".format(self.statusAC3)
            if self.status=="ON":
                self.AC3=1
            elif self.status=="OFF":
                self.AC3=0
            else:
                print"Unknow AC1 status"
        except:
            print "Unknow AC1 status"
        print"---------------------------------------------------"

    @periodic(publish_periodic)
    def publish_heartbeat(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''
        topic = "/agent/ui/dashboard"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
            'data_source': "devicesStatus",
        }
        total_AC = 3
        total_lamp = 13
        total_plug = 3

        self.AC = self.AC1+self.AC2+self.AC3
        # number_AC_working = random.randint(0, total_AC)
        # number_lamp_working = random.randint(0, total_lamp)
        # number_plug_working = random.randint(0, total_plug)
        number_AC_working = self.AC
        number_lamp_working = self.number_lamp
        number_plug_working = 3
        message = json.dumps({"total_AC": total_AC,
                              "total_lamp": total_lamp,
                              "total_plug": total_plug,
                              "number_AC_working": number_AC_working,
                              "number_lamp_working": number_lamp_working,
                              "number_plug_working": number_plug_working})
        self.publish(topic, headers, message)
        print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)




def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(DeviceStatusAppAgent,
                           description='Agent to feed information from grid to UI and other agents',
                           argv=argv)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass