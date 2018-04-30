#Author : NopparatA.

from __future__ import division
from datetime import datetime
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from dateutil.relativedelta import relativedelta
from volttron.platform.messaging import headers as headers_mod

import settings
import json
import psycopg2
import psycopg2.extras
import datetime
import logging
import sys
import numpy as np
import calendar


utils.setup_logging()
_log = logging.getLogger(__name__)

def PVrealtimeAppAgent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # 1. @params agent
    agent_id = get_config('agent_id')

    # 2. @param DB interfaces
    db_host = get_config('db_host')
    db_port = get_config('db_port')
    db_database = get_config('db_database')
    db_user = get_config('db_user')
    db_password = get_config('db_password')
    db_table_pvrealtime = settings.DATABASES['default']['TABLE_pvrealtime_hourly']


    class Agent(PublishMixin, BaseAgent):
        '''Calculate energy and bill from evergy power sources'''

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            # self.start_first_time = True
            # self.check_day = datetime.datetime.now().day
            # self.check_month = datetime.datetime.now().month
            # self.check_year = datetime.datetime.now().year
            # self.current_electricity_price = 0

            try:
                self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                            user=db_user, password=db_password)
                self.cur = self.con.cursor()
                print ("{} connects to the database name {} successfully".format(agent_id, db_database))

            except:
                print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))

        def set_variable(self, k, v): # k=key, v=value
            self.variables[k] = v

        def get_variable(self, k):
            return self.variables.get(k, None) #default of get variable is none

        def setup(self):
            super(Agent, self).setup()
            # Demonstrate accessing value from the config file
            _log.info(config['message'])
            self._agent_id = agent_id
            # self.get_today_data()

        @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
        def on_match_smappee(self, topic, headers, message, match):
            print "Hello from SMappee"
            message_from_Smappee = json.loads(message[0])
            self.power_from_solar = message_from_Smappee['solar_activePower']

            print self.power_from_solar
        @periodic(10)
        def insertDB(self):
            now_str = datetime.datetime.now()
            sql_cmd = "INSERT INTO " + db_table_pvrealtime + " VALUES (DEFAULT,'"+str(now_str.strftime('%Y-%m-%d'))+"', "+str(now_str.hour)+","+str(now_str.minute)+", "+str(self.power_from_solar)+");"
            print sql_cmd
            self.cur.execute(str(sql_cmd))

            self.con.commit()

    Agent.__name__ = 'PVrealtimeAppAgent'
    return Agent(**kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(PVrealtimeAppAgent,
                       description='PVrealtimeApp agent',
                       argv=argv)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass