# -*- coding: utf-8 -*-

from __future__ import absolute_import

from datetime import datetime
import logging
import sys
import settings
from pprint import pformat
import subprocess as sp
import os
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'HiVE Platform Message'
DEFAULT_AGENTID = "hive.platform.agent"
DEFAULT_HEARTBEAT_PERIOD = 5


# Step1: Agent Initialization
def hiveplatform_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    topic_scenecontrol = '/ui/agent/update/hive/999/scenecontrol'
    topic_agent_reload = '/agent/update/hive/999/reload'
    topic_token_reload = '/ui/agent/update/hive/999/login'

    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class HiVEPlatformAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(HiVEPlatformAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = self.config.get('agentid', DEFAULT_AGENTID)
            self._message = self.config.get('message', DEFAULT_MESSAGE)
            self._heartbeat_period = self.config.get('heartbeat_period',
                                                     DEFAULT_HEARTBEAT_PERIOD)
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
            if self._heartbeat_period != 0:  # ON Start Event enable Agent's Heartbeat
                self.vip.heartbeat.start_with_period(self._heartbeat_period)
                self.vip.health.set_status(STATUS_GOOD, self._message)

        @Core.periodic(30)
        def check_status_agent(self):
            out = sp.check_output('volttron-ctl status', shell=True)
            status = out.split('\n')
            status = status[0:-1]  # Remove '' After split('\n') at end of list
            for row in status:
                if row.find('running') == -1:  # Agent not running condition
                    if row.split(' ')[-1] != '0':
                        # Agent Dead Found Here
                        uuid = row.split(' ')[0]
                        os.system('volttron-ctl restart {}'.format(uuid))
                        print('Restart Agent : {}'.format(row.split(' ')[3])) # Index 3 is a TAG of Agent
                        _log.info('Auto Restart Agent {}'.format(row.split(' ')[3]))

                    elif row.split(' ')[-1] == '0':
                        # Agent Not Start Found Here
                        print('Agent {} not running'.format(row.split(' ')[3]))
                        pass

                else:
                    # Agent run normaly Found Here
                    print('Agent {} is Running'.format(row.split(' ')[3]))

    Agent.__name__ = 'hiveplatformAgent'
    return HiVEPlatformAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(hiveplatform_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
