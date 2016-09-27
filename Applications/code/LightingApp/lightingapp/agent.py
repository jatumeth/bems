# -*- coding: utf-8 -*- {{{
#Author : Nopparat A
#}}}


from datetime import datetime
import logging
import sys
import json
import datetime

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings


utils.setup_logging()
_log = logging.getLogger(__name__)
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
publish_period = 10
NUMBER_DEVICE = 13

class ListenerAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''
    device_status = "OFF"
    check_device_status = "OFF"
    device_start_time = datetime.datetime.now()
    device_stop_time = datetime.datetime.now()
    device_start_time_today = datetime.datetime.now()
    device_start_time_string = device_start_time.strftime('%H:%M:%S %d-%m-%Y')
    device_stop_time_string = device_stop_time.strftime('%H:%M:%S %d-%m-%Y')
    device_status_change_since = device_start_time_string
    on_now_for_string = "0 h 0 min"
    today_current_on_time = 0 #Unit : seconds
    today_last_on_time = 0 #Unit : seconds
    today_on_time_string = "0 h 0 min"
    toggle = 0
    device_brightness = 0
    device_power = 0
    device_energy = 0
    device_bill = 0
    # device_id = ' '

    def __init__(self, config_path, **kwargs):
        super(ListenerAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        # _log.info(self.config['message'])
        self._agent_id = self.config['agent_id']
        # test control air
        # self.publish_heartbeat()
        # Always call the base class setup()
        # self.calculate_on_now_for()
        super(ListenerAgent, self).setup()

    @matching.match_exact('/agent/ui/lighting/device_status_response/bemoss/999/2HUE0017881cab4b')
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        print "--------------------------------------------------"
        print "Topic: {}".format(topic)
        print "Headers: {}".format(headers)
        received_message = json.loads(message[0])
        received_headers = dict(headers)
        print received_message
        print"---------------------------------------------------"
        # {u'status': u'ON', u'color': u'#fff7d0', u'saturation': None, u'brightness': 100}

        # TODO calculate here
        # 1. send on/off
        # 2. calculate on_now_for
        # 3. stamp time for device on first time
        # 4. calculate today_on
        # 5. send current power
        # 6. calculate today_consumption << subscribe message sent to dashboard
        # 7. calculate daily_cost << subscribe message sent to dashboard
        # -----------------------------------------------------
        print "+++++++++++++++++++++++++++++++++++++++++++++"

        print "+++++++++++++++++++++++++++++++++++++++++++++"

# Start TODO #1
        print received_headers['AgentID']
        self.device_status = received_message['status']
        print self.device_status
        self.device_brightness = received_message['brightness']
        print self.device_brightness
        self.device_id = received_headers['AgentID']

        self.calculate_power()
        self.calculate_on_now_for()
        self.calculate_power()


    def check_for_start_new_day(self):
        time_now = datetime.datetime.now()
        start_today_period = time_now.replace(hour=0, minute=0, second=0)
        end_today_period = time_now.replace(hour=23, minute=59, second=0)
        deltatime = datetime.timedelta(minutes=1)
        if ((time_now - start_today_period) < deltatime) & (self.toggle == 0):
            self.today_last_on_time = 0
            self.today_current_on_time = 0
            self.device_energy = 0
            self.device_bill = 0
            self.toggle = 1

        if ((end_today_period - time_now) < deltatime):
            self.toggle = 0


# Start TODO #2 , #3, #4
    def calculate_on_now_for(self):
        time_now = datetime.datetime.now()
        print "Start calculate On_now_for"
        #Check status change from "OFF" to "ON"
        if (self.check_device_status == "OFF") and (self.device_status == "ON"):
            self.device_start_time = time_now
            self.device_start_time_string = self.device_start_time.strftime('%H:%M:%S %d-%m-%Y')
            self.device_status_change_since = self.device_start_time_string
            print self.device_start_time_string
            self.check_device_status = self.device_status
            self.on_now_for_string = " 0 h  0 min"

            self.device_start_time_today = time_now
            self.check_device_status = self.device_status
            print "Status change from OFF to ON"
        #Check status is still "ON"
        elif (self.check_device_status == "ON") and (self.device_status == "ON"):
            on_now_for_time = time_now - self.device_start_time
            hours, remainder = divmod(on_now_for_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.on_now_for_string = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'

            self.today_current_on_time = (time_now - self.device_start_time_today).seconds
            today_on_time = self.today_last_on_time + self.today_current_on_time
            hours, remainder = divmod(today_on_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.today_on_time_string = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'
            print "Status still ON for : {}".format(self.on_now_for_string)
        #Check status change from "ON" to "OFF"
        elif (self.check_device_status == "ON") and (self.device_status == "OFF"):
            self.on_now_for_string = " 0 h  0 min"
            self.check_device_status = self.device_status
            self.device_stop_time = time_now
            self.device_stop_time_string = self.device_stop_time.strftime('%H:%M:%S %d-%m-%Y')
            self.device_status_change_since = self.device_stop_time_string

            self.check_device_status = self.device_status
            self.today_last_on_time = self.today_current_on_time
            self.today_current_on_time = 0
            print "Status change from ON to OFF"
        #Status is still "OFF"
        else:
            self.on_now_for_string = " 0 h  0 min"

# Start TODO #5
    def calculate_power(self):
        '''Actually, the power of a Phillip Hue like exponential as this equation f(x) = 14257e^(0.0153x)
        But for this function will separate the range of HUE's brightness in 3 ranges such as 0 - 25, 25 - 75 and 75 - 100
        Brightness 0 - 25 : f(x) = 0.014 x + 1.565
        Brightness 25 - 75 : f(x) = 0.0516 x + 0.518333
        Brightness 75 - 100 : f(x) = 0.0956 x - 2.675'''

        if (self.device_status == "ON"):
            if (self.device_brightness >= 0) and (self.device_brightness < 25):
                self.device_power = (0.014 * self.device_brightness + 1.565) * NUMBER_DEVICE
            elif (self.device_brightness >= 25) and (self.device_brightness < 75):
                self.device_power = (0.0516 * self.device_brightness + 0.518333) * NUMBER_DEVICE
            else:
                self.device_power = (0.0956 * self.device_brightness - 2.675) * NUMBER_DEVICE
        else:
            self.device_power = 0

# Start TODO #6, #7

    def calculate_today_energy_bill(self):
        time_now = datetime.datetime.now()
        weekday = time_now.weekday()
        start_peak_period = time_now.replace(hour=9, minute=0, second=1)
        end_peak_period = time_now.replace(hour=22, minute=0, second=0)
        self.device_energy += self.device_power * publish_period / 3600 / 1000
        if (weekday == 5) | (weekday == 6) | (weekday == 7):
            self.device_bill += (self.device_power * publish_period / 3600 / 1000) * OFFPEAK_RATE
        else:
            if (time_now > start_peak_period) * (time_now < end_peak_period):
                self.device_bill += (self.device_power * publish_period / 3600 / 1000) * PEAK_RATE
            else:
                self.device_bill += (self.device_power * publish_period / 3600 / 1000) * OFFPEAK_RATE


    @periodic(publish_period)
    def publish_heartbeat(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''

        # TODO this is example how to write an app to control Refrigerator
        topic = '/agent/ui/lighting'
        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
            'data_source': "realtime",
            "agent_id": self.device_id
        }

        self.check_for_start_new_day()
        self.calculate_on_now_for()
        self.calculate_today_energy_bill()
        print self.device_energy

        message = json.dumps({"status": self.device_status, "on_now_for": self.on_now_for_string,
                              "device_status_change_since": self.device_status_change_since,
                              "today_on": self.today_on_time_string, "power": round(self.device_power, 2),
                              "today_energy": round(self.device_energy, 2), "today_bill": round(self.device_bill, 2)})
        self.publish(topic, headers, message)
        print message


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.default_main(ListenerAgent,
                           description='Example VOLTTRON platform™ heartbeat agent',
                           argv=argv)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass