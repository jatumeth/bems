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
from bemoss_lib.energycalculation.energycalculation import last_day_usage

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


    def __init__(self, config_path, **kwargs):
        super(PowermeterAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(PowermeterAppAgent, self).setup()

    @matching.match_exact('/agent/ui/power_meter/device_status_response/bemoss/999/SmappeePowerMeter')
    def on_match_smappee(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        _log.debug("Topic: {topic}, Headers: {headers}, "
                         "Message: {message}".format(
                         topic=topic, headers=headers, message=message))
        message_from_Smappee = json.loads(message[0])
        self.power_from_load = message_from_Smappee['load_activePower']
        self.power_from_solar = message_from_Smappee['solar_activePower']
        self.power_from_grid = message_from_Smappee['grid_activePower']

    @matching.match_start('/agent/ui/')
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        _log.debug("Topic: {topic}, Headers: {headers}, "
                   "Message: {message}".format(
            topic=topic, headers=headers, message=message))
        dict_headers = dict(headers)
        try:
            data_source = dict_headers['data_source']
            if (data_source == "realtime"):
                agent_id = dict_headers['agent_id']
                print agent_id
        except:
            print "No header that interesting"


    # / agent / ui / power_meter / device_status_response / bemoss / 999 / SmappeePowerMeter
    # ['{"grid_phasediff": 0.0, "solar_reactivePower": 98.912, "load_phasediff": 0.0, "db_password": "admin",
    # "solar_quadrant": 0.0, "api": "classAPI_PowerMeter", "addressl": "http://Smappee1006003343.local/gateway/apipublic/logon",
    # "connection_renew_interval": 6000, "volttage": 229.2, "load_apparentPower": 1604.061, "usernameq": {"Authorization": "admin"},
    # "grid_powerfactor": 0.77, "grid_current": 6.995, "solar_activePower": 15.358, "solar_phasediff": 0.0, "offline_count": 0,
    # "grid_quadrant": 0.0, "grid_phaseshift": 0.0, "addressq": "http://Smappee1006003343.local/gateway/apipublic/reportInstantaneousValues",
    # "type": "power_meter", "usernamel": "admin", "grid_activePower": 1247.172, "load_reactivePower": 1008.748, "load_quadrant": 0.0,
    # "load_current": 6.995, "db_port": "5432", "solar_phaseshift": 0.0, "grid_reactivePower": 1008.748, "agent_id": "SmappeePowerMeter",
    # "load_powerfactor": 0.77, "grid_apparentPower": 1604.061, "solar_apparentPower": 100.098, "load_activePower": 1247.172,
    # "db_database": "bemossdb", "load_phaseshift": 0.0, "solar_current": 0.436, "db_user": "admin",
    # "db_host": "localhost", "time": 1474905838.075941, "model": "Smappee", "solar_powerfactor": 0.14}']

    # Demonstrate periodic decorator and settings access
    # @periodic(publish_periodic)
    #
    # def publish_heartbeat(self):
    #     '''Send heartbeat message every HEARTBEAT_PERIOD seconds.
    #
    #     HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
    #     '''
    #     topic = "/agent/ui/dashboard"
    #     now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
    #     headers = {
    #         'AgentID': self._agent_id,
    #         headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
    #         headers_mod.DATE: now,
    #         'data_source': "powermeterApp",
    #     }
    #     message = json.dumps({"monthly_electricity_bill": self.monthly_electricity_bill,
    #                           "last_month_bill": self.last_month_bill,
    #                           "last_month_bill_compare": self.last_month_bill_compare,
    #                           "daily_electricity_bill": self.daily_electricity_bill,
    #                           "last_day_bill": self.last_day_bill,
    #                           "last_day_bill_compare": self.last_day_bill_compare,
    #                           "daily_bill_AC": self.daily_bill_AC,
    #                           "daily_bill_light": self.daily_bill_light,
    #                           "daily_bill_plug": self.daily_bill_plug,
    #                           "daily_bill_EV": self.daily_bill_EV,
    #                           "daily_bill_AC_compare_percent": self.daily_bill_AC_compare_percent,
    #                           "daily_bill_light_compare_percent": self.daily_bill_light_compare_percent,
    #                           "daily_bill_plug_compare_percent": self.daily_bill_plug_compare_percent,
    #                           "daily_bill_EV_compare_percent": self.daily_bill_EV_compare_percent,
    #                           "monthly_bill_AC": self.monthly_bill_AC,
    #                           "monthly_bill_light": self.monthly_bill_light,
    #                           "monthly_bill_plug": self.monthly_bill_plug,
    #                           "monthly_bill_EV": self.daily_bill_EV, #need to fix it
    #                           "monthly_bill_AC_compare_percent": self.monthly_bill_AC_compare_percent,
    #                           "monthly_bill_light_compare_percent": self.monthly_bill_light_compare_percent,
    #                           "monthly_bill_plug_compare_percent": self.monthly_bill_plug_compare_percent,
    #                           "monthly_bill_EV_compare_percent": self.monthly_bill_EV_compare_percent,
    #                           "daily_energy_usage": self.daily_energy_usage,
    #                           "last_day_energy_usage": self.last_day_energy_usage,
    #                           "monthly_energy_usage": self.monthly_energy_usage,
    #                           "last_month_energy_usage": self.last_month_energy_usage,
    #                           "max_monthly_energy_usage": self.max_monthly_energy_usage,
    #                           "max_energy_usage_month": self.max_energy_usage_month,
    #                           "max_energy_usage_year": self.max_energy_usage_year,
    #                           "netzero_condition": self.netzero_condition,
    #                           "netzero_onsite_generation": self.netzero_onsite_generation,
    #                           "netzero_energy_consumption": self.netzero_energy_consumption})
    #     self.publish(topic, headers, message)
    #     print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)


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
