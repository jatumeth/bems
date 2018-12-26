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
from collections import OrderedDict
import collections
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

# set up for firebase
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

    # Config. file
    agent_id = get_config('agent_id')

    device_id = get_config('device_id')
    print('device_id = {}'.format(device_id))
    topic_device = '/agent/zmq/update/hive/999/' + device_id
    type_consumption = get_config('type_consumption')
    date_bill = get_config('date_bill')
    limit_bill = get_config('limit_bill')
    gateway_id = settings.gateway_id
    print('gateway_id = {}'.format(gateway_id))

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
            self.first_time = 1

            self.max_energy_cum_monthly = 0
            self.max_bill_cum_monthly = 0

            # date for daily E&B & date for monthly E&B
            time_n = datetime.now()
            self.this_day = time_n.date()
            print('this day = {}'.format(self.this_day))

            if (date_bill <= self.this_day.day):
                self.date_start = time_n.replace(day=date_bill).date()
                self.date_end = self.date_start + relativedelta(months=+1) - relativedelta(days=+1)
            else:
                self.date_end = time_n.replace(day=date_bill-1).date()
                self.date_start = self.date_end - relativedelta(months=+1) + relativedelta(days=+1)
            print('date start = {}'.format(self.date_start))
            print('date end = {}'.format(self.date_end))

            # Total Data
            self.total_energy = {'grid': 0, 'load': 0, 'solar': 0}
            self.total_bill = {'grid': 0, 'load': 0, 'solar': 0}

            # Cumulative Data
            self.energy_cum_daily = {'grid': 0, 'load': 0, 'solar': 0}
            self.bill_cum_daily = {'grid': 0, 'load': 0, 'solar': 0}
            self.energy_cum_monthly = {'grid': 0, 'load': 0, 'solar': 0}
            self.bill_cum_monthly = {'grid': 0, 'load': 0, 'solar': 0}

            # percent type
            self.percent_energy = {'grid': 0, 'load': 0, 'solar': 0}
            self.percent_bill = {'grid': 0, 'load': 0, 'solar': 0}

            # bill type 1.1
            self.price_1_1 = {'type':'step', 0:2.3488, 15:2.9882, 25:3.2405, 35:3.6237, 100:3.7171, 150:4.2218, 400:4.4217}

            # bill type 1.2
            self.price_1_2 = {'type':'step', 0:3.2484, 150:4.2218, 400:4.4217}

            # bill type 1.3
            self.price_1_3 = {'type': 'tou',
                              'on': 5.7982, 'off': 2.6369,
                              'tstart': datetime.now().replace(hour=9, minute=0, second=0, microsecond=1).time(),
                              'tstop': datetime.now().replace(hour=22, minute=0, second=0, microsecond=0).time()}

            # bill type 6.1
            self.price_6_1 = {'type': 'step', 0: 2.8013, 10: 3.8919}

        @Core.receiver('onstart')
        def onstart(self, sender, **kwargs):
            # type price
            self.list_type_consumption = {'1.1': self.type_1_1(), '1.2': self.type_1_2(), '1.3': self.type_1_3(), '6.1': self.type_6_1()}
            self.type_bill = self.list_type_consumption[type_consumption]
            print('type bill = {}'.format(self.type_bill))

            # read from firebase
            if (db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_grid').get().val() != None):
                print('Read from firebase')
                self.total_energy = {
                    'grid': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_grid').get().val(),
                    'load': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_load').get().val(),
                    'solar': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_solar').get().val()
                    }

                self.total_bill = {
                    'grid': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_grid').get().val(),
                    'load': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_load').get().val(),
                    'solar': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_solar').get().val()
                    }

                print('Total energy = {}'.format(self.total_energy))
                print('Total bill = {}'.format(self.total_bill))

                try:
                    if ((datetime.strptime((db.child(gateway_id).child('energy').child(device_id).child('dateinfo').get()).val(), '%Y-%m-%d')).date() == self.this_day):
                        self.energy_cum_daily = {
                            'grid': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_grid').get().val(),
                            'load': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_load').get().val(),
                            'solar': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_solar').get().val()
                            }

                        self.bill_cum_daily = {
                            'grid': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_grid').get().val(),
                            'load': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_load').get().val(),
                            'solar': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_solar').get().val()
                            }

                        print('Energy cum daily = {}'.format(self.energy_cum_daily))
                        print('Bill cum daily = {}'.format(self.bill_cum_daily))

                except:
                    print('Data is None (Daily)')

                try:
                    if ((datetime.strptime((db.child(gateway_id).child('energy').child(device_id).child('monthinfo').get()).val(), '%Y-%m-%d')).date() >= self.this_day):
                        self.energy_cum_monthly = {
                            'grid': db.child(gateway_id).child('energy').child(device_id).child('month').child('energy').get().val(),
                            # 'grid': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_grid').get().val(),
                            'load': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_load').get().val(),
                            'solar': db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_solar').get().val()
                            }

                        self.bill_cum_monthly = {
                            'grid': db.child(gateway_id).child('energy').child(device_id).child('month').child('bill').get().val(),
                            # 'grid': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_grid').get().val(),
                            'load': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_load').get().val(),
                            'solar': db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_solar').get().val()
                            }

                        print('Energy cum monthly = {}'.format(self.energy_cum_monthly))
                        print('Bill cum monthly = {}'.format(self.bill_cum_monthly))

                except:
                    print('Data is None (Monthly)')

            else:
                print('Data is None (Total)')

        @PubSub.subscribe('pubsub', topic_device)  # Calculate consumption
        def match_topic_create(self, peer, sender, bus,  topic, headers, message):
            msg = json.loads(message)

            # choose type (power meter/inverter)
            if (device_id[0:2] == '05'): # power meter (grid)
                self.energy_acc = {'grid': float(msg['grid_accumulated_energy'])*0.001,
                                   'load': float(msg['grid_accumulated_energy'])*0.001,
                                   'solar': 0}
                                   # 'load': float(msg['grid_accumulated_energy'])*0.001,
                                   # 'solar': float(msg['grid_accumulated_energy'])*0.001}

            elif (device_id[0:2] == '22'): # inverter waiting....
                self.energy_acc = {'grid': float(msg['grid_accumulated_energy']),
                                   'load': float(msg['load_accumulated_energy']),
                                   'solar': float(msg['solar_accumulated_energy'])}

            else:
                print('please choose your device')
                pass

            #  this day / this month / this time
            self.dt_now = datetime.now()
            self.date_now = self.dt_now.date()
            self.time_now = self.dt_now.time()

            # check data
            if (self.energy_acc['grid'] == 'None') | (self.energy_acc['load'] == 'None') | (self.energy_acc['solar'] == 'None'):
                self.energy_now = {'grid': 0, 'load': 0, 'solar': 0}

            else:
                if (self.first_time == 1): # first time
                    self.energy_now = {'grid': 0, 'load': 0, 'solar': 0}
                    self.energy_old = self.energy_acc
                    self.first_time = 0

                else:
                    self.energy_new = self.energy_acc
                    self.energy_now = {key: self.energy_new[key] - self.energy_old[key] for key in self.energy_new.keys()}
                    self.energy_old = self.energy_new
                    print('Energy Now = {}'.format(self.energy_now))

            try:
                # check new day & month
                self.check_new_date_month()

                # percent grid/load/solar
                self.total_percent_energy_bill()

                # Update to firebase
                self.publish_firebase()

                # Update to Azure IoT hub
                # self.publish_azure_iot_hub()


            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)

        def check_new_date_month(self):
            if (self.date_now >= self.date_start) & (self.date_now <= self.date_end): # same month
                if (self.date_now == self.this_day): # same day
                    self.energy_cum_daily = {key: self.energy_cum_daily[key] + self.energy_now[key] for key in self.energy_now.keys()}
                    self.calculate_consumption(self.type_bill)
                    self.energy_cum_monthly = {key: self.energy_cum_monthly[key] + self.energy_now[key] for key in self.energy_now.keys()}
                    self.bill_cum_daily = {key: self.bill_cum_daily[key] + self.bill_now[key] for key in self.bill_now.keys()}
                    self.bill_cum_monthly = {key: self.bill_cum_monthly[key] + self.bill_now[key] for key in self.bill_now.keys()}

                elif (self.date_now > self.this_day): # new day
                    self.energy_cum_daily = self.energy_now
                    self.calculate_consumption(self.type_bill)
                    self.energy_cum_monthly = {key: self.energy_cum_monthly[key] + self.energy_now[key] for key in self.energy_now.keys()}
                    self.bill_cum_daily = self.bill_now
                    self.bill_cum_monthly = {key: self.bill_cum_monthly[key] + self.bill_now[key] for key in self.bill_now.keys()}

                    self.this_day = self.date_now

                else:
                    print('ERROR: daily consumption(calculation)')

            elif (self.date_now > self.date_end): # new month
                if (self.bill_cum_monthly['grid'] > self.max_bill_cum_monthly):  # max value(bill)
                    self.max_bill_cum_monthly = self.bill_cum_monthly['grid']

                try:
                    self.energy_cum_daily = self.energy_now
                    self.energy_cum_monthly = self.energy_now

                    self.calculate_consumption(self.type_bill)

                    self.bill_cum_daily = self.bill_now
                    self.bill_cum_monthly = self.bill_now

                    self.date_start = self.date_now
                    self.date_end = self.date_start + relativedelta(months=+1) - relativedelta(days=+1)

                except Exception as er:
                    print er

            else:
                print('ERROR: monthly consumption(calculation)')

            print('Energy cum daily = {}'.format(self.energy_cum_daily))
            print('Energy cum monthly = {}'.format(self.energy_cum_monthly))
            print('Bill cum daily = {}'.format(self.bill_cum_daily))
            print('Bill cum monthly = {}'.format(self.bill_cum_monthly))

        def total_percent_energy_bill(self):
            self.total_energy = {key: self.total_energy[key] + self.energy_now[key] for key in self.energy_now.keys()}
            self.total_bill = {key: self.total_bill[key] + self.bill_now[key] for key in self.bill_now.keys()}
            print('Total energy = {}'.format(self.total_energy))
            print('Total bill = {}'.format(self.total_bill))

            # if (self.energy_now['grid'] != 0):
            #     self.percent_energy = {key: self.energy_now[key] / self.energy_now['load'] * 100 for key in self.energy_now.keys()}
            #     self.percent_bill = {key: self.bill_now[key] / self.bill_now['load'] * 100 for key in self.bill_now.keys()}
            #     print('Percent energy = {}'.format(self.percent_energy))
            #     print('Percent bill = {}'.format(self.percent_bill))

        # type consumption
        def type_1_1(self):
            return collections.OrderedDict(sorted(self.price_1_1.items(), key=lambda t: t[0]))
        def type_1_2(self):
            return collections.OrderedDict(sorted(self.price_1_2.items(), key=lambda t: t[0]))
        def type_1_3(self):
            return self.price_1_3
        def type_6_1(self):
            return collections.OrderedDict(sorted(self.price_6_1.items(), key=lambda t: t[0]))

        # calculate consumption function
        def calculate_consumption(self, typeprice):
            if (typeprice['type'] == 'step'):  # step
                for i in range(0, len(typeprice)):
                    try:
                        if ((self.energy_cum_monthly['grid'] >= 0) | (self.energy_cum_monthly['grid'] > list(typeprice.keys())[i])) & (self.energy_cum_monthly['grid'] <= list(typeprice.keys())[i + 1]):
                            self.bill_now = {key: self.energy_now[key] * typeprice[list(typeprice.keys())[i]] for key in self.energy_now.keys()}
                            print('Bill Now = {}'.format(self.bill_now))
                            break

                    except:
                        if (list(typeprice.keys())[i]) == (list(typeprice.keys())[-1]):
                            self.bill_now = {key: self.energy_now[key] * typeprice[list(typeprice.keys())[i]] for key in self.energy_now.keys()}
                            print('Bill Now = {}'.format(self.bill_now))
                            break

            elif (typeprice['type'] == 'tou'):  # tou
                if ((self.date_now.weekday() == 5) | (self.date_now.weekday() == 6)):  # offpeak
                    self.bill_now = {key: self.energy_now[key] * typeprice['off'] for key in self.energy_now.keys()}
                    # print('Bill Now = {}'.format(self.bill_now))

                else:
                    if ((self.time_now) >= typeprice['tstart']) & (self.time_now <= typeprice['tstop']):
                        self.bill_now = {key: self.energy_now[key] * typeprice['on'] for key in self.energy_now.keys()}
                        # print('Bill Now = {}'.format(self.bill_now))

                    else:
                        self.bill_now = {key: self.energy_now[key] * typeprice['off'] for key in self.energy_now.keys()}
                        # print('Bill Now = {}'.format(self.bill_now))
            else:
                print("please choose price type")

        def publish_firebase(self):
            try:
                db.child(gateway_id).child('energy').child(device_id).child("dt").set(datetime.now().replace(microsecond=0).isoformat())
                db.child(gateway_id).child('energy').child(device_id).child('dateinfo').set(str(self.date_now))
                db.child(gateway_id).child('energy').child(device_id).child('monthinfo').set(str(self.date_end))

                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('current_grid').set(self.energy_now['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('current_load').set(self.energy_now['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('current_solar').set(self.energy_now['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_grid').set(self.energy_cum_daily['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_load').set(self.energy_cum_daily['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('daily_solar').set(self.energy_cum_daily['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('month').child('energy').set(round(self.energy_cum_monthly['grid'],2))
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_grid').set(self.energy_cum_monthly['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_load').set(self.energy_cum_monthly['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('monthly_solar').set(self.energy_cum_monthly['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_grid').set(self.total_energy['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_load').set(self.total_energy['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('total_solar').set(self.total_energy['solar'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('percent_grid').set(self.percent_energy['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('percent_load').set(self.percent_energy['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('percent_solar').set(self.percent_energy['solar'])
                # db.child(gateway_id).child('energy').child(device_id).child('consumption_kwh').child('max_grid').set(self.max_energy_cum_monthly)
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('history_m_grid').set(self.max_bill_cum_monthly)

                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('current_grid').set(self.bill_now['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('current_load').set(self.bill_now['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('current_solar').set(self.bill_now['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_grid').set(self.bill_cum_daily['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_load').set(self.bill_cum_daily['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('daily_solar').set(self.bill_cum_daily['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('month').child('bill').set(round(self.bill_cum_monthly['grid'],2))
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_grid').set(self.bill_cum_monthly['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_load').set(self.bill_cum_monthly['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('monthly_solar').set(self.bill_cum_monthly['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_grid').set(self.total_bill['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_load').set(self.total_bill['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('total_solar').set(self.total_bill['solar'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('percent_grid').set(self.percent_bill['grid'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('percent_load').set(self.percent_bill['load'])
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('percent_solar').set(self.percent_bill['solar'])
                db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('max_grid').set(self.max_bill_cum_monthly)
                # db.child(gateway_id).child('energy').child(device_id).child('bill_baht').child('history_m_grid').set(self.max_bill_cum_monthly)

            except Exception as er:
                print er

        # def publish_azure_iot_hub(self):
        #     # TODO publish to Azure IoT Hub u
        #     '''
        #     here we need to use code from /home/kwarodom/workspace/hive_os/volttron/
        #     hive_lib/azure-iot-sdk-python/device/samples/simulateddevices.py
        #     def iothub_client_telemetry_sample_run():
        #     '''
        #     print('Publish Azure IoT Hub')
        #
        #     x = {}
        #     x["device_id"] = agent_id
        #     x["date_time"] = datetime.now().replace(microsecond=0).isoformat()
        #     x["unixtime"] = int(time.time())
        #
        #     x["gridvoltage"] = self.Powermeter.variables['grid_voltage']
        #     x["gridcurrent"] = self.Powermeter.variables['grid_current']
        #     x["gridactivePower"] = self.Powermeter.variables['grid_activePower']
        #     x["gridreactivePower"] = self.Powermeter.variables['grid_reactivePower']
        #
        #     x["activity_type"] = 'application'
        #     x["username"] = 'arm'
        #     x["device_name"] = 'Consumption'
        #     x["device_type"] = 'energy'
        #     discovered_address = self.iotmodul.iothub_client_sample_run(bytearray(str(x), 'utf8'))


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
