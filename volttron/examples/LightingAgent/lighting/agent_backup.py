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

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Listener Message'
DEFAULT_AGENTID = "listener"
DEFAULT_HEARTBEAT_PERIOD = 5
DEFAULT_MONITORING_TIME = 5
oat_point = 'devices/Building/LAB/Device/OutsideAirTemperature'
all_topic = 'devices/Building/LAB/Device/all'

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
        self._building_name = self.config.get('building_name')
        self._zone_id = self.config.get('zone_id')

        # TODO get database parameters from settings.py, add db_table for specific table


        # 4. @params device_api
        self._api = self.config.get('api')
        self.apiLib = importlib.import_module("DeviceAPI.classAPI." + self._api)

        # 4.1 initialize device object
        self.Light = self.apiLib.API(model='RelaySW', type='tv', api='API3', agent_id='RelaySWAgent',
                  url='https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/314fe2f7-1724-42ed-86b6-4a8c03a08601/switches/',
                  bearer='Bearer ebb37dd7-d048-4cf6-bc41-1fbe9f510ea7', device='b51760e0-35b2-4b69-ab67-a36621f12f08')
        # print("{0}agent is initialized for {1} using API={2} at {3}".format(self._agent_id, Light.get_variable('model'),
        #                                                                     Light.get_variable('api'),
        #                                                                     Light.get_variable('address')))

        try:
            self._heartbeat_period = int(self._heartbeat_period)
        except:
            _log.warn('Invalid heartbeat period specified setting to default')
            self._heartbeat_period = DEFAULT_HEARTBEAT_PERIOD
        log_level = self.config.get('log-level', 'INFO')
        if log_level == 'ERROR':
            self._logfn = _log.error
        elif log_level == 'WARN':
            self._logfn = _log.warn
        elif log_level == 'DEBUG':
            self._logfn = _log.debug
        else:
            self._logfn = _log.info

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        # Demonstrate accessing a value from the config file
        _log.info(self.config.get('message', DEFAULT_MESSAGE))
        self._agent_id = self.config.get('agentid')

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        _log.debug("VERSION IS: {}".format(self.core.version()))
        # if self._heartbeat_period != 0:
        #     self.vip.heartbeat.start_with_period(self._heartbeat_period)
        #     self.vip.health.set_status(STATUS_GOOD, self._message)
        # self.vip.pubsub.publish(peer='pubsub', topic='test2gfdgdgd', headers={'a':1},
        #                         message={'b':2}).get(timeout=5)

    @PubSub.subscribe('pubsub', 'test')
    def on_match(self, peer, sender, bus,  topic, headers, message):
        """Use match_all to receive all messages and print them out."""
        print('on_match')
        print(sender)
        print(topic)
        print(headers)
        print(message)
        # if sender == 'pubsub.compat':
        #     message = compat.unpack_legacy_message(headers, message)
        # self._logfn(
        #     "Peer: %r, Sender: %r:, Bus: %r, Topic: %r, Headers: %r, "
        #     "Message: \n%s", peer, sender, bus, topic, headers,  pformat(message))

    @PubSub.subscribe('pubsub', 'test2')
    def on_match2(self, peer, sender, bus,  topic, headers, message):
        """Use match_all to receive all messages and print them out."""
        print('on_match2')
        print(sender)
        print(topic)
        print(headers)
        print(message)
        # if sender == 'pubsub.compat':
        #     message = compat.unpack_legacy_message(headers, message)
        # self._logfn(
        #     "Peer: %r, Sender: %r:, Bus: %r, Topic: %r, Headers: %r, "
        #     "Message: \n%s", peer, sender, bus, topic, headers,  pformat(message))

    @PubSub.subscribe('pubsub', all_topic)
    def match_device_all(self, peer, sender, bus, topic, headers, message):
        '''
        This method subscribes to all points under a device then pulls out
        the specific point it needs.
        The first element of the list in message is a dictionairy of points
        under the device. The second element is a dictionary of metadata for points.
        '''
        print("device_all")
        # print("Whole message", message)
        #
        # # The time stamp is in the headers
        # print('Date', headers['Date'])
        #
        # # Pull out the value for the point of interest
        # print("Value", message[0]['OutsideAirTemperature'])
        #
        # # Pull out the metadata for the point
        # print('Unit', message[1]['OutsideAirTemperature']['units'])
        # print('Timezone', message[1]['OutsideAirTemperature']['tz'])
        # print('Type', message[1]['OutsideAirTemperature']['type'])

    @PubSub.subscribe('pubsub', oat_point)
    def on_match_OAT(self, peer, sender, bus, topic, headers, message):
        '''
        This method subscribes to the specific point topic.
        For these topics, the value is the first element of the list
        in message.
        '''
        print("OAT")
        # print("Whole message", message)
        # print('Date', headers['Date'])
        # print("Value", message[0])
        # print("Units", message[1]['units'])
        # print("TimeZone", message[1]['tz'])
        # print("Type", message[1]['type'])

    @Core.periodic(50)
    def deviceMonitorBehavior(self):
        # try:
            self.Light.getDeviceStatus()

            self.vip.pubsub.publish(peer='pubsub', topic='test2gfdgdgd', headers={'a': 1},
                                    message={'b': 2}).get(timeout=5)
        # except Exception as er:
        #     print("device connection is not successful {}".format(er))

    @Core.periodic(10)
    def pub_fake_data(self):
        ''' This method publishes fake data for use by the rest of the agent.
        The format mimics the format used by VOLTTRON drivers.

        This method can be removed if you have real data to work against.
        '''

        # Make some random readings
        oat_reading = random.uniform(30, 100)
        mixed_reading = oat_reading + random.uniform(-5, 5)
        damper_reading = random.uniform(0, 100)

        # Create a message for all points.
        all_message = [{'OutsideAirTemperature': oat_reading, 'MixedAirTemperature': mixed_reading,
                        'DamperSignal': damper_reading},
                       {'OutsideAirTemperature': {'units': 'F', 'tz': 'UTC', 'type': 'float'},
                        'MixedAirTemperature': {'units': 'F', 'tz': 'UTC', 'type': 'float'},
                        'DamperSignal': {'units': '%', 'tz': 'UTC', 'type': 'float'}
                        }]

        # Create messages for specific points
        oat_message = [oat_reading, {'units': 'F', 'tz': 'UTC', 'type': 'float'}]
        mixed_message = [mixed_reading, {'units': 'F', 'tz': 'UTC', 'type': 'float'}]
        damper_message = [damper_reading, {'units': '%', 'tz': 'UTC', 'type': 'float'}]

        # Create timestamp
        now = datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            headers_mod.DATE: now
        }

        # # Publish messages
        self.vip.pubsub.publish(
            'pubsub', all_topic, headers, all_message)

        self.vip.pubsub.publish(
            'pubsub', oat_point, headers, oat_message)

        # self.vip.pubsub.publish(
        #     'pubsub', mixed_point, headers, mixed_message)
        #
        # self.vip.pubsub.publish(
        #     'pubsub', damper_point, headers, damper_message)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(LightingAgent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
