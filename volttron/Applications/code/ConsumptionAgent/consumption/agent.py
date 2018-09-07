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
import pyrebase


utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Consumption'
DEFAULT_AGENTID = "consumption"
DEFAULT_HEARTBEAT_PERIOD = 30

apiKeyconfig = settings.CHANGE['change']['apiKeyLight']
authDomainconfig = settings.CHANGE['change']['authLight']
dataBaseconfig = settings.CHANGE['change']['databaseLight']
stoRageconfig = settings.CHANGE['change']['storageLight']

try:
    config = {
        "apiKey": apiKeyconfig,
        "authDomain": authDomainconfig,
        "databaseURL": dataBaseconfig,
        "storageBucket": stoRageconfig,
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except Exception as er:
    print er

def consumption_agent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    agent_id = get_config('agent_id')
    print(agent_id)
    message = get_config('message')
    heartbeat_period = get_config('heartbeat_period')
    device_id = get_config('powermeter_device_id')
    topic_powermeter = '/agent/zmq/update/hive/999/' + device_id
    print(topic_powermeter)
    typecal = get_config('type_cal')
    gateway_id = settings.gateway_id

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

            self.first_time = 1
            time_t = datetime.now()
            self.this_month = time_t.month
            self.max_energy = 0
            self.max_bill = 0

            # Cumulative Data
            self.grid_energy_month = 0
            self.grid_bill_month = 0

            # ----- Type 1.1 -----
            self.kwh_1lv1 = 15.00
            self.kwh_1lv2 = 25.00
            self.kwh_1lv3 = 35.00
            self.kwh_1lv4 = 100.00
            self.kwh_1lv5 = 150.00
            self.kwh_1lv6 = 400.00
            self.price_1lv1 = 2.3488 # 1-15
            self.price_1lv2 = 2.9882 # 16-25
            self.price_1lv3 = 3.2405 # 26-35
            self.price_1lv4 = 3.6237 # 36-100
            self.price_1lv5 = 3.7171 # 101-150
            self.price_1lv6 = 4.2218 # 151-400
            self.price_1lv7 = 4.4217 # 401-

            # ----- Type 1.2 -----
            self.kwh_2lv1 = 150.00
            self.kwh_2lv2 = 400.00
            self.price_2lv1 = 3.2484 # 1-150
            self.price_2lv2 = 4.2218 # 151-400
            self.price_2lv3 = 4.4217 # 401-

            # ----- Type 1.3 -----
            self.start_peak_period = time_t.replace(hour=9, minute=0, second=0, microsecond=1).time()
            self.end_peak_period = time_t.replace(hour=22, minute=0, second=0, microsecond=0).time()
            self.price_onpeak = 5.7982 # onpeak
            self.price_offpeak = 2.6369 # offpeak

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            print("On Start")
            # self.build_automation_agent(55)

        @PubSub.subscribe('pubsub', topic_powermeter)  # Calculate consumption
        def match_topic_create(self, peer, sender, bus,  topic, headers, message):
            print("----- Consumption & Bill Agent -----")
            msg = json.loads(message)
            print(msg)

            # datetime now
            time_n = datetime.now()

            self.date_now = time_n.weekday()
            # self.date_now = datetime.strptime(str(msg['grid_date']),'%Y-%m-%d').weekday()
            print("Weekday = {}".format(self.date_now))

            self.time_now = time_n.time()
            # self.time_now = datetime.strptime(str(msg['grid_time']),'%H:%M:%S').time()
            print("Time = {}".format(self.time_now))

            # grid
            self.grid_energy_acc = msg['grid_accumulated_energy']
            print("<Meter> Grid Accumulated Energy(Wh) = {}".format(self.grid_energy_acc))

            # Check data = None
            if (self.grid_energy_acc == 'None'):
                self.grid_energy_now = 0

            else:
                if (self.first_time == 1):

                    self.grid_energy_now = 0
                    self.grid_energy_acc_old = float(self.grid_energy_acc)
                    self.first_time = 0
                    self.month_now = time_n.month
                    print("Month now = {}".format(self.month_now))

                else:
                    self.grid_energy_acc_new = float(self.grid_energy_acc)
                    self.grid_energy_now = (self.grid_energy_acc_new - self.grid_energy_acc_old) / 1000
                    self.grid_energy_acc_old = self.grid_energy_acc_new
                    self.month_now = time_n.month
                    print("Grid Energy(kWh) = {}".format(self.grid_energy_now))
                    print("Month now = {}".format(self.month_now))

            # Check New Month
            if (self.month_now == self.this_month):
                self.calculate_consumption()

            else: # new month
                self.this_month = self.month_now
                self.grid_energy_month = 0
                self.grid_bill_month = 0
                self.calculate_consumption()

                # check max value
                if (self.grid_energy_month > self.max_energy):
                    self.max_energy = self.grid_energy_month
                    self.max_bill = self.grid_bill_month

            # Update to firebase
            self.publish_firebase()

            # Update to Azure IoT hub
            # self.publish_azure_iot_hub()

            # Update to Local
            # self.update_local()

        def calculate_consumption(self):

            #  Monthly Energy
            self.grid_energy_month += self.grid_energy_now
            print("Monthly Grid Energy(kWh) = {}".format(self.grid_energy_month))

            if (typecal == "1.1"):
                self.calculate_consumption_11()

            elif (typecal == "1.2"):
                self.calculate_consumption_12()

            elif (typecal == "1.3"):
                self.calculate_consumption_13()

            else:
                print("please choose type cal.")

            #  Monthly Bill
            self.grid_bill_month += self.grid_bill_now
            print("Monthly Grid Bill(Baht) = {}".format(self.grid_bill_month))

        # --- Type 1.1 ---
        def calculate_consumption_11(self):
            if (self.grid_energy_month <= self.kwh_1lv1):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv1
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_1lv1) & (self.grid_energy_month >= self.kwh_1lv2)):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv2
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_1lv2) & (self.grid_energy_month >= self.kwh_1lv3)):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv3
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_1lv3) & (self.grid_energy_month >= self.kwh_1lv4)):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv4
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_1lv4) & (self.grid_energy_month >= self.kwh_1lv5)):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv5
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_1lv6) & (self.grid_energy_month >= self.kwh_1lv7)):
                self.grid_bill_now = self.grid_energy_now * self.price_1lv6
                print("Grid Price = {}".format(self.grid_bill_now))

            else:
                self.grid_bill_now = self.grid_energy_now * self.price_1lv7
                print("Grid Price = {}".format(self.grid_bill_now))

        # --- Type 1.2 ---
        def calculate_consumption_12(self):
            if (self.grid_energy_month <= self.kwh_2lv1):
                self.grid_bill_now = self.grid_energy_now * self.price_2lv1
                print("Grid Price = {}".format(self.grid_bill_now))

            elif ((self.grid_energy_month > self.kwh_2lv1) & (self.grid_energy_month >= self.kwh_2lv2)):
                self.grid_bill_now = self.grid_energy_now * self.price_2lv2
                print("Grid Price = {}".format(self.grid_bill_now))

            else:
                self.grid_bill_now = self.grid_energy_now * self.price_2lv3
                print("Grid Price = {}".format(self.grid_bill_now))

        # --- Type 1.3 ---
        def calculate_consumption_13(self):
            if(self.date_now == 5 | self.date_now == 6):
                self.grid_bill_now = self.grid_energy_now * self.price_offpeak
                print("Grid Price = {}".format(self.grid_bill_now))

            else:
                if ((self.time_now >= self.start_peak_period) & (self.time_now <= self.end_peak_period)):
                    self.grid_bill_now = self.grid_energy_now * self.price_onpeak
                    print("Grid Price = {}".format(self.grid_bill_now))

                else:
                    self.grid_bill_now = self.grid_energy_now * self.price_offpeak
                    print("Grid Price = {}".format(self.grid_bill_now))


        def publish_firebase(self):
            try:
                # # consumption - current energy(now)
                # db.child(gateway_id).child('energy').child('consumption').child('current').set(self.grid_energy_now)
                # # consumption - monthly energy
                # db.child(gateway_id).child('energy').child('consumption').child('monthly').set(self.grid_energy_month)
                # # consumption - max monthly energy
                # db.child(gateway_id).child('energy').child('consumption').child('max_monthly').set(self.max_energy)
                # # consumption - current bill(now)
                # db.child(gateway_id).child('energy').child('bill').child('current').set(self.grid_bill_now)
                # # consumption - monthly bill
                # db.child(gateway_id).child('energy').child('bill').child('monthly').set(self.grid_bill_month)
                # # consumption - max monthly bill
                # db.child(gateway_id).child('energy').child('bill').child('max_monthly').set(self.max_bill)

                # temp data
                db.child(gateway_id).child('energy').child('daily_energy').child('gridimportenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('daily_energy').child('gridimportbill').set(self.grid_bill_month)
                db.child(gateway_id).child('energy').child('daily_energy').child('loadenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('daily_energy').child('loadbill').set(self.grid_bill_month)
                db.child(gateway_id).child('energy').child('monthly_energy').child('gridimportenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('monthly_energy').child('gridimportbill').set(self.grid_bill_month)
                db.child(gateway_id).child('energy').child('monthly_energy').child('loadenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('monthly_energy').child('loadbill').set(self.grid_bill_month)
                db.child(gateway_id).child('energy').child('annual_energy').child('gridimportenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('annual_energy').child('gridimportbill').set(self.grid_bill_month)
                db.child(gateway_id).child('energy').child('annual_energy').child('loadenergy').set(self.grid_energy_month)
                db.child(gateway_id).child('energy').child('annual_energy').child('loadbill').set(self.grid_bill_month)

            except Exception as er:
                print er

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
