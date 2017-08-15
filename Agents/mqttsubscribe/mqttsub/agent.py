# -*- coding: utf-8 -*- {{{
from datetime import datetime
import logging
import sys

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
            self.sbs.create_subscription('wemo01', 'client1')
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

    @periodic(1)
    def on_matchmode(self):

        try:
            print("message MQTT received")
            msg = self.sbs.receive_subscription_message('home1', 'client1', peek_lock=False)

            self.commsg = json.loads(msg.body)
            device = str(self.commsg['device'])

            if str(device) == "hue1":  # check if the data is valid
                self.hue()
            elif str(device) == "wemo1":
                self.wemo()

            elif str(device) == "daikin1":
                self.daikin()

            elif str(device) == "fan1":
                self.fan()
            else:
                print "Receiving message not in HiVE IoT Device "
        except:
            print "No MQTT to"
        print "End"

    def hue(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps(self.commsg)
        print type(message)

        self.publish(topic, headers, message)
        print ("topic{}".format(topic))
        print ("message{}".format(message))


    def wemo(self):
        # TODO this is example how to write an app to control Lighting
        topic = '/ui/agent/plugload/update/bemoss/999/3WIS221445K1200321'
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