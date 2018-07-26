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
import requests
import socket
import psycopg2
import psycopg2.extras
import pyrebase
import pprint
import psycopg2
import sys

from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'


# Step1: Agent Initialization
def notifier_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    topic_update_token = '/ui/agent/update/notifier'
    topic_device_notify = '/agent/update/hive/999/devicealeart/'

    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class NotifierAgent(Agent):

        def __init__(self, config_path, **kwargs):
            super(NotifierAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self.conn = None
            self.cur = None
            self.expo_token = self.config.get('noti_token', '')
            self.token = self.config.get('token')
            self.endpoint_expo = self.config.get('endpoint_expo')
            self.url = self.config.get('backend_url') + self.config.get('notify_api')
            self._message = self.config.get('message', DEFAULT_MESSAGE)
            self._heartbeat_period = self.config.get('heartbeat_period',
                                                     DEFAULT_HEARTBEAT_PERIOD)
            self.acknowlage = None
            _log.info("init attribute to Agent")

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self._agent_id = self.config.get('agentid')

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            if self._heartbeat_period != 0:
                self.vip.heartbeat.start_with_period(self._heartbeat_period)
                self.vip.health.set_status(STATUS_GOOD, self._message)

            # # TODO : Stuff for pre config
            # if self.expo_token == '':
            #     self.get_expo_token()  # First Agent Started it need Expo Token for Push NotiFy Services
            #
            # else:
            #     pass

        @PubSub.subscribe('pubsub', topic_device_notify)
        def match_device_alert(self, peer, sender, bus, topic, headers, message):
            print("Aleart Event on Device Occur")
            #  TODO : make a request for notification here. {Hint : Use Expo Token to identity mobile devices}
            msg = json.loads(message)

            try:
                response = self.send_push_message(token=msg.get('noti_token'), message=msg.get('message'))
                if response.status == u'ok':
                    # Pub topic acknowlage notification
                    self.vip.pubsub.publish('pubsub', topic='agent/update/notified/'+msg.get('sender'))

            except Exception as Err :
                print('Error : {}'.format(Err))

        @PubSub.subscribe('pubsub', topic_update_token)  # This topic match when mobile user logged-in
        def match_token_reload(self, peer, sender, bus, topic, headers, message):
            print('Message Recived')
            print(' >>> Reload Token')
            msg = json.loads(message)
            new_token = msg.get('token', None)
            expo_token = msg.get('noti_token', None)

            self.config.update({'token': new_token,
                                'noti_token': expo_token})
            config_dict = self.config
            json.dump(config_dict, open(config_path, 'w'), sort_keys=True, indent=4)

        # Expo and Login Token is update when Mobile User logged-in
        # Function to Handle expo notification
        def send_push_message(self, token, message, extra=None):
            try:
                response = PushClient().publish(
                    PushMessage(to=token,
                                body=message,
                                data=extra))
                if response.status == u'ok':
                    print('Notification Complete')
                    # TODO :  Make a Acknownlage Routine
                    self.acknowlage = True

            except PushServerError as exc:
                # Encountered some likely formatting/validation error.
                print(exc)
                # TODO : Handle Push Server Error

            except (ConnectionError, HTTPError) as exc:
                # Encountered some Connection or HTTP error - retry a few times in
                print(exc)
                # TODO : Handle Connection Error

            return response

    Agent.__name__ = 'notifierAgent'
    return NotifierAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(notifier_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
