# -*- coding: utf-8 -*- {{{
#Author : Nopparat A
#}}}


from datetime import datetime
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from dateutil.relativedelta import relativedelta
from volttron.platform.messaging import headers as headers_mod

import logging
import sys
import psycopg2
import psycopg2.extras
import json
import datetime
import random
import settings

OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
publish_period = 10

utils.setup_logging()
_log = logging.getLogger(__name__)

def ACAppAgent(config_path, **kwargs):
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
    db_table_ac_daily_consumption = settings.DATABASES['default']['TABLE_ac_daily_consumption']
    db_table_ac_monthly_consumption = settings.DATABASES['default']['TABLE_ac_monthly_consumption']
    # db_table_ac_annual_consumption = settings.DATABASES['default']['TABLE_ac_annual_consumption']

    class Agent(PublishMixin, BaseAgent):

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            self.start_first_time = True
            self.conversion_kWh = 1.0/(3600*1000)
            self.check_day = datetime.datetime.now().weekday()
            self.device_status = {}
            self.device_power = {}
            self.device_power_from_grid = {}
            self.device_current_temp = {}
            self.device_set_temp = {}

            self.device_energy = {}
            self.device_energy_from_grid = {}
            self.device_bill = {}
            self.device_total_bill = {}
            self.power_from_load = 0
            self.power_from_grid_import = 0

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
            # self.get_annual_data()

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

        @matching.match_start('/agent/ui/airconditioner/device_status_response/bemoss/999')
        def on_match_AC(self, topic, headers, message, match):
            '''Use match_all to receive all messages and print them out.'''
            # This for calculate the period of power which got from AC
            print "--------------------------------------------------"
            print "Topic: {}".format(topic)
            print "Headers: {}".format(headers)
            received_message = json.loads(message[0])
            print received_message
            print"---------------------------------------------------"

            device_id = str(received_message['device_id'])
            print device_id
            self.device_status[device_id] = received_message['status']
            self.device_current_temp[device_id] = received_message['current_temperature']
            self.device_set_temp[device_id] = received_message['set_temperature']
            try:
                self.device_power[device_id] = received_message['power']
                return
            except:
                print("")
            self.calculate_power(device_id)
            # self.calculate_device_energy_today(device_id)
            # self.calculate_bill_today(device_id)

            print "+++++++++++++++++++++++++++++++"
            print self.device_power
            print self.device_power_from_grid
            print sum(self.device_energy.values())
            print type(self.device_bill)
            print "+++++++++++++++++++++++++++++++"

        # TODO come back to revise how to calculate power
        def calculate_power(self, device_id):
            delta_temp = self.device_current_temp[device_id] - self.device_set_temp[device_id]
            if (self.device_status[device_id] == "ON"):
                if (delta_temp > 1):
                    if (device_id == 'BedroomAir'):
                        self.device_power[device_id] = random.uniform(750, 800)
                    elif (device_id == 'LivingroomAir1') or (device_id == 'LivingroomAir2'):
                        self.device_power[device_id] = random.uniform(1450, 1500)
                else:
                    if (device_id == 'BedroomAir'):
                        self.device_power[device_id] = random.uniform(400, 600)
                    elif (device_id == 'LivingroomAir1') or (device_id == 'LivingroomAir2'):
                        self.device_power[device_id] = random.uniform(800, 1100)
                    elif (device_id == '1TH20000000000001') or (device_id == '1TH20000000000002'):
                        self.device_power[device_id] = self.device_power[device_id]
            else:
                self.device_power[device_id] = 0

            if (self.power_from_load > self.power_from_grid_import):
                self.device_power_from_grid[device_id] = self.device_power[device_id] * self.power_from_grid_import / self.power_from_load
            else:
                self.device_power_from_grid[device_id] = self.device_power[device_id]

            self.calculate_device_energy_today(device_id)
            self.calculate_bill_today(device_id)
            self.calculate_this_month_device_energy_and_bill(device_id)

        def calculate_device_energy_today(self, device_id):
            # Calculate total energy usage from device
            try:
                self.device_energy[device_id] += self.device_power[device_id] * self.conversion_kWh
            except:
                self.device_energy[device_id] = self.device_power[device_id] * self.conversion_kWh

            # Calculate energy usage of device which recieved from grid
            try:
                self.device_energy_from_grid[device_id] += self.device_power_from_grid[device_id] * self.conversion_kWh
            except:
                self.device_energy_from_grid[device_id] = self.device_power_from_grid[device_id] * self.conversion_kWh


        def calculate_bill_today(self, device_id):
            time_now = datetime.datetime.now()
            weekday = time_now.weekday()
            start_peak_period = time_now.replace(hour=9, minute=0, second=1)
            end_peak_period = time_now.replace(hour=22, minute=0, second=0)

            if ((weekday == 5) or (weekday == 6) or (weekday == 7)): #Holiday have electricity price only OFFPEAK_RATE
                try:
                    self.device_total_bill[device_id] += self.device_power[device_id] * self.conversion_kWh * OFFPEAK_RATE
                    self.device_bill[device_id] += self.device_power_from_grid[device_id] * self.conversion_kWh * OFFPEAK_RATE
                except:
                    self.device_total_bill[device_id] = self.device_power[device_id] * self.conversion_kWh * OFFPEAK_RATE
                    self.device_bill[device_id] = self.device_power_from_grid[device_id] * self.conversion_kWh * OFFPEAK_RATE
            else:
                if (time_now > start_peak_period) and (time_now < end_peak_period):
                    try:
                        self.device_total_bill[device_id] += self.device_power[device_id] * self.conversion_kWh * PEAK_RATE
                        self.device_bill[device_id] += self.device_power_from_grid[device_id] * self.conversion_kWh * PEAK_RATE
                    except:
                        self.device_total_bill[device_id] = self.device_power[device_id] * self.conversion_kWh * PEAK_RATE
                        self.device_bill[device_id] = self.device_power_from_grid[device_id] * self.conversion_kWh * PEAK_RATE
                else:
                    try:
                        self.device_total_bill[device_id] += self.device_power[device_id] * self.conversion_kWh * OFFPEAK_RATE
                        self.device_bill[device_id] += self.device_power_from_grid[device_id] * self.conversion_kWh * OFFPEAK_RATE
                    except:
                        self.device_total_bill[device_id] = self.device_power[device_id] * self.conversion_kWh * OFFPEAK_RATE
                        self.device_bill[device_id] = self.device_power_from_grid[device_id] * self.conversion_kWh * OFFPEAK_RATE

        def start_new_day_checking(self):
            today = datetime.datetime.now().weekday()
            if (((self.check_day == 6) and (self.check_day > today)) or (
                (self.check_day is not 6) and (self.check_day < today))):
                self.start_new_day()
            else:
                pass

        def insertDB(self, table, device_id):
            if (table == 'daily'):
                self.cur.execute("INSERT INTO " + db_table_ac_daily_consumption +
                                 " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date())), device_id,
                                  self.device_energy[device_id], self.device_energy_from_grid[device_id],
                                  self.device_bill[device_id], self.device_total_bill[device_id]))
                self.con.commit()
            elif (table == 'monthly'):
                self.cur.execute("INSERT INTO " + db_table_ac_monthly_consumption +
                                 " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date() + relativedelta(day=31))), device_id,
                                  self.device_energy_this_month[device_id],
                                  self.device_energy_from_grid_this_month[device_id],
                                  self.device_bill_this_month[device_id], self.device_total_bill_this_month[device_id]))

                self.con.commit()
            #
            # elif (table == 'annaul'):
            #     self.cur.execute("INSERT INTO " + db_table_ac_annual_consumption +
            #                      " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
            #                      ((str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))),
            #                       device_id, self.device_energy_annual[device_id],
            #                       self.device_energy_from_grid_annual[device_id],
            #                       self.device_bill_annual[device_id], self.device_total_bill_annual[device_id]))
            #
            #     self.con.commit()

        def get_yesterday_data(self):
            self.device_energy_last_day = {}
            self.device_energy_from_grid_last_day = {}
            self.device_bill_last_day = {}
            self.device_total_bill_last_day = {}

            time_now = datetime.datetime.now()
            last_day = str((time_now - datetime.timedelta(days=1)).date())

            self.cur.execute("SELECT * FROM " + db_table_ac_daily_consumption + " WHERE date = '" + last_day + "'")
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
            self.cur.execute("SELECT * FROM " + db_table_ac_daily_consumption + " WHERE date BETWEEN '" +
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
            self.cur.execute("SELECT * FROM " + db_table_ac_daily_consumption + " WHERE date = '" + today + "'")
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
            self.cur.execute("SELECT * FROM " + db_table_ac_daily_consumption + " WHERE date BETWEEN '" +
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
                self.device_energy_this_month[device_id] = self.device_energy_this_month_until_last_day[device_id] + self.device_energy[device_id]
                self.device_energy_from_grid_this_month[device_id] = self.device_energy_from_grid_this_month_until_last_day[device_id] + self.device_energy_from_grid[device_id]
                self.device_bill_this_month[device_id] = self.device_bill_this_month_until_last_day[device_id] + self.device_bill[device_id]
                self.device_total_bill_this_month[device_id] = self.device_total_bill_this_month_until_last_day[device_id] + self.device_total_bill[device_id]
            except:
                self.device_energy_this_month[device_id] = self.device_energy[device_id]
                self.device_energy_from_grid_this_month[device_id] = self.device_energy_from_grid[device_id]
                self.device_bill_this_month[device_id] = self.device_bill[device_id]
                self.device_total_bill_this_month[device_id] = self.device_total_bill[device_id]

        def calculate_daily_bill_compare(self):
            try:
                self.device_bill_compare = (sum(self.device_bill.values()) - sum(self.device_bill_last_day.values())) / sum(self.device_bill_last_day.values()) * 100
            except:
                self.device_bill_compare = 100

        def calculate_monthly_bill_compare(self):
            try:
                self.device_bill_this_month_compare = (sum(self.device_bill_this_month.values()) - sum(self.device_bill_last_month.values())) / sum(self.device_bill_last_month.values()) * 100
            except:
                self.device_bill_this_month_compare = 100

        @periodic(20)
        def updateDB(self):
            today = str(datetime.datetime.now().date())
            last_day_of_this_month = str(datetime.datetime.now().date() + relativedelta(day=31))
            # last_day_of_end_month = str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))

            device_id = self.device_energy.keys()

            # Update table "daily_consumption"
            for i in range(len(device_id)):
                self.cur.execute("SELECT * FROM " + db_table_ac_daily_consumption + " WHERE date = '" + today +
                                 "' AND device_id = '" + str(device_id[i]) + "'")
                if bool(self.cur.rowcount):
                    try:
                        self.cur.execute("UPDATE " + db_table_ac_daily_consumption +
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
                self.cur.execute("SELECT * FROM " + db_table_ac_monthly_consumption + " WHERE date = '"
                                 + last_day_of_this_month + "' AND device_id = '" + str(device_id[i]) + "'")
                if bool(self.cur.rowcount):
                    try:
                        self.cur.execute("UPDATE " + db_table_ac_monthly_consumption +
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

        @periodic(publish_period)
        def publish_message(self):
            topic = '/app/ui/acapp/update_ui/bemoss/999'
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'receiver_agent_id': "ui"
            }

            self.calculate_daily_bill_compare()
            self.calculate_monthly_bill_compare()

            try:
                message = json.dumps({"daily_bill_AC": round(sum(self.device_bill.values()), 2),
                                      "daily_bill_AC_percent_compare": round(self.device_bill_compare, 2),
                                      "monthly_bill_AC": round(sum(self.device_bill_this_month.values()), 2),
                                      "monthly_bill_AC_percent_compare": round(self.device_bill_this_month_compare, 2),
                                      "power_AC": round(sum(self.device_power.values()), 2),
                                      "power_from_grid_AC": round(sum(self.device_power_from_grid.values()), 2)})
            except:
                message = json.dumps({"daily_bill_AC": 0,
                                      "daily_bill_AC_percent_compare": 0,
                                      "monthly_bill_AC": 0,
                                      "monthly_bill_AC_percent_compare": 0,
                                      "power_AC": 0,
                                      "power_from_grid_AC": 0})
            self.publish(topic, headers, message)
            print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)

    Agent.__name__ = 'ACAppAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(ACAppAgent,
                       description='ACApp agent',
                       argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass