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

publish_periodic = 10
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982

utils.setup_logging()
_log = logging.getLogger(__name__)

def EnergyBillAppAgent(config_path, **kwargs):
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
    db_table_daily_consumption = settings.DATABASES['default']['TABLE_daily_consumption']
    db_id_column_name = 'date'

    #Dictionary of variables supposed to be save into database
    log_variables = dict(date='date', gridimportenergy='double', gridexportenergy='double', solarenergy='double',
                         loadenergy='double', gridimportbill='double', gridexportbill='double', solarbill='double',
                         loadbill='double')

    class Agent(PublishMixin, BaseAgent):
        '''Calculate energy and bill from evergy power sources'''

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs

            self.start_first_time = True
            self.check_day = datetime.datetime.now().weekday()

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
            self._agent_id = config['agentid']
            self.get_yesterday_data()
            self.get_today_data()

        def start_new_day(self):
            self.load_energy_today = 0
            self.solar_energy_today = 0
            self.grid_import_energy_today = 0
            self.grid_export_energy_today = 0
            self.load_bill_today = 0
            self.solar_bill_today = 0
            self.grid_import_bill_today = 0
            self.grid_export_bill_today = 0
            self.get_yesterday_data()

        @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
        def on_match_smappee(self, topic, headers, message, match):
            print "Hello from SMappee"
            message_from_Smappee = json.loads(message[0])
            self.power_from_load = message_from_Smappee['load_activePower']
            self.power_from_solar = message_from_Smappee['solar_activePower']
            if (message_from_Smappee['grid_activePower']):
                self.power_from_grid_import = message_from_Smappee['grid_activePower']
                self.power_from_grid_export = 0
            else:
                self.power_from_grid_export = abs(message_from_Smappee['grid_activePower'])
                self.power_from_grid_import = 0

            # This for calculate the period of power which got from SMAPPEE
            if (self.start_first_time):
                self.conversion_kWh = 0
                self.last_time = datetime.datetime.now()
                self.start_first_time = False
            else:
                time_now = datetime.datetime.now()
                timedelta_period = time_now - self.last_time
                self.conversion_kWh = timedelta_period.seconds / (3600 * 1000)
                self.last_time = time_now

            self.start_new_day_checking()
            self.calculate_energy_today()
            self.calculate_bill_today()

        def calculate_energy_today(self):
            # Calculate Energy from Grid_import
            self.grid_import_energy_today += self.power_from_grid_import * self.conversion_kWh
            self.set_variable('gridImportEnergy', self.grid_import_energy_today)
            # Calculate Energy from Grid_export
            self.grid_export_energy_today += self.power_from_grid_export * self.conversion_kWh
            self.set_variable('gridExportEnergy', self.grid_export_energy_today)
            # Calculate Energy from Solar
            self.solar_energy_today += self.power_from_solar * self.conversion_kWh
            self.set_variable('solarEnergy', self.solar_energy_today)
            #Calculate Energy from Load
            self.load_energy_today += self.power_from_load * self.conversion_kWh
            self.set_variable('loadEnergy', self.load_energy_today)


        def calculate_bill_today(self):
            time_now = datetime.datetime.now()
            weekday = time_now.weekday()
            start_peak_period = time_now.replace(hour=9, minute=0, second=1)
            end_peak_period = time_now.replace(hour=22, minute=0, second=0)

            if ((weekday == 5) or (weekday == 6) or (weekday == 7)): #Holiday have electricity price only OFFPEAK_RATE
                self.grid_import_bill_today += self.power_from_grid_import * self.conversion_kWh * OFFPEAK_RATE
                self.grid_export_bill_today += self.power_from_grid_export * self.conversion_kWh * OFFPEAK_RATE
                self.solar_bill_today += self.power_from_solar * self.conversion_kWh * OFFPEAK_RATE
                self.load_bill_today += self.power_from_load * self.conversion_kWh * OFFPEAK_RATE
            else:
                if (time_now > start_peak_period) and (time_now < end_peak_period):
                    self.grid_import_bill_today += self.power_from_grid_import * self.conversion_kWh * PEAK_RATE
                    self.grid_export_bill_today += self.power_from_grid_export * self.conversion_kWh * PEAK_RATE
                    self.solar_bill_today += self.power_from_solar * self.conversion_kWh * PEAK_RATE
                    self.load_bill_today += self.power_from_load * self.conversion_kWh * PEAK_RATE
                else:
                    self.grid_import_bill_today += self.power_from_grid_import * self.conversion_kWh * OFFPEAK_RATE
                    self.grid_export_bill_today += self.power_from_grid_export * self.conversion_kWh * OFFPEAK_RATE
                    self.solar_bill_today += self.power_from_solar * self.conversion_kWh * OFFPEAK_RATE
                    self.load_bill_today += self.power_from_load * self.conversion_kWh * OFFPEAK_RATE

            self.set_variable('gridImportBill', self.grid_import_bill_today)
            self.set_variable('gridExportBill', self.grid_export_bill_today)
            self.set_variable('solarBill', self.solar_bill_today)
            self.set_variable('loadBill', self.load_bill_today)

        def start_new_day_checking(self):
            today = datetime.datetime.now().weekday()
            if (((self.check_day == 6) and (self.check_day > today)) or ((self.check_day is not 6) and (self.check_day < today))):
                self.start_new_day()
                self.insertDB()
            else:
                pass

        def insertDB(self):
            self.cur.execute("INSERT INTO " + db_table_daily_consumption +
                             " VALUES(DEFULT, %s, %s, %s, %s, %s, %s, %s, %s)",
                             ((str(datetime.datetime.now().date()-datetime.timedelta(days=1))),
                              self.get_variable('gridImportEnergy'), self.get_variable('gridExportEnergy'),
                              self.get_variable('solarEnergy'), self.get_variable('loadEnergy'),
                              self.get_variable('gridImportBill'), self.get_variable('gridExportBill'),
                              self.get_variable('solarBill'), self.get_variable('loadBill')))

            self.con.commit()

        @periodic(60)
        def updateDB(self):
            today = str(datetime.datetime.now().date())
            try:
                self.cur.execute("UPDATE " + db_table_daily_consumption + " SET gridimportenergy=%s, gridexportenergy=%s, "
                                                                          "solarenergy=%s, loadenergy=%s, gridimportbill=%s,"
                                                                          "gridexportbill=%s, solarbill=%s, loadbill=%s"
                                                                          " WHERE date = '" + today + "'",
                                 (self.get_variable('gridImportEnergy'), self.get_variable('gridExportEnergy'),
                                  self.get_variable('solarEnergy'), self.get_variable('loadEnergy'),
                                  self.get_variable('gridImportBill'), self.get_variable('gridExportBill'),
                                  self.get_variable('solarBill'), self.get_variable('loadBill')))
                self.con.commit()
                print"Success"
            except:
                print"Cannot update database"

        def get_yesterday_data(self):
            time_now = datetime.datetime.now()
            last_day = str((time_now - datetime.timedelta(days=1)).date())

            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE date = '" + last_day + "'")
            try:
                data = self.cur.fetchall()[0]
                self.grid_import_energy_last_day = data[2]
                self.grid_export_energy_last_day = data[3]
                self.solar_energy_last_day = data[4]
                self.load_energy_last_day = data[5]
                self.grid_import_bill_last_day = data[6]
                self.grid_export_bill_last_day = data[7]
                self.solar_bill_last_day = data[8]
                self.load_bill_last_day = data[9]

            except:
                self.grid_import_energy_last_day = 0
                self.grid_export_energy_last_day = 0
                self.solar_energy_last_day = 0
                self.load_energy_last_day = 0
                self.grid_import_bill_last_day = 0
                self.grid_export_bill_last_day = 0
                self.solar_bill_last_day = 0
                self.load_bill_last_day = 0


        def get_today_data(self):
            today = str(datetime.datetime.now().date())
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE date = '" + today + "'")
            try:
                data = self.cur.fetchall()[0]
                self.grid_import_energy_today = data[2]
                self.grid_export_energy_today = data[3]
                self.solar_energy_today = data[4]
                self.load_energy_today = data[5]
                self.grid_import_bill_today = data[6]
                self.grid_export_bill_today = data[7]
                self.solar_bill_today = data[8]
                self.load_bill_today = data[9]

            except:
                self.start_new_day()

        @periodic(publish_periodic)
        def publish_message(self):
            topic = "/agent/ui/dashboard"
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'data_source': "powermeterApp"
            }
            message = json.dumps(({"daily_energy_usage": round(self.get_variable('loadEnergy'), 2),
                                   "last_day_energy_usage": round(self.load_energy_last_day, 2),
                                   "daily_electricity_bill": round(self.get_variable('gridImportBill'), 2),
                                   "last_day_bill_compare": round(self.get_variable('gridImportBill')-self.grid_import_bill_last_day, 2)}))

            self.publish(topic, headers, message)
            print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)


    Agent.__name__ = 'EnergyBillAppAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(EnergyBillAppAgent,
                       description='EnergyBillApp agent',
                       argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass