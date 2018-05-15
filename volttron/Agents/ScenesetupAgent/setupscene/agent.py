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
def scencesetup_agent(config_path, **kwargs):
    config = utils.load_config(config_path)
    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # List of all keywords for a scencesetup agent
    agentAPImapping = dict(status=[], brightness=[], color=[], saturation=[], power=[])
    log_variables = dict(status='text', brightness='double', hexcolor='text', power='double', offline_count='int')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_monitor_time = config.get('device_monitor_time', DEFAULT_MONITORING_TIME)
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    if model == "Philips hue bridge":
        hue_username = get_config('username')
    else:
        hue_username = ''
    device_type = get_config('type')
    device = get_config('device')
    bearer = get_config('bearer')
    url = get_config('url')
    api = get_config('api')
    address = get_config('ipaddress')
    _address = address.replace('http://', '')
    _address = address.replace('https://', '')
    try:  # validate whether or not address is an ip address
        socket.inet_aton(_address)
        ip_address = _address
    except socket.error:
        ip_address = None
    identifiable = get_config('identifiable')

    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id

    topic_device_control = '/ui/agent/update/hive/999/scenesetup'
    topic_agent_reload = '/agent/update/hive/999/reload'
    print(topic_device_control)
    gateway_id = 'hivecdf12345'

    # 5. @params notification_info
    send_notification = True

    class scencesetupAgent(Agent):
        """Listens to everything and publishes a heartbeat according to the
        heartbeat period specified in the settings module.
        """

        def __init__(self, config_path, **kwargs):
            super(scencesetupAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self._message = message
            self._heartbeat_period = heartbeat_period
            self.conn = None
            self.cur = None

            # initialize device object
        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            _log.debug("VERSION IS: {}".format(self.core.version()))

        @Core.periodic(device_monitor_time)
        def deviceMonitorBehavior(self):
            print "Scence setup agent is running."

        @PubSub.subscribe('pubsub', topic_device_control)
        def match_device_control(self, peer, sender, bus, topic, headers, message):
            print('Message incoming')
            # if topic == topic_device_control:

            db_database = 'hivedb'
            db_host = '127.0.0.1'
            db_port = '5432'
            db_user = 'admin'
            db_password = 'admin'
            message_load = json.loads(message)
            sceneconfig = message_load.get('sceneconfig')
            type_msg = message_load.get('type', None)
            scene_name = sceneconfig.get('scene_name')
            msg = sceneconfig.get('scene_tasks')
            scene_id = sceneconfig.get('scene_id')
            print(type_msg)
            self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                         user=db_user, password=db_password)

            self.cur = self.conn.cursor()
            if type_msg == 'sceneupdate':
                self.cur.execute("""SELECT * from scene""")
                rows = self.cur.fetchall()
                scene_id_set = set()

                for row in rows:
                    scene_id_set.add(str(row[0]))

                if set({str(scene_id)}).issubset(scene_id_set):
                    self.updatedb(scene_id, scene_name, scene_task=msg)

                else:
                    self.insertdb(scene_id, scene_name, scene_task=msg)

            elif type_msg == 'scenecreate':
                self.insertdb(scene_id, scene_name, scene_task=msg)

            elif type_msg == 'scenedelete':
                print(" >>> Delete Scene Function Executed")
                self.deletedb(scene_id)

        def deletedb(self, scene_id):
            print 'Delete Scene id : {}'.format(scene_id)
            scene_id = str(scene_id)
            self.cur.execute("DELETE FROM scene WHERE scene_id ='{}'".format(scene_id))

            self.conn.commit()
            self.conn.close()

            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                                    {'Type': 'HiVE Scene Control'}, None)

        def updatedb(self, scene_id, scene_name, scene_task):
            print 'Update Scene id : {}'.format(scene_id)
            task = json.dumps(scene_task)
            self.cur.execute("""UPDATE scene SET scene_name=%s, scene_task=%s WHERE scene_id=%s""",
                            (scene_name, task, str(scene_id)))

            self.conn.commit()
            self.conn.close()

            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)

        def insertdb(self, scene_id, scene_name, scene_task):
            print 'Insert Scene id : {}'.format(scene_id)
            tasks = json.dumps(scene_task)
            self.cur = self.conn.cursor()
            self.cur.execute(
                """INSERT INTO scene (scene_id, scene_name, scene_task) VALUES (%s, %s, %s);""",
                (scene_id, scene_name, tasks))
            self.conn.commit()
            self.conn.close()
            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)

    Agent.__name__ = 'scencesetupAgent'
    return scencesetupAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''

    try:
        utils.vip_main(scencesetup_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
