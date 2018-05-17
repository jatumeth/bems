# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}

from __future__ import absolute_import

from datetime import datetime
import logging
import sys
import settings
import os
from pprint import pformat
import subprocess as sp
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Automation Message'
DEFAULT_AGENTID = "automation_control"
DEFAULT_HEARTBEAT_PERIOD = 5


# def automation_manager_agent(config_path, **kwargs):
#     config = utils.load_config(config_path)
#
#     def get_config(name):
#         try:
#             kwargs.pop(name)
#         except KeyError:
#             return config.get(name, '')
#
#     agent_id = get_config('agent_id')
#     message = get_config('message')
#     heartbeat_period = get_config('heartbeat_period')
#     topic_automation_create = '/ui/agent/update/hive/999/automation_control'


    # # DATABASES
    # db_host = settings.DATABASES['default']['HOST']
    # db_port = settings.DATABASES['default']['PORT']
    # db_database = settings.DATABASES['default']['NAME']
    # db_user = settings.DATABASES['default']['USER']
    # db_password = settings.DATABASES['default']['PASSWORD']

class AutomationAgent(Agent):

    def __init__(self, config_path, **kwargs):
        super(AutomationAgent, self).__init__(**kwargs)
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
        print('on-setup event occur')

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        print("On Start Event")
        self.build_automation_agent(config_param=None)

    # @PubSub.subscribe('pubsub', topic_automation_create)
    # def on_match(self, peer, sender, bus,  topic, headers, message):
    #     print("Match Topic")
    #     # Fake message for new born agent
    #     message = {'automation_id': '1',
    #                'automation_name': 'rule_1',
    #                'conditon': [{'multisensor': {'status': 'active'}},
    #                             {'scene':{'scene_name': 'Good Morning'}}],
    #                'trigger': [{'doorlock': {'status': 'unlock'}}]
    #                }
    #     # newborn_agent_id = self.build_automation_agent(message)  # Compatible with argument dict format

    def build_automation_agent(self, config_param):
        print(' >>> Build Agent Process')
        os.system("volttron-pkg package Agents/AutomationControlAgent;" +
                  "volttron-pkg configure ~/.volttron/packaged/automationagent-3.2-py2-none-any.whl" +
                  "~/workspace/hive_os/volttron/Agents/AutomationControlAgent/automationcontrolagent.launch.json" +
                  ";volttron-ctl install " +
                  "~/.volttron/packaged/automationagent-3.2-py2-none-any.whl --tag automation_01")

    # Agent.__name__ = 'automation_manager_agent'
    # return automation_manager_agent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''

    try:
        utils.vip_main(AutomationAgent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
