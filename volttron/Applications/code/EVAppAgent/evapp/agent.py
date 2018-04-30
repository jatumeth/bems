# -*- coding: utf-8 -*- {{{
#Author : Nopparat A
#}}}


from __future__ import division
from datetime import datetime
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from dateutil.relativedelta import relativedelta
from volttron.platform.messaging import headers as headers_mod

import logging
import sys
import settings
import json
import datetime
import psycopg2
import psycopg2.extras


utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 5
BATT_START_KILOMETER = 50
BATT_MAX_KITLOMETER = 82

start_percent_charge = BATT_START_KILOMETER / BATT_MAX_KITLOMETER * 100

def EVAppAgent(config_path, **kwargs):
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
    db_table_ev_daily_consumption = settings.DATABASES['default']['TABLE_ev_daily_consumption']
    db_table_ev_monthly_consumption = settings.DATABASES['default']['TABLE_ev_monthly_consumption']

    class Agent(PublishMixin, BaseAgent):

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            self.current_electricity_price = 0
            self.device_power = 0
            self.check_day = datetime.datetime.now().weekday()
            self.conversion_kWh = publish_periodic / (3600.0 * 1000.0)
            self.device_status = {}
            self.device_power = {}
            self.device_power_from_grid = {}
            self.device_energy = {}
            self.device_energy_from_grid = {}
            self.device_bill = {}
            self.device_total_bill = {}
            self.check_first_time = {}
            self.check_power = {}
            self.check_time = {}
            self.percent_charge = {}
            self.EV_mode = {}
            self.power_from_load = 0
            self.power_from_grid_import = 0
            self.time_delta = datetime.timedelta(minutes=2, seconds=28)

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
            self.device_energy = {}
            self.device_energy_from_grid = {}
            self.device_bill = {}
            self.device_total_bill = {}

        def start_new_month(self):
            self.device_energy_this_month = {}
            self.device_energy_from_grid_this_month = {}
            self.device_bill_this_month = {}
            self.device_total_bill_this_month = {}

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

        @matching.match_start('/agent/ui/dashboard')
        def on_match_gridappagent(self, topic, headers, message, match):
            recived_header = headers['data_source']

            if (recived_header=='gridApp'):
                message_from_gridApp = json.loads(message[0])
                self.current_electricity_price = message_from_gridApp['current_electricity_price']
                print "Current electricity price : {}".format(self.current_electricity_price)
            else:
                pass

        @matching.match_start("/agent/ui/plugload/device_status_response/bemoss/999")
        def on_match_ev(self, topic, headers, message, match):
            '''Use match_all to receive all messages and print them out.'''
            _log.debug("Topic: {topic}, Headers: {headers}, "
                       "Message: {message}".format(
                topic=topic, headers=headers, message=message))

            device_id = headers['AgentID']
            message_from_EV = json.loads(message[0])
            self.device_status[device_id] = message_from_EV['status']
            self.device_power[device_id] = message_from_EV['power']
            try:
                if (self.check_first_time[device_id]):
                    pass
            except:
                self.check_first_time[device_id] = True

            self.calculate_power(device_id)
            self.calculate_EV_percentage()

        def calculate_power(self, device_id):
            if (self.power_from_load > self.power_from_grid_import):
                self.device_power_from_grid[device_id] = self.device_power[device_id] * self.power_from_grid_import / self.power_from_load
            else:
                self.device_power_from_grid[device_id] = self.device_power[device_id]

        @periodic(publish_periodic)
        def calculate_device_energy_today(self):
            device_id = self.device_power.keys()
            for i in range(len(device_id)):
                # Calculate total energy usage from device
                try:
                    self.device_energy[device_id[i]] += self.device_power[device_id[i]] * self.conversion_kWh
                except:
                    self.device_energy[device_id[i]] = self.device_power[device_id[i]] * self.conversion_kWh

                # Calculate energy usage of device which recieved from grid
                try:
                    self.device_energy_from_grid[device_id[i]] += self.device_power_from_grid[device_id[i]] * self.conversion_kWh
                except:
                    self.device_energy_from_grid[device_id[i]] = self.device_power_from_grid[device_id[i]] * self.conversion_kWh

                self.calculate_bill_today(device_id[i])
                self.calculate_this_month_device_energy_and_bill(device_id[i])

        def calculate_bill_today(self, device_id):
             total_bill_current_time = self.device_power[device_id] * self.conversion_kWh * self.current_electricity_price
             bill_current_time = self.device_power_from_grid[device_id] * self.conversion_kWh * self.current_electricity_price
             try:
                 self.device_total_bill[device_id] += total_bill_current_time
                 self.device_bill[device_id] += bill_current_time
             except:
                 self.device_total_bill[device_id] = total_bill_current_time
                 self.device_bill[device_id] = bill_current_time

        def start_new_day_checking(self):
             today = datetime.datetime.now().weekday()
             if (((self.check_day == 6) and (self.check_day > today)) or (
                 (self.check_day is not 6) and (self.check_day < today))):
                 self.start_new_day()
             else:
                 pass

        def insertDB(self, table, device_id):
             if (table == 'daily'):
                 self.cur.execute("INSERT INTO " + db_table_ev_daily_consumption +
                                  " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                  ((str(datetime.datetime.now().date())), device_id,
                                   self.device_energy[device_id],
                                   self.device_energy_from_grid[device_id],
                                   self.device_bill[device_id], self.device_total_bill[device_id]))
                 self.con.commit()
             elif (table == 'monthly'):
                 self.cur.execute("INSERT INTO " + db_table_ev_monthly_consumption +
                                  " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                  ((str(datetime.datetime.now().date() + relativedelta(day=31))),
                                   device_id,
                                   self.device_energy_this_month[device_id],
                                   self.device_energy_from_grid_this_month[device_id],
                                   self.device_bill_this_month[device_id],
                                   self.device_total_bill_this_month[device_id]))

                 self.con.commit()

        def get_yesterday_data(self):
             self.device_energy_last_day = {}
             self.device_energy_from_grid_last_day = {}
             self.device_bill_last_day = {}
             self.device_total_bill_last_day = {}

             time_now = datetime.datetime.now()
             last_day = str((time_now - datetime.timedelta(days=1)).date())

             self.cur.execute(
                 "SELECT * FROM " + db_table_ev_daily_consumption + " WHERE date = '" + last_day + "'")
             if bool(self.cur.rowcount):
                 data = self.cur.fetchall()
                 for i in range(len(data)):
                     self.device_energy_last_day[data[i][2]] = data[i][3]
                     self.device_energy_from_grid_last_day[data[i][2]] = data[i][4]
                     self.device_bill_last_day[data[i][2]] = data[i][5]
                     self.device_total_bill_last_day[data[i][2]] = data[i][6]
             else:
                 pass

        def get_last_month_data(self):
             self.device_energy_last_month = {}
             self.device_energy_from_grid_last_month = {}
             self.device_bill_last_month = {}
             self.device_total_bill_last_month = {}

             first_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1).date()
             end_date = first_date + relativedelta(day=31)
             first_date_str = str(first_date)
             end_date_str = str(end_date)
             self.cur.execute("SELECT * FROM " + db_table_ev_daily_consumption + " WHERE date BETWEEN '" +
                              first_date_str + "' AND '" + end_date_str + "'")
             if bool(self.cur.rowcount):
                 data = self.cur.fetchall()
                 for i in range(len(data)):
                     try:
                         self.device_energy_last_month[data[i][2]] += data[i][3]
                         self.device_energy_from_grid_last_month[data[i][2]] += data[i][4]
                         self.device_bill_last_month[data[i][2]] += data[i][5]
                         self.device_total_bill_last_month[data[i][2]] += data[i][6]
                     except:
                         self.device_energy_last_month[data[i][2]] = data[i][3]
                         self.device_energy_from_grid_last_month[data[i][2]] = data[i][4]
                         self.device_bill_last_month[data[i][2]] = data[i][5]
                         self.device_total_bill_last_month[data[i][2]] = data[i][6]
             else:
                 pass

        def get_today_data(self):
             today = str(datetime.datetime.now().date())
             self.cur.execute(
                 "SELECT * FROM " + db_table_ev_daily_consumption + " WHERE date = '" + today + "'")
             if bool(self.cur.rowcount):
                 data = self.cur.fetchall()
                 for i in range(len(data)):
                     self.device_energy[data[i][2]] = data[i][3]
                     self.device_energy_from_grid[data[i][2]] = data[i][4]
                     self.device_bill[data[i][2]] = data[i][5]
                     self.device_total_bill[data[i][2]] = data[i][6]
             else:
                 self.start_new_day()

        def get_this_month_data(self):
             self.device_energy_this_month_until_last_day = {}
             self.device_energy_from_grid_this_month_until_last_day = {}
             self.device_bill_this_month_until_last_day = {}
             self.device_total_bill_this_month_until_last_day = {}

             first_date = datetime.datetime.now().replace(day=1).date()
             end_date = datetime.datetime.now() - datetime.timedelta(days=1)
             first_date_str = str(first_date)
             end_date_str = str(end_date)
             self.cur.execute("SELECT * FROM " + db_table_ev_daily_consumption + " WHERE date BETWEEN '" +
                              first_date_str + "' AND '" + end_date_str + "'")

             if bool(self.cur.rowcount):
                 data = self.cur.fetchall()
                 for i in range(len(data)):
                     try:
                         self.device_energy_this_month_until_last_day[data[i][2]] += data[i][3]
                         self.device_energy_from_grid_this_month_until_last_day[data[i][2]] += data[i][4]
                         self.device_bill_this_month_until_last_day[data[i][2]] += data[i][5]
                         self.device_total_bill_this_month_until_last_day[data[i][2]] += data[i][6]
                     except:
                         self.device_energy_this_month_until_last_day[data[i][2]] = data[i][3]
                         self.device_energy_from_grid_this_month_until_last_day[data[i][2]] = data[i][4]
                         self.device_bill_this_month_until_last_day[data[i][2]] = data[i][5]
                         self.device_total_bill_this_month_until_last_day[data[i][2]] = data[i][6]
             else:
                 self.start_new_month()

        def calculate_this_month_device_energy_and_bill(self, device_id):
             try:
                 self.device_energy_this_month[device_id] = self.device_energy_this_month_until_last_day[
                                                                device_id] + self.device_energy[device_id]
                 self.device_energy_from_grid_this_month[device_id] = \
                 self.device_energy_from_grid_this_month_until_last_day[device_id] + self.device_energy_from_grid[
                     device_id]
                 self.device_bill_this_month[device_id] = self.device_bill_this_month_until_last_day[device_id] + \
                                                          self.device_bill[device_id]
                 self.device_total_bill_this_month[device_id] = self.device_total_bill_this_month_until_last_day[
                                                                    device_id] + self.device_total_bill[device_id]
             except:
                 self.device_energy_this_month[device_id] = self.device_energy[device_id]
                 self.device_energy_from_grid_this_month[device_id] = self.device_energy_from_grid[device_id]
                 self.device_bill_this_month[device_id] = self.device_bill[device_id]
                 self.device_total_bill_this_month[device_id] = self.device_total_bill[device_id]

        def calculate_daily_bill_compare(self):
             try:
                 self.device_bill_compare = (sum(self.device_bill.values()) - sum(
                     self.device_bill_last_day.values())) / sum(self.device_bill_last_day.values()) * 100
             except:
                 self.device_bill_compare = 100

        def calculate_monthly_bill_compare(self):
             try:
                 self.device_bill_this_month_compare = (sum(self.device_bill_this_month.values()) - sum(
                     self.device_bill_last_month.values())) / sum(self.device_bill_last_month.values()) * 100
             except:
                 self.device_bill_this_month_compare = 100

        def updateDB(self):
             today = str(datetime.datetime.now().date())
             last_day_of_this_month = str(datetime.datetime.now().date() + relativedelta(day=31))
             # last_day_of_end_month = str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))

             device_id = self.device_energy.keys()

             # Update table "daily_consumption"
             for i in range(len(device_id)):
                 self.cur.execute(
                     "SELECT * FROM " + db_table_ev_daily_consumption + " WHERE date = '" + today +
                     "' AND device_id = '" + str(device_id[i]) + "'")
                 if bool(self.cur.rowcount):
                     try:
                         self.cur.execute("UPDATE " + db_table_ev_daily_consumption +
                                          " SET device_energy=%s, device_energy_from_grid=%s, "
                                          "device_bill=%s, device_total_bill=%s WHERE date = '" + today +
                                          "' AND device_id=%s",
                                          (self.device_energy[device_id[i]],
                                           self.device_energy_from_grid[device_id[i]],
                                           self.device_bill[device_id[i]], self.device_total_bill[device_id[i]],
                                           device_id[i]))
                         self.con.commit()
                         print "Success to Update Postgres"
                     except:
                         print "Cannot update database"
                 else:
                     self.insertDB('daily', device_id[i])

             # Update table "monthly_consumption"
             for i in range(len(device_id)):
                 self.cur.execute("SELECT * FROM " + db_table_ev_monthly_consumption + " WHERE date = '"
                                  + last_day_of_this_month + "' AND device_id = '" + str(device_id[i]) + "'")
                 if bool(self.cur.rowcount):
                     try:
                         self.cur.execute("UPDATE " + db_table_ev_monthly_consumption +
                                          " SET device_energy=%s, device_energy_from_grid=%s, "
                                          "device_bill=%s, device_total_bill=%s WHERE date = '"
                                          + last_day_of_this_month + "' AND device_id=%s",
                                          (self.device_energy_this_month[device_id[i]],
                                           self.device_energy_from_grid_this_month[device_id[i]],
                                           self.device_bill_this_month[device_id[i]],
                                           self.device_total_bill_this_month[device_id[i]],
                                           device_id[i]))
                         self.con.commit()
                         print "Success to Update Postgres"
                     except:
                         print "Cannot update database"
                 else:
                     self.insertDB('monthly', device_id[i])

        def calculate_EV_percentage(self):
            device_id = self.device_status.keys()
            for i in range(len(device_id)):
                time_now = datetime.datetime.now()
                if (self.device_status[device_id[i]] == "ON"):
                    if (self.check_first_time[device_id[i]]):
                        self.check_power[device_id[i]] = self.device_power[device_id[i]]
                        self.percent_charge[device_id[i]] = start_percent_charge
                        self.check_time[device_id[i]] = datetime.datetime.now() + self.time_delta
                        self.check_first_time[device_id[i]] = False
                        self.EV_mode[device_id[i]] = "Charging"
                    if (self.device_power[device_id[i]] >= 1000):
                        if (time_now > self.check_time[device_id[i]]):
                            self.check_time[device_id[i]] = datetime.datetime.now() + self.time_delta
                            if (self.percent_charge[device_id[i]] == 100):
                                self.percent_charge[device_id[i]] = 100
                                self.EV_mode[device_id[i]] = "Charged"
                            else:
                                self.percent_charge[device_id[i]] += 1
                                self.EV_mode[device_id[i]] = "Charging"
                    elif (self.device_power[device_id[i]] > 1) and (self.device_power[device_id[i]] < 1000):
                        if (self.device_power[device_id[i]] > self.check_first_power[device_id[i]]):
                            if (time_now > self.check_time[device_id[i]]):
                                self.check_time[device_id[i]] = datetime.datetime.now() + self.time_delta
                                if (self.percent_charge[device_id[i]] == 100):
                                    self.percent_charge[device_id[i]] = 100
                                    self.EV_mode[device_id[i]] = "Charged"
                                else:
                                    self.percent_charge[device_id[i]] += 1
                                    self.EV_mode[device_id[i]] = "Charging"
                        else:
                            self.percent_charge[device_id[i]] = 100
                            self.EV_mode[device_id[i]] = "Charged"

                elif (self.device_status[device_id[i]] == "OFF"):
                    if (self.check_first_time[device_id[i]]):
                        self.check_power[device_id[i]] = self.device_power[device_id[i]]
                        self.percent_charge[device_id[i]] = 0
                        self.check_time[device_id[i]] = datetime.datetime.now() + self.time_delta
                    self.EV_mode[device_id[i]] = "No Charge"

        @periodic(publish_periodic)
        def publish_message(self):
             topic = '/app/ui/evapp/update_ui/bemoss/999'
             now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
             headers = {
                 'AgentID': self._agent_id,
                 headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                 headers_mod.DATE: now,
                 'receiver_agent_id': "ui"
             }

             self.calculate_daily_bill_compare()
             self.calculate_monthly_bill_compare()

             self.updateDB()

             try:
                 message = json.dumps({"daily_bill_ev": round(sum(self.device_bill.values()), 2),
                                       "daily_bill_ev_percent_compare": round(self.device_bill_compare, 2),
                                       "monthly_bill_ev": round(sum(self.device_bill_this_month.values()), 2),
                                       "monthly_bill_ev_percent_compare": round(self.device_bill_this_month_compare, 2),
                                       "power_ev": round(sum(self.device_power.values()), 2),
                                       "power_from_grid_ev": round(sum(self.device_power_from_grid.values()), 2),
                                       "EV_mode": "No Charge",
                                       "percentage_charge": 0})
             except:
                 message = json.dumps({"daily_bill_ev": 0.00,
                                       "daily_bill_ev_percent_compare": 0.00,
                                       "monthly_bill_ev": 0.00,
                                       "monthly_bill_ev_percent_compare": 0.00,
                                       "power_ev": 0.00,
                                       "power_from_grid_ev": 0.00,
                                       "EV_mode": "No Charge",
                                       "percentage_charge": 0})
             self.publish(topic, headers, message)
             print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)


    Agent.__name__ = 'EVAppAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(EVAppAgent,
                       description='Agent to feed information from grid to UI and other agents',
                       argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass