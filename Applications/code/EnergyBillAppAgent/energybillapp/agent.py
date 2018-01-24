from __future__ import division
#from datetime import datetime
from datetime import *
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
#from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import *
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
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    # db_table_daily_consumption = settings.DATABASES['default']['TABLE_daily_consumption']
    db_table_daily_consumption = "daily_consumption"
    db_table_weekly_consumption = "weekly_consumption"
    db_table_monthly_consumption = settings.DATABASES['default']['TABLE_monthly_consumption']
    db_table_annual_consumption = settings.DATABASES['default']['TABLE_annual_consumption']
    # db_table_cumulative_energy = settings.DATABASES['default']['TABLE_cumulative_energy']
    db_table_cumulative_energy = "cumulative_consumption"

    class Agent(PublishMixin, BaseAgent):
        '''Calculate energy and bill from evergy power sources'''

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs

            self.start_first_time = True
            self.check_day = datetime.datetime.now().weekday()
            self.check_week = datetime.datetime.now().isocalendar()[1]
            self.check_month = datetime.datetime.now().month
            self.check_year = datetime.datetime.now().year
            self.current_electricity_price = 0
            self.gateway_id = settings.gateway_id
            print('++++++++++++++++++++++++++++++++')
            print('gateway_id : {}'.format(self.gateway_id))

            # try:
            #     self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database,
            #                                 user=db_user, password=db_password)
            #     self.cur = self.con.cursor()
            #     print ("{} connects to the database name {} successfully".format(agent_id, db_database))
            #
            # except:
            #     print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))

        def set_variable(self, k, v):  # postgre k=key, v=value
            self.variables[k] = v

        def get_variable(self, k):
            return self.variables.get(k, None)  # default of get variable is none

        def setup(self):
            super(Agent, self).setup()
            # Demonstrate accessing value from the config file
            _log.info(config['message'])
            self._agent_id = agent_id
            self.get_yesterday_data()
            self.get_today_data()
            self.get_last_week_data()
            self.get_this_week_data()
            self.get_last_month_data()
            self.get_this_month_data()
            self.get_annual_data()

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
            self.get_this_week_data()
            self.get_this_month_data()

        def start_new_week(self):
            self.load_energy_this_week = 0
            self.solar_energy_this_week = 0
            self.grid_import_energy_this_week = 0
            self.grid_export_energy_this_week = 0
            self.load_bill_this_week = 0
            self.solar_bill_this_week = 0
            self.grid_import_bill_this_week = 0
            self.grid_export_bill_this_week = 0
            self.get_last_week_data()

        def start_new_month(self):
            self.load_energy_this_month = 0
            self.solar_energy_this_month = 0
            self.grid_import_energy_this_month = 0
            self.grid_export_energy_this_month = 0
            self.load_bill_this_month = 0
            self.solar_bill_this_month = 0
            self.grid_import_bill_this_month = 0
            self.grid_export_bill_this_month = 0
            self.get_last_month_data()

        def start_new_year(self):
            self.load_energy_annual = 0
            self.solar_energy_annual = 0
            self.grid_import_energy_annual = 0
            self.grid_export_energy_annual = 0
            self.load_bill_annual = 0
            self.solar_bill_annual = 0
            self.grid_import_bill_annual = 0
            self.grid_export_bill_annual = 0

        @matching.match_start('/app/ui/grid/update_ui/bemoss/999')
        def on_match_gridappagent(self, topic, headers, message, match):
            message_from_gridApp = json.loads(message[0])
            self.current_electricity_price = message_from_gridApp['current_electricity_price']
            print "Current electricity price : {}".format(self.current_electricity_price)

        # etrix
        @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/5PMCP009')
        def on_match_etrix(self, topic, headers, message, match):
            print "Hello from E-trix"
            message_from_power_meter = json.loads(message[0])
            # self.energy_from_load = message_from_power_meter['load_energy']
            self.energy_from_load = 0
            # self.energy_from_solar = float(message_from_power_meter['solar_energy'])
            self.energy_from_solar = 0
            if (message_from_power_meter['grid_energy'] > 0):
                self.energy_from_grid_import = message_from_power_meter['grid_energy']
                self.energy_from_grid_export = 0
            else:
                self.energy_from_grid_export = message_from_power_meter['grid_energy']
                self.energy_from_grid_import = 0

            self.calculate_energy_bill()

        def calculate_energy_bill(self):
            self.start_new_day_checking()
            self.calculate_energy_today()
            self.calculate_bill_today()
            self.calculate_this_week_energy_and_bill()
            self.calculate_this_month_energy_and_bill()
            self.calculate_annual_energy_and_bill()
            self.updateDB()
            self.publish_message()

        # inverter
        # @matching.match_exact('/agent/ui/PVInverter/device_status_response/bemoss/999/1PV221445K1200138')
        # smappee
        # @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/5Smappee001')
        # def on_match_smappee(self, topic, headers, message, match):
        #     print "Hello from Smappee"
        #     message_from_power_meter = json.loads(message[0])
        #     self.power_from_load = message_from_power_meter['grid_activePower']
        #     # self.power_from_solar = float(message_from_power_meter['solar_activePower'])
        #     self.power_from_solar = 0
        #     if (message_from_power_meter['grid_activePower'] > 0):
        #         self.power_from_grid_import = message_from_power_meter['grid_activePower']
        #         self.power_from_grid_export = 0
        #     else:
        #         self.power_from_grid_export = message_from_power_meter['grid_activePower']
        #         self.power_from_grid_import = 0
        #
        #     # This for calculate the period of power which got from Inverter
        #     if (self.start_first_time):
        #         self.conversion_kWh = 0
        #         self.last_time = datetime.datetime.now()
        #         self.start_first_time = False
        #     else:
        #         time_now = datetime.datetime.now()
        #         timedelta_period = time_now - self.last_time
        #         self.conversion_kWh = timedelta_period.seconds / (3600.0 * 1000.0)
        #         print "conversion = {}".format(self.conversion_kWh)
        #         self.last_time = time_now
        #
        #     self.start_new_day_checking()
        #     self.calculate_energy_today()
        #     self.calculate_bill_today()
        #     self.calculate_this_week_energy_and_bill()
        #     self.calculate_this_month_energy_and_bill()
        #     self.calculate_annual_energy_and_bill()
        #     self.updateDB()
        #     self.publish_message()

        # def calculate_energy_today_smappee(self):
        #     # Calculate Energy from Grid_import
        #     self.grid_import_energy_today += self.power_from_grid_import * self.conversion_kWh
        #     self.set_variable('gridImportEnergy', self.grid_import_energy_today)
        #     # Calculate Energy from Grid_export
        #     self.grid_export_energy_today += self.power_from_grid_export * self.conversion_kWh
        #     self.set_variable('gridExportEnergy', self.grid_export_energy_today)
        #     # Calculate Energy from Solar
        #     self.solar_energy_period = self.power_from_solar * self.conversion_kWh
        #     self.solar_energy_today += self.solar_energy_period
        #     self.set_variable('solarEnergy', self.solar_energy_today)
        #     # Calculate Energy from Load
        #     self.load_energy_period = self.power_from_load * self.conversion_kWh
        #     self.load_energy_today += self.load_energy_period
        #     self.set_variable('loadEnergy', self.load_energy_today)

        # def calculate_bill_today_smappee(self):
        #     grid_import_bill_current_time = self.power_from_grid_import * self.conversion_kWh * self.current_electricity_price
        #     grid_export_bill_current_time = self.power_from_grid_export * self.conversion_kWh * self.current_electricity_price
        #     solar_bill_current_time = self.power_from_solar * self.conversion_kWh * self.current_electricity_price
        #     load_bill_current_time = self.power_from_load * self.conversion_kWh * self.current_electricity_price
        #
        #     self.grid_import_bill_today += grid_import_bill_current_time
        #     self.grid_export_bill_today += grid_export_bill_current_time
        #     self.solar_bill_today += solar_bill_current_time
        #     self.load_bill_today += load_bill_current_time
        #
        #     self.set_variable('gridImportBill', self.grid_import_bill_today)
        #     self.set_variable('gridExportBill', self.grid_export_bill_today)
        #     self.set_variable('solarBill', self.solar_bill_today)
        #     self.set_variable('loadBill', self.load_bill_today)

        def calculate_energy_today(self):
            # Calculate Energy from Grid_import
            self.grid_import_energy_today += self.energy_from_grid_import
            self.set_variable('gridImportEnergy', self.grid_import_energy_today)
            # Calculate Energy from Grid_export
            self.grid_export_energy_today += self.energy_from_grid_export
            self.set_variable('gridExportEnergy', self.grid_export_energy_today)
            # Calculate Energy from Solar
            self.solar_energy_today += self.energy_from_solar
            self.set_variable('solarEnergy', self.solar_energy_today)
            # Calculate Energy from Load
            self.load_energy_today += self.energy_from_load
            self.set_variable('loadEnergy', self.load_energy_today)

        def calculate_bill_today(self):
            grid_import_bill_current_time = self.energy_from_grid_import * self.current_electricity_price
            grid_export_bill_current_time = self.energy_from_grid_export * self.current_electricity_price
            solar_bill_current_time = self.energy_from_solar * self.current_electricity_price
            load_bill_current_time = self.energy_from_load * self.current_electricity_price

            self.grid_import_bill_today += grid_import_bill_current_time
            self.grid_export_bill_today += grid_export_bill_current_time
            self.solar_bill_today += solar_bill_current_time
            self.load_bill_today += load_bill_current_time

            self.set_variable('gridImportBill', self.grid_import_bill_today)
            self.set_variable('gridExportBill', self.grid_export_bill_today)
            self.set_variable('solarBill', self.solar_bill_today)
            self.set_variable('loadBill', self.load_bill_today)

        def start_new_day_checking(self):
            today = datetime.datetime.now().weekday()
            if ((self.check_day == 6) and (self.check_day > today)) or (
                (self.check_day is not 6) and (self.check_day < today)):
                self.start_new_day()
                self.check_day = today
                # self.insertDB()
            else:
                pass

        def connect_postgresdb(self):
            try:
                self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
                                            password=db_password)
                self.cur = self.con.cursor()  # open a cursor to perfomm database operations
                print("{} connects to the database name {} successfully".format(agent_id, db_database))
            except Exception as er:
                print er
                print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))

        def disconnect_postgresdb(self):
            if(self.con.closed == False):
                self.con.close()
            else:
                print("postgresdb is not connected")


        def start_new_week_checking(self):
            this_week = datetime.datetime.now().isocalendar()[1]
            if ((self.check_week == 53) and (self.check_week > this_week)) or (
                (self.check_week is not 53) and (self.check_week < this_week)):
                self.start_new_week()
                self.check_week = this_week
                # self.insertDB()
            else:
                pass

        def start_new_month_checking(self):
            this_month = datetime.datetime.now().month
            if ((self.check_month == 12) and (self.check_month > this_month)) or (
                (self.check_month is not 12) and (self.check_month < this_month)):
                self.start_new_month()
                self.check_month = this_month
            else:
                pass

        def start_new_year_checking(self):
            this_year = datetime.datetime.now().year
            if self.check_year < this_year:
                self.start_new_year()
                self.check_year = this_year
            else:
                pass

        def insertDB(self, table):
            if (table == 'daily'):
                self.connect_postgresdb()
                self.cur.execute("INSERT INTO " + db_table_daily_consumption +
                                 " (datetime, gridimportenergy, gridexportenergy, solarenergy, loadenergy, "
                                 "gridimportbill, gridexportbill, solarbill, loadbill, updated_at, gateway_id) "
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date())),
                                  self.get_variable('gridImportEnergy'), self.get_variable('gridExportEnergy'),
                                  self.get_variable('solarEnergy'), self.get_variable('loadEnergy'),
                                  self.get_variable('gridImportBill'), self.get_variable('gridExportBill'),
                                  self.get_variable('solarBill'), self.get_variable('loadBill'),
                                  datetime.datetime.now(), self.gateway_id))
                self.con.commit()
                self.disconnect_postgresdb()

            elif (table == 'weekly'):
                self.connect_postgresdb()
                self.cur.execute("INSERT INTO " + db_table_weekly_consumption +
                                 " (datetime, gridimportenergy, gridexportenergy, solarenergy, loadenergy, "
                                 "gridimportbill, gridexportbill, solarbill, loadbill, updated_at, gateway_id) "
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                 ((str((datetime.datetime.now() - relativedelta(weekday=MO(-1))).date())),
                                  self.grid_import_energy_this_week, self.grid_export_energy_this_week,
                                  self.solar_energy_this_week, self.load_energy_this_week,
                                  self.grid_import_bill_this_week, self.grid_export_bill_this_week,
                                  self.solar_bill_this_week, self.load_bill_this_week, datetime.datetime.now(), self.gateway_id))
                self.con.commit()
                self.disconnect_postgresdb()

            elif (table == 'monthly'):
                self.connect_postgresdb()
                self.cur.execute("INSERT INTO " + db_table_monthly_consumption +
                                 " (datetime, gridimportenergy, gridexportenergy, solarenergy, loadenergy, "
                                 "gridimportbill, gridexportbill, solarbill, loadbill, updated_at, gateway_id) "
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().date() + relativedelta(day=31))),
                                  self.grid_import_energy_this_month, self.grid_export_energy_this_month,
                                  self.solar_energy_this_month, self.load_energy_this_month,
                                  self.grid_import_bill_this_month, self.grid_export_bill_this_month,
                                  self.solar_bill_this_month, self.load_bill_this_month, datetime.datetime.now(), self.gateway_id))
                self.con.commit()
                self.disconnect_postgresdb()

            elif (table == 'annual'):
                self.connect_postgresdb()
                self.cur.execute("INSERT INTO " + db_table_annual_consumption +
                                 " (datetime, gridimportenergy, gridexportenergy, solarenergy, loadenergy, "
                                 "gridimportbill, gridexportbill, solarbill, loadbill, updated_at, gateway_id) "
                                 "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                 ((str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))),
                                  self.grid_import_energy_annual, self.grid_export_energy_annual,
                                  self.solar_energy_annual, self.load_energy_annual,
                                  self.grid_import_bill_annual, self.grid_export_bill_annual,
                                  self.solar_bill_annual, self.load_bill_annual, datetime.datetime.now(), self.gateway_id))
                self.con.commit()
                self.disconnect_postgresdb()

            elif (table == 'cumulative'):
                self.connect_postgresdb()
                self.cur.execute("INSERT INTO " + db_table_cumulative_energy +
                                 " (datetime, grid_consumption, load_consumption, solar_consumption, gateway_id) "
                                 "VALUES(%s, %s, %s, %s, %s)",
                                 (datetime.datetime.now(), self.energy_from_grid_import, self.energy_from_load, self.energy_from_solar, self.gateway_id))

                self.con.commit()
                self.disconnect_postgresdb()
                print"insert to db:Success"


        # @periodic(10)
        def updateDB(self):
            try:
                self.insertDB('cumulative')
            except Exception as er:
                print "insert data base error: {}".format(er)
            today = str(datetime.datetime.now().date())
            this_week = str((datetime.datetime.now() - relativedelta(weekday=MO(-1))).date())
            last_day_of_this_month = str(datetime.datetime.now().date() + relativedelta(day=31))
            last_day_of_end_month = str(datetime.datetime.now().replace(month=12).date() + relativedelta(day=31))

            # Update table "daily_consumption"
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime = '" + today + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute(
                        "UPDATE " + db_table_daily_consumption + " SET gridimportenergy=%s, gridexportenergy=%s, "
                                                                 "solarenergy=%s, loadenergy=%s, gridimportbill=%s,"
                                                                 "gridexportbill=%s, solarbill=%s, loadbill=%s, updated_at=%s, gateway_id=%s"
                                                                 " WHERE datetime = '" + today + "'",
                        (self.get_variable('gridImportEnergy'), self.get_variable('gridExportEnergy'),
                         self.get_variable('solarEnergy'), self.get_variable('loadEnergy'),
                         self.get_variable('gridImportBill'), self.get_variable('gridExportBill'),
                         self.get_variable('solarBill'), self.get_variable('loadBill'), datetime.datetime.now(), self.gateway_id))
                    self.con.commit()
                    self.disconnect_postgresdb()
                    print"update daily db:Success"
                except Exception as er:
                    print "update data base error: {}".format(er)
            else:
                self.insertDB('daily')

            # Update table "weekly consumption"
            self.connect_postgresdb()
            self.cur.execute(
                "SELECT * FROM " + db_table_weekly_consumption + " WHERE datetime = '" + this_week + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute(
                        "UPDATE " + db_table_weekly_consumption + " SET gridimportenergy=%s, gridexportenergy=%s, "
                                                                  "solarenergy=%s, loadenergy=%s, gridimportbill=%s,"
                                                                  "gridexportbill=%s, solarbill=%s, loadbill=%s, gateway_id=%s"
                                                                  " WHERE datetime = '" + this_week + "'",
                        (self.grid_import_energy_this_week, self.grid_export_energy_this_week,
                         self.solar_energy_this_week, self.load_energy_this_week,
                         self.grid_import_bill_this_week, self.grid_export_bill_this_week,
                         self.solar_bill_this_week, self.load_bill_this_week, self.gateway_id))

                    self.con.commit()
                    self.disconnect_postgresdb()
                    print"update weekly db:Success"
                except Exception as er:
                    print "update data base error: {}".format(er)
            else:
                self.insertDB('weekly')

            # Update table "monthly consumption"
            self.connect_postgresdb()
            self.cur.execute(
                "SELECT * FROM " + db_table_monthly_consumption + " WHERE datetime = '" + last_day_of_this_month + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute(
                        "UPDATE " + db_table_monthly_consumption + " SET gridimportenergy=%s, gridexportenergy=%s, "
                                                                   "solarenergy=%s, loadenergy=%s, gridimportbill=%s,"
                                                                   "gridexportbill=%s, solarbill=%s, loadbill=%s, gateway_id=%s"
                                                                   " WHERE datetime = '" + last_day_of_this_month + "'",
                        (self.grid_import_energy_this_month, self.grid_export_energy_this_month,
                         self.solar_energy_this_month, self.load_energy_this_month,
                         self.grid_import_bill_this_month, self.grid_export_bill_this_month,
                         self.solar_bill_this_month, self.load_bill_this_month, self.gateway_id))

                    self.con.commit()
                    self.disconnect_postgresdb()
                    print"update monthly db:Success"
                except Exception as er:
                    print "update data base error: {}".format(er)
            else:
                self.insertDB('monthly')

            # Update table "annual consumption"
            self.connect_postgresdb()
            self.cur.execute(
                "SELECT * FROM " + db_table_annual_consumption + " WHERE datetime = '" + last_day_of_end_month + "'")
            if bool(self.cur.rowcount):
                try:
                    self.cur.execute(
                        "UPDATE " + db_table_annual_consumption + " SET gridimportenergy=%s, gridexportenergy=%s, "
                                                                  "solarenergy=%s, loadenergy=%s, gridimportbill=%s,"
                                                                  "gridexportbill=%s, solarbill=%s, loadbill=%s, gateway_id=%s"
                                                                  " WHERE datetime = '" + last_day_of_end_month + "'",
                        (self.grid_import_energy_annual, self.grid_export_energy_annual,
                         self.solar_energy_annual, self.load_energy_annual,
                         self.grid_import_bill_annual, self.grid_export_bill_annual,
                         self.solar_bill_annual, self.load_bill_annual, self.gateway_id))

                    self.con.commit()
                    self.disconnect_postgresdb()
                    print"update annual db:Success"
                except Exception as er:
                    print "update data base error: {}".format(er)
            else:
                self.insertDB('annual')

        def get_yesterday_data(self):
            time_now = datetime.datetime.now()
            last_day = str((time_now - datetime.timedelta(days=1)).date())
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime = '" + last_day + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()[0]
                self.grid_import_energy_last_day = float(data[1])
                self.grid_export_energy_last_day = float(data[2])
                self.solar_energy_last_day = float(data[3])
                self.load_energy_last_day = float(data[4])
                self.grid_import_bill_last_day = float(data[5])
                self.grid_export_bill_last_day = float(data[6])
                self.solar_bill_last_day = float(data[7])
                self.load_bill_last_day = float(data[8])
            else:
                self.grid_import_energy_last_day = 0
                self.grid_export_energy_last_day = 0
                self.solar_energy_last_day = 0
                self.load_energy_last_day = 0
                self.grid_import_bill_last_day = 0
                self.grid_export_bill_last_day = 0
                self.solar_bill_last_day = 0
                self.load_bill_last_day = 0

            self.disconnect_postgresdb()

        def get_last_week_data(self):
            self.grid_import_energy_last_week = 0
            self.grid_export_energy_last_week = 0
            self.solar_energy_last_week = 0
            self.load_energy_last_week = 0
            self.grid_import_bill_last_week = 0
            self.grid_export_bill_last_week = 0
            self.solar_bill_last_week = 0
            self.load_bill_last_week = 0

            first_date = (datetime.datetime.now()-relativedelta(weeks=1, weekday=MO(-1))).date()
            end_date = first_date + relativedelta(days=+6)
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.grid_import_energy_last_week += float(data[i][1])
                    self.grid_export_energy_last_week += float(data[i][2])
                    self.solar_energy_last_week += float(data[i][3])
                    self.load_energy_last_week += float(data[i][4])
                    self.grid_import_bill_last_week += float(data[i][5])
                    self.grid_export_bill_last_week += float(data[i][6])
                    self.solar_bill_last_week += float(data[i][7])
                    self.load_bill_last_week += float(data[i][8])
            else:
                pass

            self.disconnect_postgresdb()

        def get_last_month_data(self):
            self.grid_import_energy_last_month = 0
            self.grid_export_energy_last_month = 0
            self.solar_energy_last_month = 0
            self.load_energy_last_month = 0
            self.grid_import_bill_last_month = 0
            self.grid_export_bill_last_month = 0
            self.solar_bill_last_month = 0
            self.load_bill_last_month = 0

            first_date = (datetime.datetime.now() - relativedelta(months=1)).replace(day=1).date()
            end_date = first_date + relativedelta(day=31)
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.grid_import_energy_last_month += float(data[i][1])
                    self.grid_export_energy_last_month += float(data[i][2])
                    self.solar_energy_last_month += float(data[i][3])
                    self.load_energy_last_month += float(data[i][4])
                    self.grid_import_bill_last_month += float(data[i][5])
                    self.grid_export_bill_last_month += float(data[i][6])
                    self.solar_bill_last_month += float(data[i][7])
                    self.load_bill_last_month += float(data[i][8])
            else:
                pass

            self.disconnect_postgresdb()

        def get_today_data(self):
            today = str(datetime.datetime.now().date())
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime = '" + today + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()[0]
                self.grid_import_energy_today = float(data[1])
                self.grid_export_energy_today = float(data[2])
                self.solar_energy_today = float(data[3])
                self.load_energy_today = float(data[4])
                self.grid_import_bill_today = float(data[5])
                self.grid_export_bill_today = float(data[6])
                self.solar_bill_today = float(data[7])
                self.load_bill_today = float(data[8])
            else:
                self.start_new_day()

            self.disconnect_postgresdb()

        def get_this_week_data(self):
            self.grid_import_energy_this_week_until_last_day = 0
            self.grid_export_energy_this_week_until_last_day = 0
            self.solar_energy_this_week_until_last_day = 0
            self.load_energy_this_week_until_last_day = 0
            self.grid_import_bill_this_week_until_last_day = 0
            self.grid_export_bill_this_week_until_last_day = 0
            self.solar_bill_this_week_until_last_day = 0
            self.load_bill_this_week_until_last_day = 0

            first_date = (datetime.datetime.now() - relativedelta(weekday=MO(-1))).date()
            end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.grid_import_energy_this_week_until_last_day += float(data[i][1])
                    self.grid_export_energy_this_week_until_last_day += float(data[i][2])
                    self.solar_energy_this_week_until_last_day += float(data[i][3])
                    self.load_energy_this_week_until_last_day += float(data[i][4])
                    self.grid_import_bill_this_week_until_last_day += float(data[i][5])
                    self.grid_export_bill_this_week_until_last_day += float(data[i][6])
                    self.solar_bill_this_week_until_last_day += float(data[i][7])
                    self.load_bill_this_week_until_last_day += float(data[i][8])
            else:
                self.start_new_week()

            self.disconnect_postgresdb()

        def get_this_month_data(self):
            self.grid_import_energy_this_month_until_last_day = 0
            self.grid_export_energy_this_month_until_last_day = 0
            self.solar_energy_this_month_until_last_day = 0
            self.load_energy_this_month_until_last_day = 0
            self.grid_import_bill_this_month_until_last_day = 0
            self.grid_export_bill_this_month_until_last_day = 0
            self.solar_bill_this_month_until_last_day = 0
            self.load_bill_this_month_until_last_day = 0

            first_date = datetime.datetime.now().replace(day=1).date()
            end_date = datetime.datetime.now() - datetime.timedelta(days=1)
            first_date_str = str(first_date)
            end_date_str = str(end_date)
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_daily_consumption + " WHERE datetime BETWEEN '" +
                             first_date_str + "' AND '" + end_date_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.grid_import_energy_this_month_until_last_day += float(data[i][1])
                    self.grid_export_energy_this_month_until_last_day += float(data[i][2])
                    self.solar_energy_this_month_until_last_day += float(data[i][3])
                    self.load_energy_this_month_until_last_day += float(data[i][4])
                    self.grid_import_bill_this_month_until_last_day += float(data[i][5])
                    self.grid_export_bill_this_month_until_last_day += float(data[i][6])
                    self.solar_bill_this_month_until_last_day += float(data[i][7])
                    self.load_bill_this_month_until_last_day += float(data[i][8])
            else:
                self.start_new_month()

            self.disconnect_postgresdb()

        def get_annual_data(self):
            self.grid_import_energy_annual_until_last_month = 0
            self.grid_export_energy_annual_until_last_month = 0
            self.solar_energy_annual_until_last_month = 0
            self.load_energy_annual_until_last_month = 0
            self.grid_import_bill_annual_until_last_month = 0
            self.grid_export_bill_annual_until_last_month = 0
            self.solar_bill_annual_until_last_month = 0
            self.load_bill_annual_until_last_month = 0

            first_month = datetime.datetime.now().replace(month=1, day=31).date()
            this_month = (datetime.datetime.now() - datetime.timedelta(days=31) + relativedelta(day=31)).date()
            first_month_str = str(first_month)
            this_month_str = str(this_month)
            self.connect_postgresdb()
            self.cur.execute("SELECT * FROM " + db_table_monthly_consumption + " WHERE datetime BETWEEN '" +
                             first_month_str + "' AND '" + this_month_str + "'")
            if bool(self.cur.rowcount):
                data = self.cur.fetchall()
                for i in range(len(data)):
                    self.grid_import_energy_annual_until_last_month += float(data[i][1])
                    self.grid_export_energy_annual_until_last_month += float(data[i][2])
                    self.solar_energy_annual_until_last_month += float(data[i][3])
                    self.load_energy_annual_until_last_month += float(data[i][4])
                    self.grid_import_bill_annual_until_last_month += float(data[i][5])
                    self.grid_export_bill_annual_until_last_month += float(data[i][6])
                    self.solar_bill_annual_until_last_month += float(data[i][7])
                    self.load_bill_annual_until_last_month += float(data[i][8])
            else:
                self.start_new_year()

            self.disconnect_postgresdb()

        def calculate_this_week_energy_and_bill(self):
            self.grid_import_energy_this_week = self.grid_import_energy_this_week_until_last_day + self.grid_import_energy_today
            self.grid_export_energy_this_week = self.grid_export_energy_this_week_until_last_day + self.grid_export_energy_today
            self.solar_energy_this_week = self.solar_energy_this_week_until_last_day + self.solar_energy_today
            self.load_energy_this_week = self.load_energy_this_week_until_last_day + self.load_energy_today
            self.grid_import_bill_this_week = self.grid_import_bill_this_week_until_last_day + self.grid_import_bill_today
            self.grid_export_bill_this_week = self.grid_export_bill_this_week_until_last_day + self.grid_export_bill_today
            self.solar_bill_this_week = self.solar_bill_this_week_until_last_day + self.solar_bill_today
            self.load_bill_this_week = self.load_bill_this_week_until_last_day + self.load_bill_today

        def calculate_this_month_energy_and_bill(self):
            self.grid_import_energy_this_month = self.grid_import_energy_this_month_until_last_day + self.grid_import_energy_today
            self.grid_export_energy_this_month = self.grid_export_energy_this_month_until_last_day + self.grid_export_energy_today
            self.solar_energy_this_month = self.solar_energy_this_month_until_last_day + self.solar_energy_today
            self.load_energy_this_month = self.load_energy_this_month_until_last_day + self.load_energy_today
            self.grid_import_bill_this_month = self.grid_import_bill_this_month_until_last_day + self.grid_import_bill_today
            self.grid_export_bill_this_month = self.grid_export_bill_this_month_until_last_day + self.grid_export_bill_today
            self.solar_bill_this_month = self.solar_bill_this_month_until_last_day + self.solar_bill_today
            self.load_bill_this_month = self.load_bill_this_month_until_last_day + self.load_bill_today

        def calculate_annual_energy_and_bill(self):
            self.grid_import_energy_annual = self.grid_import_energy_annual_until_last_month + self.grid_import_energy_this_month
            self.grid_export_energy_annual = self.grid_export_energy_annual_until_last_month + self.grid_export_energy_this_month
            self.solar_energy_annual = self.solar_energy_annual_until_last_month + self.solar_energy_this_month
            self.load_energy_annual = self.load_energy_annual_until_last_month + self.load_energy_this_month
            self.grid_import_bill_annual = self.grid_import_bill_annual_until_last_month + self.grid_import_bill_this_month
            self.grid_export_bill_annual = self.grid_export_bill_annual_until_last_month + self.grid_export_bill_this_month
            self.solar_bill_annual = self.solar_bill_annual_until_last_month + self.solar_bill_this_month
            self.load_bill_annual = self.load_bill_annual_until_last_month + self.load_bill_this_month

        # @periodic(publish_periodic)
        def publish_message(self):
            topic = "/app/ui/energybillapp/update_ui/bemoss/999"
            now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': self._agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                headers_mod.DATE: now,
                'receiver_agent_id': "ui"
            }
            try:
                message = json.dumps(({"daily_energy_usage": round(self.get_variable('loadEnergy'), 2),
                                       "last_day_energy_usage": round(self.load_energy_last_day, 2),
                                       "daily_electricity_bill": round(self.get_variable('gridImportBill'), 2),
                                       "last_day_bill_compare": round(
                                           self.get_variable('gridImportBill') - self.grid_import_bill_last_day, 2),
                                       "monthly_energy_usage": round(self.load_energy_this_month, 2),
                                       "last_month_energy_usage": round(self.load_energy_last_month, 2),
                                       "monthly_electricity_bill": round(self.grid_import_bill_this_month, 2),
                                       "last_month_bill_compare": round(
                                           (self.grid_import_bill_this_month - self.grid_import_bill_last_month), 2),
                                       "netzero_onsite_generation": round(self.solar_energy_annual, 2),
                                       "netzero_energy_consumption": round(self.load_energy_annual, 2)}))

                self.publish(topic, headers, message)
                print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)
            except:
                pass

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