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

publish_periodic = 10

class ModeAppAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    def __init__(self, config_path, **kwargs):
        super(ModeAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(ModeAppAgent, self).setup()

    # @matching.match_all
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    @matching.match_exact("/ui/agent/select_mode/")
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        _log.debug("Topic: {topic}, Headers: {headers}, "
                         "Message: {message}".format(
                         topic=topic, headers=headers, message=message))
        print "Topic: {}".format(topic)
        print "Headers: {}".format(headers)
        # print "Message: {}".format(message)
        received_message = json.loads(message[0])
        print received_message
        self.home_mode = received_message['mode']
        self.publish_heartbeat()
        print"---------------------------------------------------"

    # Demonstrate periodic decorator and settings access

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
            'data_source': "modeApp",
        }

        # home_mode = ["DR", "ECO", "COMFORT"]
        try:
            # TODO fix rebate and eco saving
            DR_rebate_price = 8.00
            ECO_saving_cost = round(random.uniform(1.00, 50.00), 2)
            print self.home_mode.upper()
            message = json.dumps({"home_mode": self.home_mode.upper(),
                                  "DR_rebate_price": DR_rebate_price,
                                  "ECO_saving_cost": ECO_saving_cost})
            self.publish(topic, headers, message)
            print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)
        except:
            print "home_mode has not been set yet"

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(ModeAppAgent,
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
