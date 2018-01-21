# -*- coding: utf-8 -*- {{{
from datetime import datetime
import logging
import sys
import time
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
import json
utils.setup_logging()
_log = logging.getLogger(__name__)


class ListenerAgent(PublishMixin, BaseAgent):
    def __init__(self, config_path, **kwargs):
        super(ListenerAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self.mode = ''
        self.mode2 = ''
        self.actor = ''
        try:
            self.sbs = ServiceBusService(
                service_namespace='hiveservicebus',
                shared_access_key_name='RootManageSharedAccessKey',
                shared_access_key_value='vZmK7ee4YhIbaUEW5e/sgT0S8JV09LnToCOEqIU+7Qw=')
            self.sbs.create_subscription('tp01', 'client1')
            self.sbs.create_subscription('wemo1', 'client1')
            self.sbs.create_subscription('hue1', 'client1')
            self.sbs.create_subscription('fan1', 'client1')
            self.sbs.create_subscription('daikin1', 'client1')
            self.sbs.create_subscription('saijo1', 'client1')
            self.sbs.create_subscription('saijo2', 'client1')
            self.sbs.create_subscription('saijo3', 'client1')
        except:
            print ""

    def setup(self):
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        super(ListenerAgent, self).setup()
        self.on_matchmode()

    def main(self):
        print ""

    @periodic(20)
    def on_matchmode(self):
        self.wemo_on()
        time.sleep(10)
        self.wemo_off()
        time.sleep(10)
        self.wemo_on()
        time.sleep(10)
        self.wemo_off()
        #
        # self.hue_min()
        # time.sleep(5)
        # self.hue_max()
        # time.sleep(5)
        # self.hue_min()
        # time.sleep(5)
        # self.hue_max()

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
        print ("HUE max")

    def hue_min(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF", "brightness": 5})
        self.publish(topic, headers, message)
        print ("HUE min")


    def wemo_on(self):
        # TODO this is example how to write an app to control plugload EV
        topic = "/ui/agent/1SAJ1/update/bemoss/999/1SAJ1000000000001"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "ON"})
        self.publish(topic, headers, message)
        print ("plug EV turn ON")

    def wemo_off(self):
        # TODO this is example how to write an app to control plugload EV
        topic = "/ui/agent/1SAJ1/update/bemoss/999/1SAJ1000000000001"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps({"status": "OFF"})
        self.publish(topic, headers, message)
        print ("plug EV turn OFF")

    def daikin(self):
        # TODO this is example how to write an app to control Lighting
        topic = '/ui/agent/AC/update/bemoss/999/ACD1200138'
        # {"status": "OFF"}
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps(self.commsg)
        self.publish(topic, headers, message)
        print ("topic{}".format(topic))
        print ("message{}".format(message))

    def fan(self):
        # TODO this is example how to write an app to control Lighting
        topic = '/ui/agent/fan/update/bemoss/999/1FN221445K1200138'
        # {"status": "OFF"}
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps(self.commsg)
        self.publish(topic, headers, message)
        print ("topic{}".format(topic))
        print ("message{}".format(message))

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