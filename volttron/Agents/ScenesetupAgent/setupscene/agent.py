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
import json
import sys
import sqlite3
from os.path import expanduser

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

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    topic_scene_create = '/ui/agent/update/hive/999/scenecreate'
    topic_scene_update = '/ui/agent/update/hive/999/sceneupdate'
    topic_scene_delete = '/ui/agent/update/hive/999/scenedelete'
    topic_agent_reload = '/agent/update/hive/999/reload'

    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class scencesetupAgent(Agent):

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
        @PubSub.subscribe('pubsub', topic_scene_create)
        def match_scene_create(self, peer, sender, bus, topic, headers, message):
            print('Message incoming')
            message_load = json.loads(message)
            sceneconfig = message_load.get('sceneconfig')
            type_msg = message_load.get('type', None)
            scene_name = sceneconfig.get('scene_name')
            msg = sceneconfig.get('scene_tasks')
            scene_id = sceneconfig.get('scene_id')
            print(type_msg)
            # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                              user=db_user, password=db_password)
            # self.insertdb(scene_id, scene_name, scene_tasks=msg)

            self.insertsqlite(scene_id, scene_name, scene_tasks=msg)

        @PubSub.subscribe('pubsub', topic_scene_update)
        def match_scene_update(self, peer, sender, bus, topic, headers, message):
            print('Message incoming')
            # message_load = json.loads(message)
            # sceneconfig = message_load.get('sceneconfig')
            # type_msg = message_load.get('type', None)
            # scene_name = sceneconfig.get('scene_name')
            # msg = sceneconfig.get('scene_tasks')
            # scene_id = sceneconfig.get('scene_id')
            # print(type_msg)
            # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                              user=db_user, password=db_password)
            #
            # self.cur = self.conn.cursor()
            # self.cur.execute("""SELECT * from scenes""")
            # rows = self.cur.fetchall()
            # scene_id_set = set()
            # for row in rows:
            #     scene_id_set.add(str(row[0]))
            #
            # if set({str(scene_id)}).issubset(scene_id_set):
            #     convertmsg = json.loads(msg)
            #     self.updatedb(scene_id, scene_name, scene_tasks=convertmsg)
            #
            # else:
            #     self.insertdb(scene_id, scene_name, scene_tasks=msg)

        @PubSub.subscribe('pubsub', topic_scene_update)
        def match_scene_updatesql(self, peer, sender, bus, topic, headers, message):
            print('Message incoming')
            message_load = json.loads(message)
            sceneconfig = message_load.get('sceneconfig')
            type_msg = message_load.get('type', None)
            scene_name = sceneconfig.get('scene_name')
            msg = sceneconfig.get('scene_tasks')
            scene_id = sceneconfig.get('scene_id')
            print(type_msg)


            gg = expanduser("~")
            path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            conn = sqlite3.connect(gg + path)
            cur = conn.cursor()
            cur.execute("""SELECT * FROM scenes """)
            rows = cur.fetchall()
            scene_id_set = set()
            for row in rows:
                scene_id_set.add(str(row[0]))

            if set({str(scene_id)}).issubset(scene_id_set):
                convertmsg = json.loads(msg)
                self.updatesqlite(scene_id, scene_name, scene_tasks=convertmsg)

            else:
                self.insertsqlite(scene_id, scene_name, scene_tasks=msg)

        @PubSub.subscribe('pubsub', topic_scene_delete)
        def match_scene_delete(self, peer, sender, bus, topic, headers, message):
            print('Message incoming')
            # message_load = json.loads(message)
            # sceneconfig = message_load.get('sceneconfig')
            # type_msg = message_load.get('type', None)
            # scene_name = sceneconfig.get('scene_name')
            # msg = sceneconfig.get('scene_tasks')
            # scene_id = sceneconfig.get('scene_id')
            # print(type_msg)
            # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                              user=db_user, password=db_password)
            # print(" >>> Delete Scene Function Executed")
            # self.deletedb(scene_id)
            # self.deletesqlite(scene_id)

        def deletedb(self, scene_id):
            print 'Delete Scene id : {}'.format(scene_id)
            scene_id = str(scene_id)
            self.cur.execute("DELETE FROM scene WHERE scene_id ='{}'".format(scene_id))

            self.conn.commit()
            self.conn.close()

            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                                    {'Type': 'HiVE Scene Control'}, None)

        def updatedb(self, scene_id, scene_name, scene_tasks):
            print 'Update Scene id : {}'.format(scene_id)
            task = json.dumps(scene_tasks)
            self.cur = self.conn.cursor()
            self.cur.execute("""UPDATE scenes SET scene_name=%s, scene_tasks=%s WHERE scene_id=%s""",
                            (scene_name, task, str(scene_id)))

            self.conn.commit()
            self.conn.close()

            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)

        def insertdb(self, scene_id, scene_name, scene_tasks):
            print 'Insert Scene id : {}'.format(scene_id)
            # tasks = json.dumps(scene_tasks)
            self.cur = self.conn.cursor()
            self.cur.execute(
                """INSERT INTO scenes (scene_id, scene_name, scene_tasks) VALUES (%s, %s, %s);""",
                (scene_id, scene_name, scene_tasks))
            self.conn.commit()
            self.conn.close()
            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)


        def insertsqlite(self,scene_id, scene_name, scene_tasks):
            # SQL lite
            print 'Insertsqlite Scene id : {}'.format(scene_id)
            gg = expanduser("~")
            path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            conn = sqlite3.connect(gg + path)
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO scenes (scene_id, scene_name, scene_tasks) VALUES (?, ?, ?);""",
                (scene_id, scene_name, scene_tasks))
            conn.commit()
            conn.close()
            print('wooooohoooooooooinsert')
            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)



        def updatesqlite(self,scene_id, scene_name, scene_tasks):
            # print 'Insertsqlite Scene id : {}'.format(scene_id)
            gg = expanduser("~")
            path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            conn = sqlite3.connect(gg + path)
            task = json.dumps(scene_tasks)
            cur = conn.cursor()
            cur.execute("""
                           UPDATE scenes
                           SET SCENE_NAME=?,SCENE_TASKS=?
                           WHERE SCENE_ID=?
                        """, (scene_name, task,str(scene_id)))

            conn.commit()
            conn.close()
            print('wooooohoooooooooupdate')
            self.vip.pubsub.publish('pubsub', topic_agent_reload,
                    {'Type': 'HiVE Scene Control'}, None)

        def deletesqlite(self, scene_id):
            # print 'Delete Scene id : {}'.format(scene_id)
            scene_id = str(scene_id)
            gg = expanduser("~")
            path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            conn = sqlite3.connect(gg + path)
            cur = conn.cursor()
            cur.execute("DELETE FROM scenes WHERE SCENE_ID ='{}'".format(scene_id))

            conn.commit()
            conn.close()
            print('wooooohooooooooodelete')
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
