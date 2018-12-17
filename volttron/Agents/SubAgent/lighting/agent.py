# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import sys
from volttron.platform.vip.agent import Agent, Core, PubSub
from volttron.platform.agent import utils
import importlib
import json


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'

# Step1: Agent Initialization
def lighting_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    model = get_config('model')
    api = get_config('api')
    identifiable = get_config('identifiable')
    # construct _topic_Agent_UI based on data obtained from DB
    topic_device_control = '/agent/zmq/update/hive/provision'
    send_notification = True


    class LightingAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(LightingAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self.model = model
            # initialize device object
            self.apiLib = importlib.import_module("DeviceAPI.classAPI." + api)
            self.Light = self.apiLib.API(model=self.model, agent_id=self._agent_id)
            self.count = None
            self.msg_log = None

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))


        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            # _log.debug("VERSION IS: {}".format(self.core.version()))
            self.count = 0
            self.msg_log = {}

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):

            # self.count += 1
            # # print(str(self.count) + "  From : " + str(json.loads(message)[1]))
            # self.msg_log.update({str(json.loads(message)[1]): str(json.loads(message)[-1])})
            # f = open('./archive.json','w')
            # f.write(json.dumps(self.msg_log, sort_keys=True, indent=4))
            # f.close()
            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)


    Agent.__name__ = '02ORV_InwallLightingAgent'
    return LightingAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(lighting_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
