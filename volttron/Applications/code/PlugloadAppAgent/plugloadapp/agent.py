# -*- coding: utf-8 -*- {{{
#Author : Nopparat A
#}}}


from datetime import datetime
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from dateutil.relativedelta import relativedelta

import logging
import sys
import json
import datetime
import psycopg2
import psycopg2.extras
import settings

publish_period = 10

utils.setup_logging()
_log = logging.getLogger(__name__)

def PlugloadAppAgent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return  config.get(name, '')

    # 1. @params agent
    agent_id = get_config('agent_id')

    # 2. @param DB interfaces
    db_host = get_config('db_host')
    db_port = get_config('db_port')
    db_database = get_config('db_database')
    db_user = get_config('db_user')
    db_password = get_config('db_password')
    db_table_plugload_daily_consumption = settings.DATABASES['default']['TABLE_plugload_daily_consumption']
    db_table_plugload_monthly_consumption = settings.DATABASES['default']['TABLE_plugload_monthly_consumption']

    class Agent(PublishMixin, BaseAgent):

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            self.start_first_time = True
            self.conversion_kWh = publish_period / (3600.0 * 1000.0)
            self.check_day = datetime.datetime.now().weekday()
            self.device_power = 0
            self.device_power_from_grid = 0
            self.device_energy = 0
            self.device_energy_from_grid = 0
            self.device_bill = 0
            self.device_total_bill = 0
            self.power_from_load = 0
            self.power_from_grid_import = 0
            self.power_lighting = 0
            self.power_from_grid_lighting = 0
            self.power_ac = 0
            self.power_from_grid_ac = 0
            self.power_ev = 0
            self.power_from_grid_ev = 0
            self.current_electricity_price = 0

            try:
                self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database,
                                            user=db_user, password=db_password)
                self.cur = self.con.cursor()
                print ("{} connects to the database name {} successfully".format(agent_id, db_database))

            except:
                print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))

        def set_variable(self, k, v):  # k=key, v=value
            self.variables[k] = v

        def get_variable(self, k):
            return self.variables.get(k, None)  # default of get variable is none

        def setup(self):
            super(Agent, self).setup()
            # Demonstrate accessing value from the config file
            _log.info(config['message'])
            self._agent_id = config['agent_id']
            self.get_yesterday_data()
            self.get_today_data()
            self.get_last_month_data()
            self.start_new_month()
            self.get_this_month_data()

        def start_new_day(self):
            self.device_energy = 0
            self.device_energy_from_grid = 0
            self.device_bill = 0
            self.device_total_bill = 0

        def start_new_month(self):
            self.device_energy_this_month = 0
            self.device_energy_from_grid_this_month = 0
            self.device_bill_this_month = 0
            self.device_total_bill_this_month = 0

        @matching.match_start('/app/ui/grid/update_ui/bemoss/999')
        def on_match_gridappagent(self, topic, headers, message, match):
            message_from_gridApp = json.loads(message[0])
            self.current_electricity_price = message_from_gridApp['current_electricity_price']

        @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
        def on_match_smappee(self, topic, headers, message, match):
            print "Hello from SMappee"
            message_from_Smappee = json.loads(message[0])
            self.power_from_load = message_from_Smappee['load_activePower']
            # self.power_from_solar = message_from_Smappee['solar_activePower']
            if (message_from_Smappee['grid_activePower']):
                self.power_from_grid_import = message_from_Smappee['grid_activePower']
                # self.power_from_grid_export = 0
            else:
                # self.power_from_grid_export = abs(message_from_Smappee['grid_activePower'])
                self.power_from_grid_import = 0

            print self.power_from_grid_import
            print self.power_from_load

        @matching.match_start('/app/ui/lightingapp/update_ui/bemoss/999')
        def on_match_LightingApp(self, topic, headers, message, match):
            received_message = json.loads(message[0])
            self.power_lighting = received_message['power_lighting']
            self.power_from_grid_lighting = received_message['power_from_grid_lighting']

        @matching.match_start('/app/ui/acapp/update_ui/bemoss/999')
        def on_match_ACApp(self, topic, headers, message, match):
            received_message = json.loads(message[0])
            self.power_ac = received_message['power_AC']
            self.power_from_grid_ac = received_message['power_from_grid_AC']

        @matching.match_start('/app/ui/evapp/update_ui/bemoss/999')
        def on_match_EVApp(self, topic, headers, message, match):
            received_message = json.loads(message[0])
            self.power_ev = received_message['power_ev']
            self.power_from_grid_ev = received_message['power_from_grid_ev']

        def calculate_power(self):
            sum_power_from_others = self.power_lighting + self.power_ac + self.power_ev
            if (sum_power_from_others > self.power_from_load):
                self.device_power = 0
            else:
                self.device_power = self.power_from_load - sum_power_from_others

            sum_power_from_grid_from_others = self.power_from_grid_lighting + self.power_from_grid_ac + self.power_from_grid_ev
            if (sum_power_from_grid_from_others > self.power_from_grid_import):
                self.device_power_from_grid = 0
            else:
                self.device_power_from_grid = self.power_from_grid_import - sum_power_from_grid_from_others

        @periodic(publish_period)
        def calculate_device_energy_today(self):
            self.calculate_power()
            # Calculate total energy usage from device
            try:
                self.device_energy += self.device_power * self.conversion_kWh
            except:
                self.device_energy = self.device_power * self.conversion_kWh

            # Calculate energy usage of device which recieved from grid
            try:
                self.device_energy_from_grid += self.device_power_from_grid * self.conversion_kWh
            except:
                self.device_energy_from_grid = self.device_power_from_grid * self.conversion_kWh

            self.calculate_bill_today()
            self.calculate_this_month_device_energy_and_bill()

        def calculate_bill_today(self):
             total_bill_current_time = self.device_power * self.conversion_kWh * self.current_electricity_price
             bill_current_time = self.device_power_from_grid * self.conversion_kWh * self.current_electricity_price
             try:
                 self.device_total_bill += total_bill_current_time
                 self.device_bill += bill_current_time
             except:
                 self.device_total_bill = total_bill_current_time
                 self.device_bill = bill_current_time

        def start_new_day_checking(self):
            today = datetime.datetime.now().weekday()
            if (((self.check_day == 6) and (self.check_day > today)) or ((self.check_day is not 6) and (self.check_day < today))):
                self.start_new_day()
            else:
                pass

        def insertDB(self, table):
            if (table == 'daily'):
                self.cur.execute("INSERT INTO " + db_table_plugload_daily_consumption +
                                 " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date())), "plugload",
                                  self.device_energy,
                                  self.device_energy_from_grid,
                                  self.device_bill, self.device_total_bill))
                self.con.commit()
            elif (table == 'monthly'):
                self.cur.execute("INSERT INTO " + db_table_plugload_monthly_consumption +
                                 " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date() + relativedelta(day=31))),
                                  "plugload",
                                  self.device_energy_this_month,
                                  self.device_energy_from_grid_this_month,
                                  self.device_bill_this_month,
                                  self.device_total_bill_this_month))

                self.con.commit()

        def get_yesterday_data(self):
            self.device_energy_last_day = 0
            self.device_energy_from_grid_last_day = 0
            self.device_bill_last_day = 0
            self.device_total_bill_last_day = 0

            time_now = datetime.datetime.now()
            last_day = str((time_now - datetime.timedelta(days=1)).date())

            self.cur.execute(
                "SELECT * FROM " + db_table_plugload_daily_consumption + " WHERE date = '" + last_day + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.device_energy_last_day = data[i][3]
                    self.device_energy_from_grid_last_day = data[i][4]
                    self.device_bill_last_day = data[i][5]
                    self.device_total_bill_last_day = data[i][6]
            else:
                pass

        def get_last_month_data(self):
            self.device_energy_last_month = 0
            self.device_energy_from_grid_last_month = 0
            self.device_bill_last_month = 0
            self.device_total_bill_last_month = 0

            first_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1).date()
            end_date = first_date + relativedelta(day=31)
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.cur.execute("SELECT * FROM " + db_table_plugload_daily_consumption + " WHERE date BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    try:
                        self.device_energy_last_month += data[i][3]
                        self.device_energy_from_grid_last_month += data[i][4]
                        self.device_bill_last_month += data[i][5]
                        self.device_total_bill_last_month += data[i][6]
                    except:
                        self.device_energy_last_month = data[i][3]
                        self.device_energy_from_grid_last_month = data[i][4]
                        self.device_bill_last_month = data[i][5]
                        self.device_total_bill_last_month = data[i][6]
            else:
                pass

        def get_today_data(self):
            today = str(datetime.datetime.now().date())
            self.cur.execute("SELECT * FROM " + db_table_plugload_daily_consumption + " WHERE date = '" + today + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.device_energy = data[i][3]
                    self.device_energy_from_grid = data[i][4]
                    self.device_bill = data[i][5]
                    self.device_total_bill = data[i][6]
            else:
                self.start_new_day()

        def get_this_month_data(self):
            self.device_energy_this_month_until_last_day = 0
            self.device_energy_from_grid_this_month_until_last_day = 0
            self.device_bill_this_month_until_last_day = 0
            self.device_total_bill_this_month_until_last_day = 0

            first_date = datetime.datetime.now().replace(day=1).date()
            end_date = datetime.datetime.now() - datetime.timedelta(days=1)
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.cur.execute("SELECT * FROM " + db_table_plugload_daily_consumption + " WHERE date BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")

            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    try:
                        self.device_energy_this_month_until_last_day += data[i][3]
                        self.device_energy_from_grid_this_month_until_last_day += data[i][4]
                        self.device_bill_this_month_until_last_day += data[i][5]
                        self.device_total_bill_this_month_until_last_day += data[i][6]
                    except:
                        self.device_energy_this_month_until_last_day = data[i][3]
                        self.device_energy_from_grid_this_month_until_last_day = data[i][4]
                        self.device_bill_this_month_until_last_day = data[i][5]
                        self.device_total_bill_this_month_until_last_day = data[i][6]
            else:
                self.start_new_month()

        def calculate_this_month_device_energy_and_bill(self):
            try:
                self.device_energy_this_month = self.device_energy_this_month_until_last_day + self.device_energy
                self.device_energy_from_grid_this_month = self.device_energy_from_grid_this_month_until_last_day + self.device_energy_from_grid
                self.device_bill_this_month = self.device_bill_this_month_until_last_day + self.device_bill
                self.device_total_bill_this_month = self.device_total_bill_this_month_until_last_day + self.device_total_bill
            except:
                self.device_energy_this_month = self.device_energy
                self.device_energy_from_grid_this_month = self.device_energy_from_grid
                self.device_bill_this_month = self.device_bill
                self.device_total_bill_this_month = self.device_total_bill

        def calculate_daily_bill_compare(self):
            try:
                self.device_bill_compare = (self.device_bill - self.device_bill_last_day) / self.device_bill_last_day * 100
            except:
                self.device_bill_compare = 100

        def calculate_monthly_bill_compare(self):
            try:
                self.device_bill_this_month_compare = (self.device_bill_this_month - self.device_bill_last_month) / self.device_bill_last_month * 100
            except:
                self.device_bill_this_month_compare = 100

        @periodic(20)
        def updateDB(self):
            today = str(datetime.datetime.now().date())
            last_day_of_this_month = str(datetime.datetime.now().date() + relativedelta(day=31))
            # last_day_of_end_month = str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))

            # Update table "daily_consumption"
            self.cur.execute("SELECT * FROM " + db_table_plugload_daily_consumption + " WHERE date = '" + today + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute("UPDATE " + db_table_plugload_daily_consumption +
                                     " SET device_energy=%s, device_energy_from_grid=%s, "
                                     "device_bill=%s, device_total_bill=%s WHERE date = '" + today + "'",
                                     (self.device_energy, self.device_energy_from_grid, self.device_bill,
                                      self.device_total_bill))
                    self.con.commit()
                    print "Success to Update Postgres"
                except:
                    print "Cannot update database"
            else:
                self.insertDB('daily')

            # Update table "monthly_consumption"
            self.cur.execute("SELECT * FROM " + db_table_plugload_monthly_consumption + " WHERE date = '"
                             + last_day_of_this_month + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute("UPDATE " + db_table_plugload_monthly_consumption +
                                     " SET device_energy=%s, device_energy_from_grid=%s, "
                                     "device_bill=%s, device_total_bill=%s WHERE date = '"
                                     + last_day_of_this_month + "'",
                                     (self.device_energy_this_month,
                                      self.device_energy_from_grid_this_month,
                                      self.device_bill_this_month,
                                      self.device_total_bill_this_month))
                    self.con.commit()
                    print "Success to Update Postgres"
                except:
                    print "Cannot update database"
            else:
                self.insertDB('monthly')

        @periodic(publish_period)
        def publish_message(self):
            topic = '/app/ui/plugloadapp/update_ui/bemoss/999'
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'receiver_agent_id': "ui",
            }

            self.calculate_daily_bill_compare()
            self.calculate_monthly_bill_compare()

            try:
                message = json.dumps({"daily_bill_plugload": round(self.device_bill, 2),
                                      "daily_bill_plugload_percent_compare": round(self.device_bill_compare, 2),
                                      "monthly_bill_plugload": round(self.device_bill_this_month, 2),
                                      "monthly_bill_plugload_percent_compare": round(self.device_bill_this_month_compare, 2),
                                      "power_plugload": round(self.device_power, 2),
                                      "power_from_grid_plugload": round(self.device_power_from_grid, 2)})
            except:
                message = json.dumps({"daily_bill_plugload": 0.00,
                                      "daily_bill_plugload_percent_compare": 0.00,
                                      "monthly_bill_plugload": 0.00,
                                      "monthly_bill_plugload_percent_compare": 0.00,
                                      "power_plugload": 0.00,
                                      "power_from_grid_plugload": 0.00})
            self.publish(topic, headers, message)
            print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)


    Agent.__name__ = 'PlugloadAppAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(PlugloadAppAgent,
                           description='PlugloadApp agent',
                           argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass