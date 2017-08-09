# -*- coding: utf-8 -*- {{{
from datetime import datetime
import logging
import sys
import json
import time
import random
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
import time
import json
import settings
utils.setup_logging()
_log = logging.getLogger(__name__)

class ListenerAgent(PublishMixin, BaseAgent):
    # '''Listens to everything and publishes a heartbeat according to the
    # heartbeat period specified in the settings module.
    # '''
    # matching_topic = '/agent/ui/lighting/update_response/bemoss/999/2HUE0017881cab4b'

    def __init__(self, config_path, **kwargs):
        super(ListenerAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self.mode = ''
        self.mode2 = ''
        self.actor = ''


    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        super(ListenerAgent, self).setup()
        self.on_matchmode()

    def main(self):
        print ""

    @periodic(1)
    def on_matchmode(self):
        sbs = ServiceBusService(
            service_namespace='hiveservicebus',
            shared_access_key_name='RootManageSharedAccessKey',
            shared_access_key_value='vZmK7ee4YhIbaUEW5e/sgT0S8JV09LnToCOEqIU+7Qw=')

        '''
        create_queue also supports additional options,
        which enable you to override default queue settings such as message time
        to live (TTL) or maximum queue size. The following example sets t
        he maximum queue size to 5 GB, and the TTL value to 1 minute
        '''
        print "777"
        sbs.create_subscription('tp01', 'client1')


        try:

            print ""
            print("message received!!!")
            msghue = sbs.receive_subscription_message('tp01', 'client1', peek_lock=False)
            print(msghue.body)
            # print type(msg.body)
            self.loadmessagehue = json.loads(msghue.body)
            self.HUE1()
        except:
            print "error11"

    def HUE1(self):
        # TODO this is example how to write an app to control Lighting
        topic = "/ui/agent/lighting/update/bemoss/999/2HUE0017881cab4b"

        print self.loadmessagehue

        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
        }
        message = json.dumps(self.loadmessagehue)
        self.publish(topic, headers, message)
        # print ("HUE turn ON")
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