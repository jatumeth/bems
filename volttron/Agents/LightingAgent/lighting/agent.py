# -*- coding: utf-8 -*-
from __future__ import absolute_import


from datetime import datetime
import logging
import sys
import settings
from pprint import pformat

from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import importlib
import random
import json

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Listener Message'
DEFAULT_AGENTID = "listener"
DEFAULT_HEARTBEAT_PERIOD = 5
DEFAULT_MONITORING_TIME = 5

class LightingAgent(Agent):
    """Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    """

    def __init__(self, config_path, **kwargs):
        super(LightingAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self._agent_id = self.config.get('agentid', DEFAULT_AGENTID)
        self._message = self.config.get('message', DEFAULT_MESSAGE)
        self._heartbeat_period = self.config.get('heartbeat_period', DEFAULT_HEARTBEAT_PERIOD)
        self._device_monitor_time = self.config.get('device_monitor_time', DEFAULT_MONITORING_TIME)

        self.model = self.config.get('model')
        self.device_type = self.config.get('type')
        self.url = self.config.get('url')
        self.device = self.config.get('device')

        self.bearer = self.config.get('bearer')
        self.device_id = self.config.get('device_id')


        # TODO get database parameters from settings.py, add db_table for specific table

        print self.device
        print self.url
        print self.bearer

        # 4. @params device_api
        self._api = self.config.get('api')
        print self._api

        self.apiLib = importlib.import_module("DeviceAPI.classAPI." + self._api)

        # 4.1 initialize device object
        self.Light = self.apiLib.API(model=self.model, device_type=self.device_type, agent_id=self.device_id,bearer=self.bearer,device =self.device,url=self.url)

    @Core.periodic(10)
    def deviceMonitorBehavior(self):
        self.Light.getDeviceStatus()

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        # Demonstrate accessing a value from the config file
        _log.info(self.config.get('message', DEFAULT_MESSAGE))
        self._agent_id = self.config.get('agentid')

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        _log.debug("VERSION IS: {}".format(self.core.version()))

    @PubSub.subscribe('pubsub', '/ui/agent/2HUEK/update/bemoss/999/2HUEK1445K1200138')
    def match_device_all2(self, peer, sender, bus, topic, headers, message):
        # print "Headers: {topic}".format(headers=topic)
        print
        print "Headers: {headers}".format(headers=headers)
        print "Message: {message}\n".format(message=message)
        print message
        print type(message)
        # print json.loads(message[0])
        print json.loads(message)
        setDeviceStatusResult = self.Light.setDeviceStatus(json.loads(message))
        # self.vip.pubsub.publish('pubsub', topic, headers, message)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(LightingAgent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
