# -*- coding: utf-8 -*- {{{
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

import datetime
from dateutil.relativedelta import relativedelta

utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 15
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
    check_daily_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                        'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0, 'solar_energy': 0.0}

    check_last_day_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                        'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0, 'solar_energy': 0.0}

    flag_last_month = False
    flag_this_month = False

    def __init__(self, config_path, **kwargs):
        super(PowermeterAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(PowermeterAppAgent, self).setup()

    # @matching.match_all
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # @matching.match_start("/ui/agent/")
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # Demonstrate periodic decorator and settings access
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
        time_now = datetime.datetime.now()
        delta_time = datetime.timedelta(days=1)
        timedelta = time_now - delta_time
        last_day = timedelta.replace(hour=23, minute=59, second=59)

        daily_data = day_energy_bill_calculation(self.check_daily_data, time_now)
        last_day_data = day_energy_bill_calculation(self.check_daily_data, last_day)

        daily_energy_usage = round(daily_data['daily_energy'], 2)
        daily_electricity_bill = round(daily_data['daily_bill'], 2)
        daily_bill_light = round(daily_data['daily_light_bill'], 2)
        daily_bill_AC = round(daily_data['daily_AC_bill'], 2)
        daily_bill_plug = round(daily_data['daily_plug_bill'], 2)
        daily_bill_EV = round(daily_data['daily_EV_bill'], 2)

        last_day_energy_usage = round(last_day_data['daily_energy'], 2)
        last_day_bill = round(last_day_data['daily_bill'], 2)
        last_day_bill_compare = round(daily_electricity_bill - last_day_bill, 2)
        last_day_bill_light = round(last_day_data['daily_light_bill'], 2)
        last_day_bill_AC = round(last_day_data['daily_AC_bill'], 2)
        last_day_bill_plug = round(last_day_data['daily_plug_bill'], 2)
        last_day_bill_EV = round(last_day_data['daily_EV_bill'], 2)


        monthly_data = monthly_energy_bill_calculation("Current")
        last_month_data = monthly_energy_bill_calculation("Last")

        monthly_energy_usage = round(monthly_data['month_energy'], 2)
        last_month_energy_usage = round(last_month_data['month_energy'], 2)
        monthly_electricity_bill = round(monthly_data['month_bill'], 2)
        last_month_bill = round(last_month_data['month_bill'], 2)
        last_month_bill_compare = round(monthly_electricity_bill-last_month_bill, 2)

        try:
            daily_bill_AC_compare_percent = round(((daily_bill_AC - last_day_bill_AC) / last_day_bill_AC * 100), 2)
        except:
            daily_bill_AC_compare_percent = 100
        try:
            daily_bill_light_compare_percent = round(((daily_bill_light - last_day_bill_light) / last_day_bill_light * 100), 2)
        except:
            daily_bill_light_compare_percent = 100
        try:
            daily_bill_plug_compare_percent = round(((daily_bill_plug - last_day_bill_plug) / last_day_bill_plug * 100), 2)
        except:
            daily_bill_plug_compare_percent = 100
        try:
            daily_bill_EV_compare_percent = round(((daily_bill_EV - last_day_bill_EV) / last_day_bill_EV * 100), 2)
        except:
            daily_bill_EV_compare_percent = 100

        monthly_bill_AC = round(monthly_data['month_AC_bill'], 2)
        monthly_bill_light = round(monthly_data['month_light_bill'], 2)
        monthly_bill_plug = round(monthly_data['month_plug_bill'], 2)
        monthly_bill_EV = round(monthly_data['month_EV_bill'], 2)

        last_month_bill_AC = round(last_month_data['month_AC_bill'], 2)
        last_month_bill_light = round(last_month_data['month_AC_bill'], 2)
        last_month_bill_plug = round(last_month_data['month_plug_bill'], 2)
        last_month_bill_EV = round(last_month_data['month_EV_bill'], 2)

        try:
            monthly_bill_AC_compare_percent = round(((monthly_bill_AC - last_month_bill_AC) / last_month_bill_AC * 100), 2)
        except:
            monthly_bill_AC_compare_percent = 100
        try:
            monthly_bill_light_compare_percent = round(((monthly_bill_light - last_month_bill_light) / last_month_bill_light * 100), 2)
        except:
            monthly_bill_light_compare_percent = 100
        try:
            monthly_bill_plug_compare_percent = round(((monthly_bill_plug - last_month_bill_plug) / last_month_bill_plug * 100), 2)
        except:
            monthly_bill_plug_compare_percent = 100
        try:
            monthly_bill_EV_compare_percent = round(((monthly_bill_EV - last_month_bill_EV) / last_month_bill_EV * 100), 2)
        except:
            monthly_bill_EV_compare_percent = 100

        max_monthly_energy_usage = 300
        month = ["Jan", "Feb", "Mar", "April", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        max_energy_usage_month = month[random.randint(0, 11)]
        max_energy_usage_year = "2016"

        annual_load_energy, annual_solar_energy = annual_energy_calculate()
        netzero_onsite_generation = round(annual_solar_energy, 2)
        netzero_energy_consumption = round(annual_load_energy, 2)

        if (netzero_energy_consumption > netzero_onsite_generation):
            netzero_condition = False
        else:
            netzero_condition = True


        message = json.dumps({"monthly_electricity_bill": monthly_electricity_bill,
                              "last_month_bill": last_month_bill,
                              "last_month_bill_compare": last_month_bill_compare,
                              "daily_electricity_bill": daily_electricity_bill,
                              "last_day_bill": last_day_bill,
                              "last_day_bill_compare": last_day_bill_compare,
                              "daily_bill_AC": daily_bill_AC,
                              "daily_bill_light": daily_bill_light,
                              "daily_bill_plug": daily_bill_plug,
                              "daily_bill_EV": daily_bill_EV,
                              "daily_bill_AC_compare_percent": daily_bill_AC_compare_percent,
                              "daily_bill_light_compare_percent": daily_bill_light_compare_percent,
                              "daily_bill_plug_compare_percent": daily_bill_plug_compare_percent,
                              "daily_bill_EV_compare_percent": daily_bill_EV_compare_percent,
                              "monthly_bill_AC": monthly_bill_AC,
                              "monthly_bill_light": monthly_bill_light,
                              "monthly_bill_plug": monthly_bill_plug,
                              "monthly_bill_EV": monthly_bill_EV,
                              "monthly_bill_AC_compare_percent": monthly_bill_AC_compare_percent,
                              "monthly_bill_light_compare_percent": monthly_bill_light_compare_percent,
                              "monthly_bill_plug_compare_percent": monthly_bill_plug_compare_percent,
                              "monthly_bill_EV_compare_percent": monthly_bill_EV_compare_percent,
                              "daily_energy_usage": daily_energy_usage,
                              "last_day_energy_usage": last_day_energy_usage,
                              "monthly_energy_usage": monthly_energy_usage,
                              "last_month_energy_usage": last_month_energy_usage,
                              "max_monthly_energy_usage": max_monthly_energy_usage,
                              "max_energy_usage_month": max_energy_usage_month,
                              "max_energy_usage_year": max_energy_usage_year,
                              "netzero_condition": netzero_condition,
                              "netzero_onsite_generation": netzero_onsite_generation,
                              "netzero_energy_consumption": netzero_energy_consumption})
        self.publish(topic, headers, message)
        PowermeterAppAgent.check_daily_data = daily_data
        PowermeterAppAgent.check_last_day_data = last_day_data
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
