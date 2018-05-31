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
import json
from pprint import pformat
import subprocess as sp
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import psycopg2
from os.path import expanduser


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Automation Message'
DEFAULT_AGENTID = "automation_control"
DEFAULT_HEARTBEAT_PERIOD = 5


def automation_manager_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    topic_automation_create = '/ui/agent/update/hive/999/automationcreate'
    topic_automation_delete = '/ui/agent/update/hive/999/automationdelete'
    topic_automation_update = '/ui/agent/update/hive/999/automationupdate'
    topic_update_agent = 'agent/update/hive/999/updateagent'

    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class AutomationAgent(Agent):

        def __init__(self, config_path, **kwargs):
            super(AutomationAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = self.config.get('agentid', DEFAULT_AGENTID)
            self._message = self.config.get('message', DEFAULT_MESSAGE)
            self._heartbeat_period = self.config.get('heartbeat_period',
                                                     DEFAULT_HEARTBEAT_PERIOD)
            self.conn = None
            self.cur = None
            self.automation_control_path = None

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            print('on-setup event occur')

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            print("On Start Event")
            # self.build_automation_agent(55)  #  Uncomment for Test Create new agent event
            # self.publish_agentupdate_topic()

        @PubSub.subscribe('pubsub', topic_automation_create)  # On Automation create
        def match_topic_create(self, peer, sender, bus,  topic, headers, message):
            print("Match Topic Create Automation")
            msg = json.loads(message)
            conf = msg.get('automationconfig', None)
            self.insertdb(conf)
            self.build_automation_agent(automation_id=str(conf.get('automation_id')))
            self.publish_agentupdate_topic()  # Pub Message to HiVEPlatfom Agent

        @PubSub.subscribe('pubsub', topic_automation_delete)  # On Automation delete
        def match_topic_delete(self, peer, sender, bus,  topic, headers, message):
            print("Match Topic Delete Automation")
            msg = json.loads(message)
            conf = msg.get('automationconfig', None)
            self.deletedb(conf)
            self.remove_automation_agent(conf.get('automation_id'))
            self.publish_agentupdate_topic()  # Pub Message to HiVEPlatfom Agent

        @PubSub.subscribe('pubsub', topic_automation_update)
        def match_topic_update(self, peer, sender, bus,  topic, headers, message):
            print("Match Topic Update Automation")
            msg = json.loads(message)
            conf = msg.get('automationconfig', None)
            automation_id = conf.get('automation_id')
            self.updatedb(conf)
            self.remove_automation_agent(automation_id)
            self.build_automation_agent(automation_id)
            self.publish_agentupdate_topic()  # Pub Message to HiVEPlatfom Agent

        def updatedb(self, conf):
            if conf is not None:
                # Update Record Attibute where match automation ID
                automation_id = str(conf.get('automation_id'))
                automation_name = conf.get('automation_name')
                condition_event = conf.get('condition_event')
                condition_value = conf.get('condition_value')
                trigger_device = conf.get('trigger_device')
                trigger_event = conf.get('trigger_event')
                trigger_value = conf.get('trigger_value')
                action_tasks = conf.get('action_tasks')

                self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                             user=db_user, password=db_password)
                self.cur = self.conn.cursor()
                self.cur.execute("""UPDATE automation SET automation_name=%s,
                                    condition_event=%s, condition_value=%s,
                                    trigger_device=%s, trigger_event=%s,
                                    trigger_value=%s, action_tasks=%s
                                    WHERE automation_id=%s;""", (automation_name, condition_event,
                                                                 condition_value, trigger_device,
                                                                 trigger_event, trigger_value,
                                                                 action_tasks, automation_id))

                self.conn.commit()
                self.conn.close()

        def deletedb(self, conf):
            if conf is not None:
                # Delete Record where match automation ID
                self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                             user=db_user, password=db_password)
                self.cur = self.conn.cursor()
                self.cur.execute("""DELETE FROM automation 
                                    WHERE automation_id ={};""".format(conf.get('automation_id')))
                self.conn.commit()
                self.conn.close()

            else:
                pass

        def insertdb(self, conf):

            if conf is not None :
                # 1.Unpack Message from Backend
                automation_id = str(conf.get('automation_id'))
                automation_name = conf.get('automation_name')
                condition_event = conf.get('condition_event')
                condition_value = conf.get('condition_value')
                trigger_device = conf.get('trigger_device')
                trigger_event = conf.get('trigger_event')
                trigger_value = conf.get('trigger_value')
                action_tasks = conf.get('action_tasks')

                self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                             user=db_user, password=db_password)

                self.cur = self.conn.cursor()
                self.cur.execute(
                    """INSERT INTO automation (automation_id, automation_name, condition_event, 
                                                condition_value, trigger_device, trigger_event, 
                                                trigger_value, action_tasks) 
                                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                    (automation_id, automation_name, condition_event, condition_value,
                     trigger_device, trigger_event, trigger_value, action_tasks))

                self.conn.commit()
                self.conn.close()

            else:
                pass

        def publish_agentupdate_topic(self):  # Pub Message to HiVEPlatform Agent
            msg = {}
            print("New Agent Registered")
            self.vip.pubsub.publish('pubsub', topic_update_agent, message=msg)

        def build_automation_agent(self, automation_id):
            print(' >>> Build Agent Process')
            #  get PATH Environment
            home_path = expanduser("~")
            json_path = '/workspace/hive_os/volttron/Agents/AutomationControlAgent/automationcontrolagent.launch.json'
            self.automation_control_path = home_path+json_path
            launcher = json.load(open(home_path + json_path, 'r'))  # load config.json to variable
            #  Update new agentID to variable (agentID is relate to automation_id)
            launcher.update({'agentid': 'automation_{}'.format(automation_id)})
            #  dump new config to file
            json.dump(launcher, open(home_path + json_path, 'w'), sort_keys=True, indent=4)
            print(" >>> Change config file successful")

            os.system("volttron-pkg package Agents/AutomationControlAgent;" +
                      "volttron-pkg configure ~/.volttron/packaged/automation_controlagent-3.2-py2-none-any.whl" +
                      " ~/workspace/hive_os/volttron/Agents/AutomationControlAgent/automationcontrolagent.launch.json" +
                      ";volttron-ctl install " +
                      "~/.volttron/packaged/automation_controlagent-3.2-py2-none-any.whl " +
                      "--tag automation_{}".format(automation_id) +
                      ";volttron-ctl start --tag automation_{}".format(automation_id))

        def remove_automation_agent(self, automation_id):
            print("check status automation agent")
            os.system("volttron-ctl stop --tag automation_{}".format(automation_id))
            os.system("volttron-ctl remove --tag automation_{}".format(automation_id))
            self.automation_control_path = None

    Agent.__name__ = 'automationmanager'
    return AutomationAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''

    try:
        utils.vip_main(automation_manager_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
