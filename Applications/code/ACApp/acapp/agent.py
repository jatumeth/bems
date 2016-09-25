# -*- coding: utf-8 -*- {{{
#Author : Nopparat A
#}}}


from datetime import datetime
import logging
import sys
import json
import datetime
import random

from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod

import settings


utils.setup_logging()
_log = logging.getLogger(__name__)
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
publish_period = 10

class ListenerAgent(PublishMixin, BaseAgent):
    '''Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    '''
    device_status = {}
    check_device_status = {}
    device_start_time = {}
    device_stop_time = {}
    device_start_time_today = {}
    device_start_time_string = {}
    device_stop_time_string = {}
    device_status_change_since = {}
    on_now_for_time = {}
    on_now_for_string = {}
    today_current_on_time = {} #Unit : seconds
    today_last_on_time = {} #Unit : seconds
    today_on_time_string = {}
    toggle = {}
    device_current_temp = {}
    device_set_temp = {}
    device_power = {}
    device_energy = {}
    device_bill = {}

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

    @matching.match_start('/agent/ui/airconditioner/device_status_response/')
    def on_match(self, topic, headers, message, match):
        '''Use match_all to receive all messages and print them out.'''
        print "--------------------------------------------------"
        print "Topic: {}".format(topic)
        print "Headers: {}".format(headers)
        received_message = json.loads(message[0])
        print received_message
        print"---------------------------------------------------"
        # {u'status': u'OFF', u'macaddress': u'20000000000002', u'agent_id': u'1TH20000000000002',
        #  u'db_database': u'bemossdb', u'fin_angle': 0,
        #  u'config_path': u'/home/ibuild06/.volttron/agents/1cb71c10-b694-413b-a3c4-bd58389d4501/acagent-0.1/acagent-0.1.dist-info/config',
        #  u'db_password': u'admin', u'address': u'http://192.168.1.30:49153', u'db_user': u'admin',
        #  u'current_temperature': 23, u'fan_speed': 4, u'api': u'classAPI_KMITL_testNetAirSaijo',
        #  u'db_host': u'localhost', u'mode': u'Cool', u'device_type': u'airconditioner', u'current_humidity': 0,
        #  u'set_humidity': 33, u'model': u'Saijo Denki GPS', u'db_port': u'5432', u'set_temperature': 20,
        #  u'device_id': u'LivingroomAir2'}

        # TODO calculate here
        # 1. send on/off status
        # 2. calculate on_now_for
        # 3. stamp time for device on first time
        # 4. calculate today_on
        # 5. send current power
        # 6. calculate today_consumption << subscribe message sent to dashboard
        # 7. calculate daily_cost << subscribe message sent to dashboard
        # -----------------------------------------------------
        # print "+++++++++++++++++++++++++++++++++++++++++++++"
        #
        # print "+++++++++++++++++++++++++++++++++++++++++++++"

# Start TODO #1

        self.device_id = received_message['device_id']
        self.device_status[self.device_id] = received_message['status']
        print self.device_status
        self.device_current_temp[self.device_id] = received_message['current_temperature']
        print self.device_current_temp
        self.device_set_temp[self.device_id] = received_message['set_temperature']
        print self.device_set_temp
        self.calculate_on_now_for(self.device_id)
        self.calculate_power(self.device_id)
        self.calculate_today_energy_bill(self.device_id)
        self.check_for_start_new_day(self.device_id)
# #
# #
    def check_for_start_new_day(self, device_id):
        time_now = datetime.datetime.now()
        start_today_period = time_now.replace(hour=0, minute=0, second=0)
        end_today_period = time_now.replace(hour=23, minute=59, second=0)
        deltatime = datetime.timedelta(minutes=1)
        if ((time_now - start_today_period) < deltatime) & (self.toggle[device_id] == 0):
            self.today_last_on_time[device_id] = 0
            self.today_current_on_time[device_id] = 0
            self.device_energy[device_id] = 0
            self.device_bill[device_id] = 0
            self.toggle[device_id] = 1

        if ((end_today_period - time_now) < deltatime):
            self.toggle[device_id] = 0
# #
# #
# Start TODO #2 , #3, #4

    def calculate_on_now_for(self, device_id):
        time_now = datetime.datetime.now()
        print "Start calculate On_now_for"

        if device_id in self.check_device_status:
            print "+++++++++++++++++++++++++++++++"
            if (self.check_device_status[device_id] == "OFF") and (self.device_status[device_id] == "ON"):
                self.device_start_time[device_id] = time_now
                self.device_start_time_string[device_id] = self.device_start_time[device_id].strftime('%H:%M:%S %d-%m-%Y')
                self.device_status_change_since[device_id] = self.device_start_time_string[device_id]
                print self.device_start_time_string
                self.check_device_status[device_id] = self.device_status[device_id]
                self.on_now_for_string[device_id] = " 0 h  0 min"

                self.device_start_time_today[device_id] = time_now
                self.check_device_status[device_id] = self.device_status[device_id]
                print "Status change from OFF to ON"
            #Check status is still "ON"
            elif (self.check_device_status[device_id] == "ON") and (self.device_status[device_id] == "ON"):
                on_now_for_time = time_now - self.device_start_time[device_id]
                hours, remainder = divmod(on_now_for_time.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.on_now_for_string[device_id] = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'

                self.today_current_on_time[device_id] = (time_now - self.device_start_time_today[device_id]).seconds
                today_on_time = self.today_last_on_time[device_id] + self.today_current_on_time[device_id]
                hours, remainder = divmod(today_on_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.today_on_time_string[device_id] = str(hours) + ' ' + 'h' + ' ' + str(minutes) + ' ' + 'min'
                print "Status still ON for : {}".format(self.on_now_for_string[device_id])
            #Check status change from "ON" to "OFF"
            elif (self.check_device_status[device_id] == "ON") and (self.device_status[device_id] == "OFF"):
                self.on_now_for_string[device_id] = " 0 h  0 min"
                self.check_device_status[device_id] = self.device_status[device_id]
                self.device_stop_time[device_id] = time_now
                self.device_stop_time_string[device_id] = self.device_stop_time[device_id].strftime('%H:%M:%S %d-%m-%Y')
                self.device_status_change_since[device_id] = self.device_stop_time_string[device_id]

                self.check_device_status[device_id] = self.device_status[device_id]
                self.today_last_on_time[device_id] = self.today_current_on_time[device_id]
                self.today_current_on_time[device_id] = 0
                print "Status change from ON to OFF"
            #Status is still "OFF"
            else:
                self.on_now_for_string[device_id] = " 0 h  0 min"
        else:
            print "--------------------------------------"
            self.check_device_status[device_id] = self.device_status[device_id]
            self.on_now_for_string[device_id] = " 0 h  0 min"
            self.today_current_on_time[device_id] = 0
            self.today_last_on_time[device_id] = 0
            self.device_energy[device_id] = 0
            self.device_bill[device_id] = 0
            self.toggle[device_id] = 0
            if (self.device_status[device_id] == "ON"):
                self.device_start_time[device_id] = time_now
                self.device_start_time_string[device_id] = self.device_start_time[device_id].strftime('%H:%M:%S %d-%m-%Y')
                self.device_status_change_since[device_id] = self.device_start_time_string[device_id]
                self.device_start_time_today[device_id] = time_now
            else:
                self.device_stop_time[device_id] = time_now
                self.device_stop_time_string[device_id] = self.device_stop_time[device_id].strftime('%H:%M:%S %d-%m-%Y')
                self.device_status_change_since[device_id] = self.device_stop_time_string[device_id]
# # #
# Start TODO #5
    def calculate_power(self, device_id):
        print ("current temp = {}".format(self.device_current_temp[device_id]))
        print ("set temp = {}".format(self.device_set_temp[device_id]))
        delta_temp = self.device_current_temp[device_id] - self.device_set_temp[device_id]
        if (self.device_status[device_id] == "ON"):
            if (delta_temp > 1):
                if (device_id == 'BedroomAir'):
                    self.device_power[device_id] = round(random.uniform(750, 800), 2)
                else:
                    self.device_power[device_id] = round(random.uniform(1450, 1500), 2)
            elif (delta_temp > 0) and (delta_temp <= 1):
                if (device_id == 'BedroomAir'):
                    self.device_power[device_id] = round(random.uniform(600, 700), 2)
                else:
                    self.device_power[device_id] = round(random.uniform(1000, 1100), 2)
            else:
                self.device_power[device_id] = round(random.uniform(0, 100), 2)
        else:
            self.device_power[device_id] = 0
#
# Start TODO #6, #7
#
    def calculate_today_energy_bill(self, device_id):
        time_now = datetime.datetime.now()
        weekday = time_now.weekday()
        start_peak_period = time_now.replace(hour=9, minute=0, second=1)
        end_peak_period = time_now.replace(hour=22, minute=0, second=0)
        self.device_energy[device_id] += round(self.device_power[device_id] * publish_period / 3600 / 1000, 2)
        if (weekday == 5) | (weekday == 6) | (weekday == 7):
            self.device_bill[device_id] += round((self.device_power[device_id] * publish_period / 3600 / 1000) * OFFPEAK_RATE, 2)
        else:
            if (time_now > start_peak_period) * (time_now < end_peak_period):
                self.device_bill[device_id] += round((self.device_power[device_id] * publish_period / 3600 / 1000) * PEAK_RATE, 2)
            else:
                self.device_bill[device_id] += round((self.device_power[device_id] * publish_period / 3600 / 1000) * OFFPEAK_RATE, 2)
# #
# #
    @periodic(publish_period)
    def publish_heartbeat(self):
        '''Send heartbeat message every HEARTBEAT_PERIOD seconds.

        HEARTBEAT_PERIOD is set and can be adjusted in the settings module.
        '''

        # TODO this is example how to write an app to control Refrigerator
        topic = '/agent/ui/airconditioner'
        now = datetime.datetime.utcnow().isoformat(' ') + 'Z'
        headers = {
            'AgentID': self._agent_id,
            headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
            headers_mod.DATE: now,
            'data_source': "realtime",
            "agent_id": self.device_status.keys()
        }
        #
        # if not self.device_status:
        #     print "No message from AC"
        # else:
        #     self.check_for_start_new_day(self.device_id)
        #     self.calculate_on_now_for(self.device_id)
        #     self.calculate_today_energy_bill(self.device_id)

        message = json.dumps({"status": self.device_status, "on_now_for": self.on_now_for_string,
                              "device_status_change_since": self.device_status_change_since,
                              "today_on": self.today_on_time_string,
                              "power": self.device_power,
                              "today_energy": self.device_energy,
                              "today_bill": self.device_bill})
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