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


OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
publish_period = 10
NUMBER_DEVICE = 13

utils.setup_logging()
_log = logging.getLogger(__name__)

def LightingAppAgent(config_path, **kwargs):
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
    db_table_lighting_daily_consumption = settings.DATABASES['default']['TABLE_lighting_daily_consumption']
    db_table_lighting_monthly_consumption = settings.DATABASES['default']['TABLE_lighting_monthly_consumption']

    class Agent(PublishMixin, BaseAgent):

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            self.start_first_time = True
            self.conversion_kWh = publish_period / (3600.0 * 1000.0)
            self.check_day = datetime.datetime.now().weekday()
            self.device_status = {}
            self.device_brightness = {}
            self.device_power = {}
            self.device_power_from_grid = {}
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


        @matching.match_exact('/agent/ui/lighting/device_status_response/bemoss/999/2HUE0017881cab4b')
        def on_match_Lighting(self, topic, headers, message, match):
            print "--------------------------------------------------"
            print "Topic: {}".format(topic)
            print "Headers: {}".format(headers)
            received_message = json.loads(message[0])
            print "Message: {}".format(received_message)
            print"---------------------------------------------------"

            device_id = headers['AgentID']
            self.device_status[device_id] = received_message['status']
            self.device_brightness[device_id] = received_message['brightness']

            self.calculate_power(device_id)

        def calculate_power(self, device_id):
            '''Actually, the power of a Phillip Hue like exponential as this equation f(x) = 14257e^(0.0153x)
             But for this function will separate the range of HUE's brightness in 3 ranges
             such as 0 - 25, 25 - 75 and 75 - 100
             Brightness 0 - 25 : f(x) = 0.014 x + 1.565
             Brightness 25 - 75 : f(x) = 0.0516 x + 0.518333
             Brightness 75 - 100 : f(x) = 0.0956 x - 2.675'''
            if (self.device_status[device_id] == "ON"):
                if (self.device_brightness[device_id] >= 0) and (self.device_brightness[device_id] < 25):
                    self.device_power[device_id] = (0.014 * self.device_brightness[device_id] + 1.565) * NUMBER_DEVICE
                elif (self.device_brightness[device_id] >= 25) and (self.device_brightness[device_id] < 75):
                    self.device_power[device_id] = (0.0516 * self.device_brightness[device_id] + 0.518333) * NUMBER_DEVICE
                else:
                    self.device_power[device_id] = (0.0956 * self.device_brightness[device_id] - 2.675) * NUMBER_DEVICE
            else:
                self.device_power[device_id] = 0

            if (self.power_from_load > self.power_from_grid_import):
                self.device_power_from_grid[device_id] = self.device_power[device_id] * self.power_from_grid_import / self.power_from_load
            else:
                self.device_power_from_grid[device_id] = self.device_power[device_id]


            # self.calculate_device_energy_today(device_id)


        @periodic(publish_period)
        def calculate_device_energy_today(self):
            device_id = self.device_power.keys()
            for i in range(len(device_id)):
                self.calculate_power(device_id[i])
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
            time_now = datetime.datetime.now()
            weekday = time_now.weekday()
            start_peak_period = time_now.replace(hour=9, minute=0, second=1)
            end_peak_period = time_now.replace(hour=22, minute=0, second=0)

            if ((weekday == 5) or (weekday == 6) or (weekday == 7)):  # Holiday have electricity price only OFFPEAK_RATE
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
            if (((self.check_day == 6) and (self.check_day > today)) or ((self.check_day is not 6) and (self.check_day < today))):
                self.start_new_day()
            else:
                pass

        def insertDB(self, table, device_id):
            if (table == 'daily'):
                self.cur.execute("INSERT INTO " + db_table_lighting_daily_consumption +
                                 " VALUES(DEFAULT, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date())), device_id,
                                  self.device_energy[device_id],
                                  self.device_energy_from_grid[device_id],
                                  self.device_bill[device_id], self.device_total_bill[device_id]))
                self.con.commit()
            elif (table == 'monthly'):
                self.cur.execute("INSERT INTO " + db_table_lighting_monthly_consumption +
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
                "SELECT * FROM " + db_table_lighting_daily_consumption + " WHERE date = '" + last_day + "'")
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
            self.cur.execute("SELECT * FROM " + db_table_lighting_daily_consumption + " WHERE date BETWEEN '" +
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
            self.cur.execute("SELECT * FROM " + db_table_lighting_daily_consumption + " WHERE date = '" + today + "'")
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
            self.cur.execute("SELECT * FROM " + db_table_lighting_daily_consumption + " WHERE date BETWEEN '" +
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
            print sum(self.device_bill.values())
            print sum(self.device_bill_last_day.values())
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
                self.cur.execute("SELECT * FROM " + db_table_lighting_daily_consumption + " WHERE date = '" + today +
                                 "' AND device_id = '" + str(device_id[i]) + "'")
                if bool(self.cur.rowcount):
                    try:
                        self.cur.execute("UPDATE " + db_table_lighting_daily_consumption +
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
                self.cur.execute("SELECT * FROM " + db_table_lighting_monthly_consumption + " WHERE date = '"
                                 + last_day_of_this_month + "' AND device_id = '" + str(device_id[i]) + "'")
                if bool(self.cur.rowcount):
                    try:
                        self.cur.execute("UPDATE " + db_table_lighting_monthly_consumption +
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
            topic = '/agent/ui/lighting'
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'data_source': "lightingApp",
                "agent_id": self.device_status.keys()
            }

            self.calculate_daily_bill_compare()
            self.calculate_monthly_bill_compare()

            try:
                message = json.dumps({"daily_bill_lighting": round(sum(self.device_bill.values()), 2),
                                      "daily_bill_lighting_percent_compare": round(self.device_bill_compare, 2),
                                      "monthly_bill_lighting": round(sum(self.device_bill_this_month.values()), 2),
                                      "monthly_bill_lighting_percent_compare": round(self.device_bill_this_month_compare, 2),
                                      "power_lighting": round(sum(self.device_power.values()), 2),
                                      "power_from_grid_lighting": round(sum(self.device_power_from_grid.values()), 2)})
            except:
                message = json.dumps({"daily_bill_lighting": 0.00,
                                      "daily_bill_lighting_percent_compare": 0.00,
                                      "monthly_bill_lighting": 0.00,
                                      "monthly_bill_ligting_percent_compare": 0.00,
                                      "power_lighting": 0.00,
                                      "power_from_grid_lighting": 0.00})
            self.publish(topic, headers, message)
            print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)




                        # class ListenerAgent(PublishMixin, BaseAgent):
#     '''Listens to everything and publishes a heartbeat according to the
#     heartbeat period specified in the settings module.
#     '''
#     device_status = "OFF"
#     check_device_status = "OFF"
#     device_start_time = datetime.datetime.now()
#     device_stop_time = datetime.datetime.now()
#     device_start_time_today = datetime.datetime.now()
#     device_start_time_string = device_start_time.strftime('%H:%M:%S %d-%m-%Y')
#     device_stop_time_string = device_stop_time.strftime('%H:%M:%S %d-%m-%Y')
#     device_status_change_since = device_start_time_string
#     on_now_for_string = "0 h 0 min"
#     today_current_on_time = 0 #Unit : seconds
#     today_last_on_time = 0 #Unit : seconds
#     today_on_time_string = "0 h 0 min"
#     toggle = 0
#     device_brightness = 0
#     device_power = 0
#     device_energy = 0
#     device_bill = 0
#     device_id = ' '
#
#     def __init__(self, config_path, **kwargs):
#         super(ListenerAgent, self).__init__(**kwargs)
#         self.config = utils.load_config(config_path)
#
#     def setup(self):
#         # Demonstrate accessing a value from the config file
#         # _log.info(self.config['message'])
#         self._agent_id = self.config['agent_id']
#         # test control air
#         # self.publish_heartbeat()
#         # Always call the base class setup()
#         # self.calculate_on_now_for()
#         super(ListenerAgent, self).setup()
#
#     @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
#     def on_match_smappee(self, topic, headers, message, match):
#         '''Use match_all to receive all messages and print them out.'''
#         _log.debug("Topic: {topic}, Headers: {headers}, "
#                    "Message: {message}".format(
#             topic=topic, headers=headers, message=message))
#         message_from_Smappee = json.loads(message[0])
#         self.device_power_from_load = message_from_Smappee['load_activePower']
#         self.device_power_from_grid = message_from_Smappee['grid_activePower']
#
#     @matching.match_exact('/agent/ui/lighting/device_status_response/bemoss/999/2HUE0017881cab4b')
#     def on_match(self, topic, headers, message, match):
#         '''Use match_all to receive all messages and print them out.'''
#         print "--------------------------------------------------"
#         print "Topic: {}".format(topic)
#         print "Headers: {}".format(headers)
#         received_headers = dict(headers)
#         received_message = json.loads(message[0])
#         print received_message
#         print"---------------------------------------------------"
#         # {u'status': u'ON', u'color': u'#fff7d0', u'saturation': None, u'brightness': 100}
#
#         # TODO calculate here
#         # 1. send on/off
#         # 2. calculate on_now_for
#         # 3. stamp time for device on first time
#         # 4. calculate today_on
#         # 5. send current power
#         # 6. calculate today_consumption << subscribe message sent to dashboard
#         # 7. calculate daily_cost << subscribe message sent to dashboard
#         # -----------------------------------------------------
#         print "+++++++++++++++++++++++++++++++++++++++++++++"
#
#         print "+++++++++++++++++++++++++++++++++++++++++++++"
#
# # Start TODO #1
#         self.device_status = received_message['status']
#         print self.device_status
#         self.device_brightness = received_message['brightness']
#         print self.device_brightness
#         self.device_id = received_headers['AgentID']
#
#         self.calculate_on_now_for()
#         self.calculate_power()
#
#
#     def check_for_start_new_day(self):
#         time_now = datetime.datetime.now()
#         start_today_period = time_now.replace(hour=0, minute=0, second=0)
#         end_today_period = time_now.replace(hour=23, minute=59, second=0)
#         deltatime = datetime.timedelta(minutes=1)
#         if ((time_now - start_today_period) < deltatime) & (self.toggle == 0):
#             self.today_last_on_time = 0
#             self.today_current_on_time = 0
#             self.device_energy = 0
#             self.device_bill = 0
#             self.toggle = 1
#
#         if ((end_today_period - time_now) < deltatime):
#             self.toggle = 0
#
#
# # Start TODO #2 , #3, #4
#     def calculate_on_now_for(self):
#         time_now = datetime.datetime.now()
#         print "Start calculate On_now_for"
#         #Check status change from "OFF" to "ON"
#         if (self.check_device_status == "OFF") and (self.device_status == "ON"):
#             self.device_start_time = time_now
#             self.device_start_time_string = self.device_start_time.strftime('%H:%M:%S %d-%m-%Y')
#             self.device_status_change_since = self.device_start_time_string
#             print self.device_start_time_string
#             self.check_device_status = self.device_status
#             self.on_now_for_string = " 0 h  0 min"
#
#             self.device_start_time_today = time_now
#             self.check_device_status = self.device_status
#             print "Status change from OFF to ON"
#         #Check status is still "ON"
#         elif (self.check_device_status == "ON") and (self.device_status == "ON"):
#             on_now_for_time = time_now - self.device_start_time
#             hours, remainder = divmod(on_now_for_time.seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             self.on_now_for_string = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'
#
#             self.today_current_on_time = (time_now - self.device_start_time_today).seconds
#             today_on_time = self.today_last_on_time + self.today_current_on_time
#             hours, remainder = divmod(today_on_time, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             self.today_on_time_string = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'
#             print "Status still ON for : {}".format(self.on_now_for_string)
#         #Check status change from "ON" to "OFF"
#         elif (self.check_device_status == "ON") and (self.device_status == "OFF"):
#             self.on_now_for_string = " 0 h  0 min"
#             self.check_device_status = self.device_status
#             self.device_stop_time = time_now
#             self.device_stop_time_string = self.device_stop_time.strftime('%H:%M:%S %d-%m-%Y')
#             self.device_status_change_since = self.device_stop_time_string
#
#             self.check_device_status = self.device_status
#             self.today_last_on_time = self.today_current_on_time
#             self.today_current_on_time = 0
#             print "Status change from ON to OFF"
#         #Status is still "OFF"
#         else:
#             self.on_now_for_string = " 0 h  0 min"
#
# # Start TODO #5
#     def calculate_power(self):
#         '''Actually, the power of a Phillip Hue like exponential as this equation f(x) = 14257e^(0.0153x)
#         But for this function will separate the range of HUE's brightness in 3 ranges such as 0 - 25, 25 - 75 and 75 - 100
#         Brightness 0 - 25 : f(x) = 0.014 x + 1.565
#         Brightness 25 - 75 : f(x) = 0.0516 x + 0.518333
#         Brightness 75 - 100 : f(x) = 0.0956 x - 2.675'''
#
#         if (self.device_status == "ON"):
#             if (self.device_brightness >= 0) and (self.device_brightness < 25):
#                 self.device_power = (0.014 * self.device_brightness + 1.565) * NUMBER_DEVICE
#             elif (self.device_brightness >= 25) and (self.device_brightness < 75):
#                 self.device_power = (0.0516 * self.device_brightness + 0.518333) * NUMBER_DEVICE
#             else:
#                 self.device_power = (0.0956 * self.device_brightness - 2.675) * NUMBER_DEVICE
#         else:
#             self.device_power = 0
#
# # Start TODO #6, #7
#
#     def calculate_today_energy_bill(self):
#         time_now = datetime.datetime.now()
#         weekday = time_now.weekday()
#         start_peak_period = time_now.replace(hour=9, minute=0, second=1)
#         end_peak_period = time_now.replace(hour=22, minute=0, second=0)
#         self.device_energy += self.device_power * publish_period / 3600 / 1000
#         if (weekday == 5) | (weekday == 6) | (weekday == 7):
#             self.device_bill += (self.device_power * self.device_power_from_grid * publish_period / 3600 / 1000 / self.device_power_from_load) * OFFPEAK_RATE
#         else:
#             if (time_now > start_peak_period) * (time_now < end_peak_period):
#                 self.device_bill += (self.device_power * self.device_power_from_grid * publish_period / 3600 / 1000 / self.device_power_from_load) * PEAK_RATE
#             else:
#                 self.device_bill += (self.device_power * self.device_power_from_grid * publish_period / 3600 / 1000 / self.device_power_from_load) * OFFPEAK_RATE
#
#
#     @periodic(publish_period)
#     def publish_heartbeat(self):
#         '''Send heartbeat message every HEARTBEAT_PERIOD seconds.
#
#         HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
#         '''
#
#         # TODO this is example how to write an app to control Refrigerator
#         topic = '/agent/ui/lighting/'
#         now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
#         headers = {
#             'AgentID': self._agent_id,
#             headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
#             headers_mod.DATE: now,
#             'data_source': "realtime",
#             "agent_id": self.device_id
#         }
#
#         self.check_for_start_new_day()
#         self.calculate_on_now_for()
#         self.calculate_today_energy_bill()
#         print self.device_energy
#
#         message = json.dumps({"status": self.device_status, "on_now_for": self.on_now_for_string,
#                               "device_status_change_since": self.device_status_change_since,
#                               "today_on": self.today_on_time_string, "power": round(self.device_power, 2),
#                               "today_energy": round(self.device_energy, 2), "today_bill": round(self.device_bill, 2)})
#         self.publish(topic, headers, message)
#         print message

    Agent.__name__ = 'LightingAppAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(LightingAppAgent,
                           description='LightingApp agent',
                           argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass