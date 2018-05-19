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
DEFAULT_AGENTID = "automation"
DEFAULT_HEARTBEAT_PERIOD = 5


def automation_control_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')


    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
<<<<<<< HEAD

    class AutomationAgent(Agent):
=======
    topic_tricker = ''
    conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                            password=db_password)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM automation """)
    rows = cur.fetchall()
    for row in rows:
        if int(automation_id) == int(row[0]):
            triger_device = row[2]
            triger_device_str = ((triger_device).replace("['", '', 1)).replace("']", '', 1)
            topic_tricker = '/agent/zmq/update/hive/999/' + triger_device_str
            print "<<<< subscribe topic >>>>>"
            print topic_tricker

    conn.close()

>>>>>>> ce9e0991d1a8fa92903eaac10eca3e6dba269cc9

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
<<<<<<< HEAD
            print("On Start Event")
=======
            _log.debug("VERSION IS: {}".format(self.core.version()))
            self.load_config()

        @PubSub.subscribe('pubsub', topic_tricker)
        def match_agent_reload(self, peer, sender, bus, topic, headers, message):
            print ">>"
            print ">>"
            print "<<<<<< step 1 subscribe triger >>>>>>>>"
            print "--------------------"
            print(" Automation set device = {}".format(self.triger_device))
            print(" Automation set event = {}".format(self.triger_event))
            print(" Automation set value = {}".format(self.triger_value))
            convert_msg = json.loads(message)
            triger_event_now = convert_msg[self.triger_event]
            print(" value reading now is value = {}".format(convert_msg[self.triger_event]))

            if triger_event_now == self.triger_value:
                print(" Automation set value == value reading now ")
                print(" go to step [[[  2  ]]] check condition event ")
                self.conditionevent()



        def load_config(self): # reload scene configuration to Agent Variable

            conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                    password=db_password)
            self.conn = conn
            self.cur = self.conn.cursor()
            self.cur.execute("""SELECT * FROM automation """)
            rows = self.cur.fetchall()

            for row in rows :
                if int(self.automation_id) == int(row[0]):
                    self.triger_device = row[2]
                    self.triger_event = row[3]
                    self.triger_value = row[4]
                    self.condition_event = row[5]
                    self.condition_value = row[6]
                    self.devicecontrols = (json.loads((row[7])))
                    print(" triger_device = {}".format(self.triger_device))
                    print(" triger_event = {}".format(self.triger_event))
                    print(" triger_value = {}".format(self.triger_value))
                    print(" condition_event  = {}".format(self.condition_event))
                    print(" condition_value = {}".format(self.condition_value))
                    print(" devicecontrols = {}".format(self.devicecontrols))

            self.conn.close()

        def conditionevent(self):
            print ">>"
            print ">>"
            print "<<<<<< step 2 check condition event>>>>>>>>"

            conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                    password=db_password)

            if self.condition_event == 'SCENE':
                self.conn = conn
                self.cur = self.conn.cursor()
                self.cur.execute("""SELECT * FROM active_scene """)
                rows = self.cur.fetchall()
                for row in rows :
                    self.scene_id_now = row[0]
                    self.scene_name_now = row[1]
                    print(" condition now = {}".format(self.scene_name_now))
                    print(" condition in automation seting  = {}".format(self.scene_name_now))

                    if str(self.condition_value) == str(self.scene_name_now):
                        print '>> condition value == condition now'
                        print(" go to step [[[  3  ]]] device control ")
                        self.devicecontrol()
                    else:
                        print '>> condition value != condition now'
                        print ""
                        print(" go to step [[[  1  ]]] for subscribe triger")
                        print ""

            self.conn.close()


        def devicecontrol(self):
            print ">>"
            print ">>"
            print "<<<<<<step 3 device control >>>>>>>>"
            try:
                for task in self.devicecontrols:
                    topic = str('/ui/agent/update/hive/999/') + str(task['device_id'])
                    print topic
                    message = json.dumps(task['command'])
                    print ("topic {}".format(topic))
                    print ("message {} \n".format(message))
                    self.vip.pubsub.publish(
                        'pubsub', topic,
                        {'Type': 'HiVE Scene Control'}, message)
            except Exception as Error:
                print('Reload Config to Agent')
>>>>>>> ce9e0991d1a8fa92903eaac10eca3e6dba269cc9

        @Core.periodic(5)
        def alive_agent(self):
            print("I'm a new born agent")


    Agent.__name__ = 'AutomationAgent'
    return automation_control_agent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''

    try:
        utils.vip_main(automation_control_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
