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
import socket
import psycopg2
import psycopg2.extras
import pyrebase
import pprint
import psycopg2
import sys

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_HEARTBEAT_PERIOD = 20
DEFAULT_MONITORING_TIME = 20
DEFAULT_MESSAGE = 'HELLO'


# Step1: Agent Initialization
def scenesetup_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # List of all keywords for a scenesetup agent
    agentAPImapping = dict(status=[], brightness=[], color=[], saturation=[], power=[])
    log_variables = dict(status='text', brightness='double', hexcolor='text', power='double', offline_count='int')

    agent_id = get_config('agent_id')

    topic_device_control = '/ui/agent/update/hive/999/scenceagent'
    print(topic_device_control)

    class scenesetupAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(scenesetupAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id

            # initialize device object
        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))

        @Core.periodic(10)
        def deviceMonitorBehavior(self):
            print "scene setup agent is running."

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):

            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)

            msg = json.loads(message)
            scene = str(msg['scene_name'])
            
            db_database = 'hivedb'
            db_host = 'localhost'
            db_port = '5432'
            db_user = 'hiveadmin'
            db_password = 'hiveadmin'
            
            conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                    password=db_password)
            cur = conn.cursor()
            cur.execute("SELECT * FROM scenceappagent WHERE scence = %s", (scene,))
            # cur.execute("""SELECT * from sceneappagent WHERE scence = scene""")
            scene = cur.fetchone()[2]
            scene_conve = list(scene)

            for i in range(len(scene_conve)):
                print(scene_conve[i])
                device = str(scene_conve[i]['device_id'])
                command = scene_conve[i]['command']
                print device
                print command

                topic = str('/ui/agent/update/hive/999/'+device)
                message = json.dumps(command)
                # message = json.dumps({"status": "OFF", "device": "2HUEK1445K1200138"})
                print ("topic {}".format(topic))
                print ("message {}".format(message))

                self.vip.pubsub.publish(
                    'pubsub', topic,
                    {'Type': 'HiVE App to Gateway'}, message)


    Agent.__name__ = 'scenesetupAgent'
    return scenesetupAgent(config_path, **kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(scenesetup_agent, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')

if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
