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
import datetime
import random

utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 5
BATT_START_KILOMETER = 50
BATT_MAX_KITLOMETER = 82
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
start_percent_charge = BATT_START_KILOMETER / BATT_MAX_KITLOMETER * 100


class EVAppAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''

    # percent_charge = BATT_START_PERCENTAGE
    time_delta = datetime.timedelta(minutes=2, seconds=28)
    check_time = datetime.datetime.now() + time_delta
    device_status = "OFF"
    check_status = "OFF"
    message_from_EV = {}
    # percent_charge = BATT_START_KILOMETER / BATT_MAX_KITLOMETER * 100
    # EV_bill = 0
    device_power = 0
    device_energy = 0
    device_bill = 0

    def __init__(self, config_path, **kwargs):
        super(EVAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(EVAppAgent, self).setup()

    # @matching.match_all
    # def on_match(self, topic, headers, message, match):
    #     '''Use match_all to receive all messages and print them out.'''
    #     _log.debug("Topic: {topic}, Headers: {headers}, "
    #                      "Message: {message}".format(
    #                      topic=topic, headers=headers, message=message))
    #     print("")

    # TODO
    # 1. Listen status change from smart plug
    # 2. Get status and power
    # 3. Calculate energy from smart plug
    # 4. Calculate EV bill
    # 5. Calculate percentage of EV
    # 6. Check charging status
    # 7. Publish message

#TODO #1 and #2
    @matching.match_start("/agent/ui/plugload/device_status_response/bemoss/999/3WIS221445K1200321")
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        _log.debug("Topic: {topic}, Headers: {headers}, "
                   "Message: {message}".format(
            topic=topic, headers=headers, message=message))
        print message
        self.message_from_EV = json.loads(message[0])
        self.device_status = self.message_from_EV['status']
        self.device_power = self.message_from_EV['power']
        self.calculate_today_energy_bill()
        self.EV_percentage_calculation()
        print self.device_status
        print self.device_power


# TODO #3 and #4
    def calculate_today_energy_bill(self):
        time_now = datetime.datetime.now()
        weekday = time_now.weekday()
        start_peak_period = time_now.replace(hour=9, minute=0, second=1)
        end_peak_period = time_now.replace(hour=22, minute=0, second=0)
        self.device_energy += self.device_power * publish_periodic / 3600 / 1000
        if (weekday == 5) | (weekday == 6) | (weekday == 7):
            self.device_bill += (self.device_power * publish_periodic / 3600 / 1000) * OFFPEAK_RATE
        else:
            if (time_now > start_peak_period) * (time_now < end_peak_period):
                self.device_bill += (self.device_power * publish_periodic / 3600 / 1000) * PEAK_RATE
            else:
                self.device_bill += (self.device_power * publish_periodic / 3600 / 1000) * OFFPEAK_RATE

    def EV_percentage_calculation(self):
        time_now = datetime.datetime.now()
        if (self.device_status == "ON") and (self.device_power > 1000):
            print ("++++++++++++++++++++++++++++++++++++++++++++++++")
            if (self.check_status == "OFF"):
                self.percent_charge = start_percent_charge
            self.check_status = "ON"
            self.percent_batt_V2G = 0

            if (self.percent_charge >= 100):
                self.percent_charge = 100
                self.EV_mode = "Charged"
            else:
                self.EV_mode = "Charging"
                if (time_now > self.check_time):
                    self.percent_charge += 1
                    self.check_time = time_now + self.time_delta

        elif (self.device_status == "ON") and (self.device_power < 1000):
            if not self.device_power:
                self.percent_charge = 0
                self.EV_mode = "No Charge"
            else:
                self.check_status = "ON"
                self.percent_charge = 100
                self.EV_mode = "Charged"
                self.percent_batt_V2G = 0

        elif (self.device_status == "OFF") and (self.check_status == "ON"):
            self.check_status = "OFF"
            self.EV_mode = "No Charge"
            self.percent_batt_V2G = 0
        else:
            self.EV_mode = "No Charge"
            self.percent_batt_V2G = 0
            self.percent_charge = 0


    @periodic(publish_periodic)
    def publish_dashboard(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''
        topic = "/agent/ui/dashboard"
        # topic2 = "/agent/ui/dashboard/EVApp"
        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
            'data_source': "EVApp",
        }

        self.calculate_today_energy_bill()
        self.EV_percentage_calculation()
        print ("from publish")

        message = json.dumps({"EV_mode": self.EV_mode,
                              "percentage_charge": round(self.percent_charge, 2),
                              "percentage_batt_V2G": self.percent_batt_V2G,
                              "EV_bill": self.device_bill,
                              "EV_energy": self.device_energy})

        self.publish(topic, headers, message)
        # self.publish(topic2, headers, message)
        print ("{} published topic: {}, message: {}").format(self._agent_id, topic, message)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(EVAppAgent,
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