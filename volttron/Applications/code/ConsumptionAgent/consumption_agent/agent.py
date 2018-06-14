# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:
#
# Copyright 2017, Battelle Memorial Institute.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This material was prepared as an account of work sponsored by an agency of
# the United States Government. Neither the United States Government nor the
# United States Department of Energy, nor Battelle, nor any of their
# employees, nor any jurisdiction or organization that has cooperated in the
# development of these materials, makes any warranty, express or
# implied, or assumes any legal liability or responsibility for the accuracy,
# completeness, or usefulness or any information, apparatus, product,
# software, or process disclosed, or represents that its use would not infringe
# privately owned rights. Reference herein to any specific commercial product,
# process, or service by trade name, trademark, manufacturer, or otherwise
# does not necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors expressed
# herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY operated by
# BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}

from __future__ import absolute_import
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging
import sys
import settings
import os
import json
from pprint import pformat
import subprocess as sp
from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import psycopg2
from os.path import expanduser


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Consumption'
DEFAULT_AGENTID = "consumption"
DEFAULT_HEARTBEAT_PERIOD = 30


def consumption_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_id = get_config('powermeter_device_id')
    topic_powermeter = '/agent/zmq/update/hive/999/' + device_id

    # DATABASES
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']

    class ConsumptionAgent(Agent):

        def __init__(self, config_path, **kwargs):
            super(ConsumptionAgent, self).__init__(**kwargs)
            self.config = utils.load_config(config_path)
            self._agent_id = self.config.get('agentid', DEFAULT_AGENTID)
            self._message = self.config.get('message', DEFAULT_MESSAGE)
            self._heartbeat_period = self.config.get('heartbeat_period',
                                                     DEFAULT_HEARTBEAT_PERIOD)
            self.conn = None
            self.cur = None
            self.automation_control_path = None

        @Core.receiver('onsetup')
        def onsetup(self, sender, **kwargs):
            # Demonstrate accessing a value from the config file
            print('Set up')

            self.first_time = 0
            time_t = datetime.now()

            # Cumulative Data
            self.grid_cum_energy = 0
            self.load_cum_energy = 0
            self.solar_cum_energy = 0
            self.grid_cum_bill = 0
            self.load_cum_bill = 0
            self.solar_cum_bill = 0

            # ----- Type 1.2 -----
            self.kwh_lv1 = 150.00
            self.kwh_lv2 = 400.00
            self.price_lv1 = 3.2484
            self.price_lv2 = 4.2218
            self.price_lv3 = 4.4217

            # ----- Type 1.3 -----
            self.start_peak_period = time_t.replace(hour=9, minute=0, second=0, microsecond=1).time()
            self.end_peak_period = time_t.replace(hour=22, minute=0, second=0, microsecond=0).time()
            self.price_onpeak = 5.7982
            self.price_offpeak = 2.6369
            # --------------------


        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            print("On Start")
            # self.build_automation_agent(55)

        @PubSub.subscribe('pubsub', topic_powermeter)  # Calculate consumption
        def match_topic_create(self, peer, sender, bus,  topic, headers, message):
            print("----- Consumption & Bill Agent -----")
            msg = json.loads(message)

            # self.date_now = datetime.strptime(str(msg['grid_date']),'%Y-%m-%d').weekday()
            self.date_now = datetime.now().weekday()
            print("Weekday = {}".format(self.date_now))

            # self.time_now = datetime.strptime(str(msg['grid_time']),'%H:%M:%S').time()
            self.time_now = datetime.now().time()
            print("Time = {}".format(self.time_now))

            # grid / load / solar data
            self.grid_energy_acc = msg['1_accumulated_energy']
            self.load_energy_acc = msg['grid_accumulated_energy']
            self.solar_energy_acc = msg['2_accumulated_energy']
            self.solar_energy_acc2 = msg['3_accumulated_energy']

            print("<Meter> Grid Accumulated Energy(Wh) = {}".format(self.grid_energy_acc))
            print("<Meter> Load Accumulated Energy(Wh) = {}".format(self.load_energy_acc))
            print("<Meter> Solar Accumulated Energy(Wh) = {}".format(self.solar_energy_acc))
            print("<Meter> Solar2 Accumulated Energy(Wh) = {}".format(self.solar_energy_acc2))

            # Check data = None
            if ((self.grid_energy_acc == 'None') | (self.load_energy_acc == 'None') | (self.solar_energy_acc == 'None')):
                self.grid_energy_now = 0
                self.load_energy_now = 0
                self.solar_energy_now = 0
            else:
                if (self.first_time == 0):

                    self.first_time = 1

                    self.grid_energy_now = 0
                    self.load_energy_now = 0
                    self.solar_energy_now = 0

                    self.grid_energy_acc_old = float(self.grid_energy_acc)
                    self.load_energy_acc_old = float(self.load_energy_acc)
                    # self.solar_energy_acc_old = float(self.solar_energy_acc)
                    self.solar_energy_acc_old = float(self.solar_energy_acc) + float(self.solar_energy_acc2)
                else:
                    self.grid_energy_acc_new = float(self.grid_energy_acc)
                    self.load_energy_acc_new = float(self.load_energy_acc)
                    # self.solar_energy_acc_new = float(self.solar_energy_acc)
                    self.solar_energy_acc_new = float(self.solar_energy_acc) + float(self.solar_energy_acc2)

                    self.grid_energy_now = (self.grid_energy_acc_new - self.grid_energy_acc_old) / 1000
                    self.load_energy_now = (self.load_energy_acc_new - self.load_energy_acc_old) / 1000
                    self.solar_energy_now = (self.solar_energy_acc_new - self.solar_energy_acc_old) / 1000

                    print("Grid Energy(kWh) = {}".format(self.grid_energy_now))
                    print("Load Energy(kWh) = {}".format(self.load_energy_now))
                    print("Solar Energy(kWh) = {}".format(self.solar_energy_now))

                    self.grid_energy_acc_old = self.grid_energy_acc_new
                    self.load_energy_acc_old = self.load_energy_acc_new
                    self.solar_energy_acc_old = self.solar_energy_acc_new

            self.grid_cum_energy += self.grid_energy_now
            self.load_cum_energy += self.load_energy_now
            self.solar_cum_energy += self.solar_energy_now
            print("Grid Cumulated Energy(kWh) = {}".format(self.grid_cum_energy))
            print("Load Cumulated Energy(kWh) = {}".format(self.load_cum_energy))
            print("Solar Cumulated Energy(kWh) = {}".format(self.solar_cum_energy))

            # Calculate Consumption
            self.calculate_consumption()

            # # Daily Data
            # self.calculate_consumption_daily()
            #
            # # Monthly Data
            # self.calculate_consumption_monthly()
            #
            # # Annual Data
            # self.calculate_consumption_annual()

            # Update to firebase
            # self.publish_firebase()

            # Update to Azure IoT hub
            # self.publish_azure_iot_hub()

            # Update to Local
            # self.update_local()

        def calculate_consumption(self):
            # Type 1.2
            self.calculate_consumption_1_2()

            # Type 1.3
            # self.calculate_consumption_1_3()

            #  Cumulative Bill
            self.grid_cum_bill += self.grid_bill_now
            self.load_cum_bill += self.load_bill_now
            self.solar_cum_bill += self.solar_bill_now
            print("Grid Bill(Baht) = {}".format(self.grid_cum_bill))
            print("Load Bill(Baht) = {}".format(self.load_cum_bill))
            print("Solar Bill(Baht) = {}".format(self.solar_cum_bill))


        # --- Type 1.2 TOU ---
        def calculate_consumption_1_2(self):
            print("----- Type 1.2 -----")

            if (self.grid_cum_energy <= self.kwh_lv1):
                self.grid_bill_now = self.grid_energy_now * self.price_lv1
                self.load_bill_now = self.load_energy_now * self.price_lv1
                self.solar_bill_now = self.solar_energy_now * self.price_lv1
                print("Grid Price = {}".format(self.grid_bill_now))
                print("Load Price = {}".format(self.load_bill_now))
                print("Solar Price = {}".format(self.solar_bill_now))

            elif ((self.grid_cum_energy > self.kwh_lv1) & (self.grid_cum_energy >= self.kwh_lv2)):
                self.grid_bill_now = self.grid_energy_now * self.price_lv2
                self.load_bill_now = self.load_energy_now * self.price_lv2
                self.solar_bill_now = self.solar_energy_now * self.price_lv2
                print("Grid Price = {}".format(self.grid_bill_now))
                print("Load Price = {}".format(self.load_bill_now))
                print("Solar Price = {}".format(self.solar_bill_now))
            else:
                self.grid_bill_now = self.grid_energy_now * self.price_lv3
                self.load_bill_now = self.load_energy_now * self.price_lv3
                self.solar_bill_now = self.solar_energy_now * self.price_lv3
                print("Grid Price = {}".format(self.grid_bill_now))
                print("Load Price = {}".format(self.load_bill_now))
                print("Solar Price = {}".format(self.solar_bill_now))

            print("--------------------")

        # --- Type 1.3 TOU ---
        def calculate_consumption_1_3(self):
            print("----- Type 1.3 -----")

            if(self.date_now == 5 | self.date_now == 6):
                self.grid_bill_now = self.grid_energy_now * self.price_offpeak
                self.load_bill_now = self.load_energy_now * self.price_offpeak
                self.solar_bill_now = self.solar_energy_now * self.price_offpeak
                print("Grid Price = {}".format(self.grid_bill_now))
                print("Load Price = {}".format(self.load_bill_now))
                print("Solar Price = {}".format(self.solar_bill_now))
            else:
                if ((self.time_now >= self.start_peak_period) & (self.time_now <= self.end_peak_period)):
                    self.grid_bill_now = self.grid_energy_now * self.price_onpeak
                    self.load_bill_now = self.load_energy_now * self.price_onpeak
                    self.solar_bill_now = self.solar_energy_now * self.price_onpeak
                    print("Grid Price = {}".format(self.grid_bill_now))
                    print("Load Price = {}".format(self.load_bill_now))
                    print("Solar Price = {}".format(self.solar_bill_now))
                else:
                    self.grid_bill_now = self.grid_energy_now * self.price_offpeak
                    self.load_bill_now = self.load_energy_now * self.price_offpeak
                    self.solar_bill_now = self.solar_energy_now * self.price_offpeak
                    print("Grid Price = {}".format(self.grid_bill_now))
                    print("Load Price = {}".format(self.load_bill_now))
                    print("Solar Price = {}".format(self.solar_bill_now))
            print("--------------------")

        # --- Daily Data ---
        # def calculate_consumption_daily(self):
        #
        # # --- Monthly Data ---
        # def calculate_consumption_monthly(self):
        #
        # # --- Annual Data ---
        # def calculate_consumption_annual(self):




    Agent.__name__ = 'consumption'
    return ConsumptionAgent(config_path, **kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''

    try:
        utils.vip_main(consumption_agent, version=__version__)

    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
