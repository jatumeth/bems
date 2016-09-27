# -*- coding: utf-8 -*- {{{
from __future__ import division
from datetime import datetime
import logging
import sys

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
import settings
import json
import random
from bemoss_lib.energycalculation.energycalculation import day_energy_bill_calculation
from bemoss_lib.energycalculation.energycalculation import monthly_energy_bill_calculation
from bemoss_lib.energycalculation.energycalculation import annual_energy_calculate
from bemoss_lib.energycalculation.energycalculation import last_day_usage

import datetime
from dateutil.relativedelta import relativedelta

utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 10
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982

#Dictionary of Variables supposed to be saved into timeseries database
log_variables = dict(load_energy='double',solar_energy='double',load_bill='double', light_energy='double',
                     light_bill='double', AC_energy='double', AC_bill='double', plug_energy='double',
                     plug_bill='double', EV_energy='double', EV_bill='double')

class PowermeterAppAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''
    total_today_energy = 0
    total_today_energy_from_solar = 0
    total_today_bill = 0
    power_from_load = 0
    power_from_solar = 0
    power_from_grid = 0
    energy_from_lighting = 0
    bill_from_lighting = 0
    energy_from_AC = 0
    bill_from_AC = 0
    energy_from_EV = 0
    bill_from_EV = 0
    energy_from_plug = 0
    bill_from_plug = 0

    def __init__(self, config_path, **kwargs):
        super(PowermeterAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        self.ac_total_energy = 0
        # Always call the base class setup()
        super(PowermeterAppAgent, self).setup()

    @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
    def on_match_smappee(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #                  "Message: {message}".format(
        #                  topic=topic, headers=headers, message=message))
        message_from_Smappee = json.loads(message[0])
        self.power_from_load = message_from_Smappee['load_activePower']
        self.power_from_solar = message_from_Smappee['solar_activePower']
        self.power_from_grid = message_from_Smappee['grid_activePower']
        self.calculate_total_today_energy_bill(self.power_from_grid, self.power_from_load, self.power_from_solar)
        self.calculate_today_energy_bill_plug()
        self.last_day_compare()
        self.calculate_monthly_energy_bill()
        self.last_month_compare()
        self.annual_energy_calculation()


        # print "1111111111111111111111111111111111111111111111111"
        # self.calculate_total_today_energy_bill(self.power_from_grid, self.power_from_load, self.power_from_solar)
        # print "2222222222222222222222222222222222222222222222222"
        # self.calculate_today_energy_bill_plug()
        # print "3333333333333333333333333333333333333333333333333"
        # self.last_day_compare()
        # print "4444444444444444444444444444444444444444444444444"
        # self.calculate_monthly_energy_bill()
        # print "7777777777777777777777777777777777777777777777777"
        # self.last_month_compare()
        # print "8888888888888888888888888888888888888888888888888"
        # self.annual_energy_calculation()
        # print "9999999999999999999999999999999999999999999999999"


    @matching.match_start('/agent/ui/lighting')
    def on_match_lighting(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(topic=topic, headers=headers, message=message))
        dict_headers = dict(headers)
        try:
            data_source = dict_headers['data_source']
            if (data_source == "realtime"):
                agent_id = dict_headers['agent_id']
                message_from_lighting = json.loads(message[0])
                if (agent_id == '2HUE0017881cab4b'):
                    self.energy_from_lighting = message_from_lighting['today_energy']
                    self.bill_from_lighting = message_from_lighting['today_bill']
                else:
                    print agent_id
            else:
                print "data source is not match"
        except:
            print "No header that interesting"
    #
    #
    @matching.match_start('/agent/ui/airconditioner')
    def on_match_AC(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(topic=topic, headers=headers, message=message))
        dict_headers = dict(headers)
        try:
            data_source = dict_headers['data_source']
            if (data_source == "realtime"):
                message_from_AC = json.loads(message[0])
                dict_energy_from_AC = message_from_AC['today_energy']
                dict_bill_from_AC = message_from_AC['today_bill']
                # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
                self.energy_from_AC = sum(dict_energy_from_AC.values())
                self.bill_from_AC = sum(dict_bill_from_AC.values())
                # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
            else:
                "data source is not match"
        except:
            print "No header that interesting"
    #
    #
    @matching.match_start('/agent/ui/dashboard')
    def on_match_EV(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        # _log.debug("Topic: {topic}, Headers: {headers}, "
        #            "Message: {message}".format(topic=topic, headers=headers, message=message))
        dict_headers = dict(headers)
        try:
            data_source = dict_headers['data_source']
            if (data_source == "EVApp"):
                message_from_EV = json.loads(message[0])
                # {"percentage_batt_V2G": 0, "EV_mode": "No Charge", "EV_bill": 0.0, "percentage_charge": 0.0,
                 # "EV_energy": 0.0}
                self.energy_from_EV = message_from_EV['EV_energy']
                self.bill_from_EV = message_from_EV['EV_bill']
                # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
                # print self.energy_from_EV
                # print self.bill_from_EV
                # print "++++++++++++++++++++++++++++++++++++++++++++++++++++"
            else:
                "data source is not match"
        except:
            print "No header that interesting"

    # def check_for_start_new_day(self):
    #     time_now = datetime.datetime.now()
    #     start_today_period = time_now.replace(hour=0, minute=0, second=0)
    #     end_today_period = time_now.replace(hour=23, minute=59, second=0)
    #     deltatime = datetime.timedelta(minutes=1)
    #     if ((time_now - start_today_period) < deltatime) & (self.toggle == 0):
    #         self.today_last_on_time = 0
    #         self.today_current_on_time = 0
    #         self.device_energy = 0
    #         self.device_bill = 0
    #         self.toggle = 1
    #
    #     if ((end_today_period - time_now) < deltatime):
    #         self.toggle = 0

    def calculate_total_today_energy_bill(self, power_from_grid, power_from_load, power_from_solar):
        time_now = datetime.datetime.now()
        weekday = time_now.weekday()
        start_peak_period = time_now.replace(hour=9, minute=0, second=1)
        end_peak_period = time_now.replace(hour=22, minute=0, second=0)
        self.total_today_energy += power_from_load * publish_periodic / (3600 * 1000)
        self.total_today_energy_from_solar += power_from_solar * publish_periodic / (3600 * 1000)
        if (weekday == 5) | (weekday == 6) | (weekday == 7):
            self.total_today_bill += (power_from_grid * publish_periodic / (3600 * 1000)) * OFFPEAK_RATE
        else:
            if (time_now > start_peak_period) * (time_now < end_peak_period):
                self.total_today_bill += (power_from_grid * publish_periodic / (3600 * 1000)) * PEAK_RATE
            else:
                self.total_today_bill += (power_from_grid * publish_periodic / (3600 * 1000)) * OFFPEAK_RATE

        print self.total_today_energy
        print self.total_today_energy_from_solar
        print self.total_today_bill


    def calculate_today_energy_bill_plug(self):
        if (self.total_today_energy):
            try:
                self.energy_from_plug = self.total_today_energy - (self.energy_from_lighting + self.energy_from_AC + self.energy_from_EV)
            except:
                self.energy_from_plug = 0
        else:
            self.energy_from_plug = 0

        if (self.total_today_bill):
            try:
                self.bill_from_plug = self.total_today_bill - (self.bill_from_lighting + self.bill_from_AC + self.bill_from_EV)
            except:
                self.bill_from_plug = 0
        else:
            self.bill_from_plug = 0
    #
    #
    def last_day_compare(self):
        self.last_day_energy_usage = 62.66
        self.last_day_bill = 250.64
        self.last_day_bill_compare = self.total_today_bill - self.last_day_bill #assume bill from yesterday is 250.64
        try:
            self.daily_bill_AC_compare_percent = ((self.bill_from_AC - 125.32) / 125.32 * 100)
        except:
            self.daily_bill_AC_compare_percent = 100
        try:
            self.daily_bill_light_compare_percent = ((self.bill_from_lighting - 9.60) / 9.6 * 100)
        except:
            self.daily_bill_light_compare_percent = 100
        try:
            self.daily_bill_plug_compare_percent = ((self.bill_from_plug - 61.50) / 61.50 * 100)
        except:
            self.daily_bill_plug_compare_percent = 100
        try:
            self.daily_bill_EV_compare_percent = ((self.bill_from_EV - 54.22) / 54.22 * 100)
        except:
            self.daily_bill_EV_compare_percent = 100

        print ("last day compare ok")
    #
    #
    def calculate_monthly_energy_bill(self):
        #The value is assumed
        self.total_monthly_energy = round(self.total_today_energy + 1620, 2)
        self.total_monthly_bill = round(self.total_today_bill + 6480, 2)
        self.monthly_bill_AC = round(self.bill_from_AC + 3240, 2)
        self.monthly_bill_light = round(self.bill_from_lighting + 248, 2)
        self.monthly_bill_plug = round(self.bill_from_plug + 1590, 2)
        self.monthly_bill_EV = round(self.bill_from_EV + 1402, 2)

        print ("monthly energy ok")

    #
    def last_month_compare(self):
        self.last_month_bill = 1824
        self.last_month_energy_usage = 456.22
        self.last_month_bill_compare = self.total_monthly_bill - self.last_month_bill #assume bill from yesterday is 250.64
        try:
            self.monthly_bill_AC_compare_percent = ((self.monthly_bill_AC - 912) / 125.32 * 100)
        except:
            self.monthly_bill_AC_compare_percent = 100
        try:
            self.monthly_bill_light_compare_percent = ((self.monthly_bill_light - 70.05) / 9.6 * 100)
        except:
            self.monthly_bill_light_compare_percent = 100
        try:
            self.monthly_bill_plug_compare_percent = ((self.monthly_bill_plug - 441.95) / 61.50 * 100)
        except:
            self.monthly_bill_plug_compare_percent = 100
        try:
            self.monthly_bill_EV_compare_percent = ((self.monthly_bill_EV - 400) / 54.22 * 100)
        except:
            self.monthly_bill_EV_compare_percent = 100

        print ("last month energy ok")
    #
    #
    def annual_energy_calculation(self):
        self.netzero_energy_consumption = round(self.total_today_energy + 3759.60, 2)
        self.netzero_onsite_generation = round(self.total_today_energy_from_solar + 680, 2)

        print ("annual energy ok")

    #
    # # Demonstrate periodic decorator and settings access
    @periodic(publish_periodic)

    def publish_heartbeat(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''
        topic = "/agent/ui/dashboard"
        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
            'data_source': "powermeterApp",
        }

        message = json.dumps({"monthly_electricity_bill": round(self.total_monthly_bill, 2),
                              "last_month_bill": round(self.last_month_bill, 2),
                              "last_month_bill_compare": round(self.last_month_bill_compare, 2),
                              "daily_electricity_bill": round(self.total_today_bill, 2),
                              "last_day_bill": round(self.last_day_bill, 2),
                              "last_day_bill_compare": round(self.last_day_bill_compare, 2),
                              "daily_bill_AC": round(self.bill_from_AC, 2),
                              "daily_bill_light": round(self.bill_from_lighting, 2),
                              "daily_bill_plug": round(self.bill_from_plug, 2),
                              "daily_bill_EV": round(self.bill_from_EV, 2),
                              "daily_bill_AC_compare_percent": round(self.daily_bill_AC_compare_percent, 2),
                              "daily_bill_light_compare_percent": round(self.daily_bill_light_compare_percent, 2),
                              "daily_bill_plug_compare_percent": round(self.daily_bill_plug_compare_percent, 2),
                              "daily_bill_EV_compare_percent": round(self.daily_bill_EV_compare_percent, 2),
                              "monthly_bill_AC": round(self.monthly_bill_AC, 2),
                              "monthly_bill_light": round(self.monthly_bill_light, 2),
                              "monthly_bill_plug": round(self.monthly_bill_plug, 2),
                              "monthly_bill_EV": round(self.monthly_bill_EV, 2),
                              "monthly_bill_AC_compare_percent": round(self.monthly_bill_AC_compare_percent, 2),
                              "monthly_bill_light_compare_percent": round(self.monthly_bill_light_compare_percent, 2),
                              "monthly_bill_plug_compare_percent": round(self.monthly_bill_plug_compare_percent, 2),
                              "monthly_bill_EV_compare_percent": round(self.monthly_bill_EV_compare_percent, 2),
                              "daily_energy_usage": round(self.total_today_energy, 2),
                              "last_day_energy_usage": round(self.last_day_energy_usage, 2),
                              "monthly_energy_usage": round(self.total_monthly_energy, 2),
                              "last_month_energy_usage": round(self.last_month_energy_usage, 2),
                              "netzero_onsite_generation": round(self.netzero_onsite_generation, 2),
                              "netzero_energy_consumption": round(self.netzero_energy_consumption, 2)})

        self.publish(topic, headers, message)
        print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(PowermeterAppAgent,
                           description='Agent to feed information from grid to UI and other agents',
                           argv=argv)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
