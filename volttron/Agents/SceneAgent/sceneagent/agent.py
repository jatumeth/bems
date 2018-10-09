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
import pyrebase
import pprint
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
def scenecontrol_agent(config_path, **kwargs):
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

    class SceneControlAgent(Agent):

        def __init__(self, config_path, **kwargs):
            super(SceneControlAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = agent_id
            self.conn = None
            self.cur = None
            self.sceneconf = None
            self.num_of_scene = None
            self.token = None
            self.url = None
            self.reload_config()  # Reload Scene when Agent Start
            self._message = self.config.get('message', DEFAULT_MESSAGE)
            self._heartbeat_period = self.config.get('heartbeat_period',
                                                     DEFAULT_HEARTBEAT_PERIOD)
            _log.info("init attribute to Agent")

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            _log.info(self.config.get('message', DEFAULT_MESSAGE))
            self._agent_id = self.config.get('agentid')
            self.url = self.config.get('backend_url') + self.config.get('scene_api')
            print self.url
            self.token = self.config.get('token')

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            if self._heartbeat_period != 0:
                self.vip.heartbeat.start_with_period(self._heartbeat_period)
                self.vip.health.set_status(STATUS_GOOD, self._message)
            # self.resync_scene()
            # self.checkactivescence()

        @PubSub.subscribe('pubsub', topic_scenecontrol)
        def match_device_control(self, peer, sender, bus, topic, headers, message):

            print "Topic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)

            msg = json.loads(message)

            print "----"
            print msg
            print "----"


            tasks = self.sceneconf1[str(msg['scene_id'])]




            task_list = json.loads(tasks['tasks'])
            print('task_list: {}'.format(task_list))



            for task in task_list:
                topic = str('/ui/agent/update/hive/999/') + str(task['device_id'])
                print type(task['command'])

                for k, v in task['command'].items():
                    if k == 'isLock':
                        task['command']['isLock'] = str(task['command']['isLock'] )

                message = json.dumps(task['command'])
                print type(message)
                print ("topic {}".format(topic))
                print ("message {} \n".format(message))

                self.vip.pubsub.publish(
                    'pubsub', topic,
                    {'Type': 'HiVE Scene Control'}, message)

            try:

                gg = expanduser("~")
                path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
                conn = sqlite3.connect(gg + path)
                cur = conn.cursor()
                cur.execute("""
                                           UPDATE active_scene
                                           SET scene_id=?,scene_name=?
                                           WHERE scene_id=?
                                        """, (msg['scene_id'], '1', '1'))

                conn.commit()
                conn.close()
                print('wooooohoooooooooupdate')

                # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                #                              user=db_user, password=db_password)
                #
                # self.cur = self.conn.cursor()
                # self.cur.execute("""
                #    UPDATE active_scene
                #    SET scene_id=%s, scene_name=%s
                #    WHERE scene=%s
                # """, (msg['scene_id'], '1', '1'))
                #
                # self.conn.commit()
                # self.conn.close()

            except Exception as er:
                print("Error in insertdb : {}".format(er))


        @PubSub.subscribe('pubsub', topic_agent_reload)
        def match_agent_reload(self, peer, sender, bus, topic, headers, message):
            print('Message Recived')
            self.reload_config()

        @PubSub.subscribe('pubsub', topic_token_reload)
        def match_token_reload(self, peer, sender, bus, topic, headers, message):
            print('Message Recived')
            print(' >>> Reload Token')
            msg = json.loads(message)
            new_token = msg.get('token', None)
            self.config.update({'token': new_token})
            config_dict = self.config
            json.dump(config_dict, open(config_path, 'w'), sort_keys=True, indent=4)

        def reload_config(self): # reload scene configuration to Agent Variable

            gg = expanduser("~")
            path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            conn = sqlite3.connect(gg + path)
            cur = conn.cursor()
            cur.execute("""SELECT scene_id, scene_tasks FROM scenes """)
            rows = cur.fetchall()
            conf = {}
            for row in rows:
                id = row[0]
                # tasks = json.loads(row[1])
                tasks = row[1]
                conf.update({str(id): {'tasks': tasks}})
            self.num_of_scene = str(len(conf))
            self.sceneconf1 = conf
            print"444444444444444"
            print self.sceneconf1
            conn.commit()
            conn.close()
            print("woooohoooooooooupdate2")


            # conn = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
            #                         password=db_password)
            # self.conn = conn
            # self.cur = self.conn.cursor()
            # self.cur.execute("""SELECT scene_id, scene_tasks FROM scenes""")
            # rows = self.cur.fetchall()
            # conf = {}
            # for row in rows:
            #     id = row[0]
            #     # tasks = json.loads(row[1])
            #     tasks1 = row[1]
            #     conf.update({str(id): {'tasks1': tasks1}})
            #
            # self.num_of_scene = str(len(conf))
            # self.sceneconf = conf
            # print(" >>> Reload Config Success")

        def resync_scene(self):
            # This function is executed by scene_id from request not exist on Local Database
            try:
                print(">>> Request GET:Scene for resync loacal database")
                response = requests.get(self.url,
                                        headers={"Authorization": "Token {token}".format(token=self.token),
                                                "Content-Type": "application/json; charset=utf-8"
                                                },
                                        data=json.dumps({}))

                if str(response.status_code) == '200':
                    print('Request Return 200')
                    data = json.loads(response.content)
                    scenes = data.get('scenes')
                    self.truncatedb()
                    for scene in scenes:
                        self.insertdb(scene_id=scene.get('scene_id'),
                                      scene_name=scene.get('scene_name'),
                                      scene_task=scene.get('scene_tasks'))

                    self.reload_config()

                elif json.loads(response.content).get('detail').__contains__('Invalid token'):
                    print("Token is Expired")

            except Exception as err:
                print(">>> Error Occur : {}".format(err))

        def truncatedb(self):

            # gg = expanduser("~")
            # path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
            # conn = sqlite3.connect(gg + path)
            # cur = conn.cursor()
            # cur.execute(
            #     """TRUNCATE TABLE scenes;""")
            # conn.commit()
            # conn.close()
            # print('wooooohoooooooooTRUNCATE')
            #
            # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                              user=db_user, password=db_password)
            #
            # self.cur = self.conn.cursor()
            # self.cur.execute("""TRUNCATE TABLE scenes;""")
            # self.conn.commit()
            # self.conn.close()
            print(' >>> truncate table scene Complete')

        def insertdb(self, scene_id, scene_name, scene_task):
            print 'insert'
            # tasks = json.dumps(scene_task)
            try:
                gg = expanduser("~")
                path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
                conn = sqlite3.connect(gg + path)
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO scenes (scene_id, scene_name, scene_tasks) VALUES (?, ?, ?);""",
                    (scene_id, scene_name, scene_task))
                conn.commit()
                conn.close()
                print('wooooohoooooooooinsert')


                # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                #                              user=db_user, password=db_password)
                #
                # self.cur = self.conn.cursor()
                # self.cur.execute(
                #     """INSERT INTO scenes (scene_id, scene_name, scene_tasks) VALUES (%s, %s, %s);""",
                #     (scene_id, scene_name, scene_task))
                # self.conn.commit()
                # self.conn.close()
            except Exception as er:
                print("Error in insertdb : {}".format(er))

        def createactivescence(self):
                gg = expanduser("~")
                path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
                conn = sqlite3.connect(gg + path)
                cur = conn.cursor()
                cur.execute(
                    """TRUNCATE TABLE active_scene;""")

                conn.commit()
                conn.close()
                print('wooooohoooooooooactivescene')

                # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                #                              user=db_user, password=db_password)
                #
                # self.cur = self.conn.cursor()
                # self.cur.execute("""TRUNCATE TABLE active_scene;""")
                # self.conn.commit()
                # self.conn.close()

                gg = expanduser("~")
                path = '/workspace/hive_os/volttron/hive_lib/sqlite.db'
                conn = sqlite3.connect(gg + path)
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO active_scene (scene_id, scene_name ) VALUES (?, ?);""",
                    ('1','1'))
                conn.commit()
                conn.close()
                print('wooooohooooooooactive_scene55555555555555555')

                # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                #                              user=db_user, password=db_password)
                # self.cur = self.conn.cursor()
                #
                # self.cur.execute(
                #     """INSERT INTO active_scene (scene, scene_name) VALUES (%s, %s);""",
                #     ('1', '1'))
                # self.conn.commit()
                # self.conn.close()

        def checkactivescence(self):
            print ""

            # self.conn = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                              user=db_user, password=db_password)
            # self.cur = self.conn.cursor()
            # self.cur.execute("""SELECT * FROM active_scene """)
            # rows = self.cur.fetchall()
            # for row in rows:
            #     self.createrow1 = True
            #     numrow1 = 0
            #     if int(row[1]) == '1':
            #         self.createrow1 = False
            #         numrow1 = numrow1+1
            # self.conn.close()
            #
            # if self.createrow1 == True:
            #     self.createactivescence()
            # if numrow1 > 1:
            #     self.createactivescence()

    Agent.__name__ = 'scenecontrolAgent'
    return SceneControlAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(scenecontrol_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
