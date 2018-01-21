# -*- coding: utf-8 -*- {{{
#Author : Krip Phongphun
#}}}


from datetime import datetime
import logging
import sys
import json
import time
import time
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings


utils.setup_logging()
_log = logging.getLogger(__name__)


class TestACDaikinAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(TestACDaikinAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # test control air
        # self.publish_heartbeat()
        # Always call the base class setup()
        super(TestACDaikinAgent, self).setup()

    # @matching.match_start('/ui/agent/AC/update/bemoss/999/1ACD1200136')
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")
    #

    @periodic(1)
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(
        #     topic=topic, headers=headers, message=message))
        print "---------Testing_Daikin----------"
        # print "Topic: {}".format(topic)
        # print "Headers: {}".format(headers)
        # #print "Message: {}".format(message)
        # received_message = json.loads(message[0])
        # print received_message
        # print"---------------------------------------------------"
        print "start self.AC_off()"
        self.AC_off()
        time.sleep(60)

        print "elf.AC_on()"
        self.AC_on()
        time.sleep(60)

        print "self.AC_temp18()"
        self.AC_temp18()
        time.sleep(60)


        print "   start  self.AC_temp25()"
        self.AC_temp25()
        time.sleep(60)

        self.AC_temp32()
        time.sleep(60)

        self.AC_Mode_0()
        time.sleep(60)

        self.AC_Mode_2()
        time.sleep(60)

        self.AC_Speed_3()
        time.sleep(60)

        self.AC_Speed_5()
        time.sleep(60)

        self.AC_Speed_7()
        time.sleep(60)

        self.AC_Speed_Auto()
        time.sleep(60)

        self.AC_Speed_Silent()
        time.sleep(60)

        self.AC_Blade_V()
        time.sleep(60)

        self.AC_Blade_H()
        time.sleep(60)

        self.AC_Blade_VH()
        time.sleep(60)

        self.AC_Blade_off()
        time.sleep(60)

    def AC_on(self):
        # TODO this is example how to write an app to control AC

        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "20", "mode": "1"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on")

    def AC_off(self):
        # TODO this is example how to write an app to control AC

        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'
        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF", "device": "1DAIK"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned off")

    def AC_temp18(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "18", "mode": "1"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on : temp 18 Celcuis")

    def AC_temp25(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on : temp 25 Celcuis")

    def AC_temp32(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "32", "mode": "1"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on : temp 32 Celcuis")

    def AC_Mode_0(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "mode": "Fan"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on to Fan Mode")

    def AC_Mode_2(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "mode": "Dry"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on to Dry Mode")

    def AC_Speed_3(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_rate": "3"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on speed setting: 3")

    def AC_Speed_5(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_rate": "5"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on speed setting: 5")

    def AC_Speed_7(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_rate": "7"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on speed setting: 7")

    def AC_Speed_Auto(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_rate": "auto"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on speed setting: Auto")

    def AC_Speed_Silent(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_rate": "silent"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester turned on speed setting: silent")

    def AC_Blade_V(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_dir": "1"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester adjust relaysw direction in vertical")

    def AC_Blade_H(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_dir": "2"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester adjust relaysw direction in Horizontal")

    def AC_Blade_VH(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_dir": "3"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester adjust relaysw direction in 2 direction")

    def AC_Blade_off(self):
        # TODO this is example how to write an app to control AC
        # topic = '/ui/agent/airconditioner/update/bemoss/999/1TH20000000000001'

        topic = '/ui/agent/AC/update/bemoss/999/1ACD1200136'
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
            }
        message = json.dumps({"status": "ON", "device": "1DAIK", "stemp": "25", "mode": "1", "f_dir": "4"})
        self.publish(topic, headers, message)
        print ("AC Daikin Tester do not adjust relaysw direction")


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(TestACDaikinAgent,
                           description='Example VOLTTRON platform™ heartbeat agent',
                           argv=argv)
    except Exception as er:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass