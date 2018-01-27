'''
__author__ = "Warodom Khamphanchai"
__copyright__ = "Copyright 2014, BEMOSS"
__credits__ = []
__license__ = "...."  # Pending
__version__ = "1.0.1"
__maintainer__ = "Warodom Khamphanchai"
__email__ = "kwarodom@vt.edu"
__website__ = "kwarodom.wordpress.com"
__status__ = "Prototype"
__created__ = "2014-10-07 13:57:14.227294"
'''

import sys
import json
import importlib
import logging
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from bemoss_lib.communication.Email import EmailService
from bemoss_lib.communication.sms import SMSService
import psycopg2  # PostgresQL database adapter
import psycopg2.extras
import socket
import settings
import datetime
import time
import math
import pyrebase
import os
import random
import time
from ISStreamer.Streamer import Streamer


# utils.setup_logging()
# _log = logging.getLogger(__name__)

try:
    config = {
      "apiKey": "AIzaSyD4QZ7ko7uXpNK-VBF3Qthhm3Ypzi_bxgQ",
      "authDomain": "hive-rt-mobile-backend.firebaseapp.com",
      "databaseURL": "https://hive-rt-mobile-backend.firebaseio.com",
      "storageBucket": "bucket.appspot.com",
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except Exception as er:
    print er

# Step1: Agent Initialization
def powermeteragent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    def valid_ip(ip):
        parts = ip.split('.')
        return (
            len(parts) == 4
            and all(part.isdigit() for part in parts)
            and all(0 <= int(part) <= 255 for part in parts)
        )

    # 1. @params agent
    agent_id = get_config('agent_id')
    print(agent_id)
    device_monitor_time = get_config('device_monitor_time')
    max_monitor_time = int(settings.DEVICES['max_monitor_time'])
    debug_agent = False

    log_variables = dict(grid_current='double', grid_activePower='double', grid_reactivePower='double',
                         grid_apparentPower='double', grid_powerfactor='double', grid_quadrant='double',
                         grid_phaseshift='double', grid_phasediff='double',
                         solar_current='double', solar_activePower='double', solar_reactivePower='double',
                         solar_apparentPower='double', solar_powerfactor='double', solar_quadrant='double',
                         solar_phaseshift='double', solar_phasediff='double',
                         load_current='double', load_activePower='double', load_reactivePower='double',
                         load_apparentPower='double', load_powerfactor='double', load_quadrant='double',
                         load_phaseshift='double', load_phasediff='double')

    # 2. @params device_info
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    device_type = get_config('type')
    address = get_config('address')
    url_q = get_config('url_q')
    head_q = get_config('head_q')
    url_l = get_config('url_l')
    head_l = get_config('head_l')
    agent_id = get_config('agent_id')
    device_id = get_config('device_id')
    _address = address
    _address = _address.replace('http://', '')
    _address = _address.replace('https://', '')
    _address = str(_address).split('/')[0]
    try:  # validate whether or not address is an ip address
        socket.inet_aton(_address)
        if valid_ip(_address):
            ip_address = _address
        else:
            ip_address = None
        print "yes ip_address is {}".format(ip_address)
    except socket.error:
        print "yes ip_address is None"
        ip_address = None
    identifiable = get_config('identifiable')
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_table_power_meter = settings.DATABASES['default']['TABLE_powermeter']
    db_table_notification_event = settings.DATABASES['default']['TABLE_notification_event']
    db_id_column_name = "power_meter_id"
    db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
    db_table_device_type = settings.DATABASES['default']['TABLE_device_type']
    db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
    db_table_alerts_notificationchanneladdress = settings.DATABASES['default'][
        'TABLE_alerts_notificationchanneladdress']
    db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
    db_table_priority = settings.DATABASES['default']['TABLE_priority']

    gateway_id = settings.gateway_id
    print('++++++++++++++++++++++++++++++++')
    print('gateway_id : {}'.format(gateway_id))
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id

    # 4. @params device_api
    api = get_config('api')
    apiLib = importlib.import_module("DeviceAPI.classAPI." + api)


    # 4.1 initialize thermostat device object
    PowerMeter = apiLib.API(device_id = device_id, model=model, type=device_type, api=api, addressq=url_q, usernameq=head_q,
                            addressl=url_l, usernamel=head_l, agent_id=agent_id, db_host=db_host, db_port=db_port,
                            db_user=db_user, db_password=db_password, db_database=db_database)

    print("{0}agent is initialized for {1} using API={2} at {3}".format(agent_id, PowerMeter.get_variable('model'),
                                                                        PowerMeter.get_variable('api'),
                                                                        PowerMeter.get_variable('address')))

    # iotmodul = importlib.import_module("azure-iot-sdk-python.device.samples.iothub_client_sample2")

    # 5. @params notification_info
    send_notification = False
    email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
    email_recipients = settings.NOTIFICATION['email']['recipients']
    email_username = settings.NOTIFICATION['email']['username']
    email_password = settings.NOTIFICATION['email']['password']
    email_mailServer = settings.NOTIFICATION['email']['mailServer']
    notify_heartbeat = settings.NOTIFICATION['heartbeat']

    class Agent(PublishMixin, BaseAgent):

        # 1. agent initialization
        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            # 1. initialize all agent variables
            self.variables = kwargs
            self.valid_data = False
            self._keep_alive = True
            self.first_time_update_deviceMonitorBehavior = True
            self.event_ids = list()
            self.time_sent_notifications = {}
            self.notify_heartbeat = notify_heartbeat
            self.ip_address = ip_address if ip_address != None else None
            self.flag = 1
            self.tmpDate = datetime.datetime.now()
            self.changed_variables = None
            self.lastUpdateTime = None
            self.stream_data_initialState = False
            self.start_first_time = True

            # 2. setup connection with db -> Connect to bemossdb database
            # try:
            #     self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
            #                                 password=db_password)
            #     self.cur = self.con.cursor()  # open a cursor to perfomm database operations
            #     print("{} connects to the database name {} successfully".format(agent_id, db_database))
            # except Exception as er:
            #     print er
            #     print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))

        def set_variable(self, k, v):  # k=key, v=value
            self.variables[k] = v

        def get_variable(self, k):
            return self.variables.get(k, None)  # default of get_variable is none

        # 2. agent setup method
        def setup(self):
            super(Agent, self).setup()
            # 1. Do a one time push when we start up so we don't have to wait for the periodic
            self.timer(1, self.deviceMonitorBehavior)
            if identifiable == "True": PowerMeter.identifyDevice()

        @periodic(device_monitor_time)
        def deviceMonitorBehavior(self):
            # step1: get current status, then map keywords and variables to agent knowledge

            try:
                print ("starting device monitor")
                PowerMeter.getDeviceStatus()
                if (self.start_first_time):
                    self.grid_energy = 0
                    self.start_first_time = False
                    self.last_energy = PowerMeter.variables['grid_accumulated_energy']
                    print("grid accu = {}".format(self.last_energy))
                else:
                    self.energy_now = PowerMeter.variables['grid_accumulated_energy']
                    print("grid accu = {}".format(self.energy_now))
                    self.grid_energy = (float(self.energy_now) - float(self.last_energy))/1000
                    print "Energy Now = {}".format(self.grid_energy)
                    self.last_energy = self.energy_now
                    print("Grid Power = {}".format(PowerMeter.variables['grid_activePower']))
            except Exception as er:
                self.grid_energy = 0
                print "cannot read data: {}".format(er)
                print "device connection for {} is not successful {}".format(agent_id, er)
            self.updateUI()

            # self.changed_variables = dict()
            # for v in log_variables:
            #     if v in PowerMeter.variables:
            #         if not v in self.variables or self.variables[v] != PowerMeter.variables[v]:
            #             self.variables[v] = PowerMeter.variables[v]
            #             self.changed_variables[v] = log_variables[v]
            #     else:
            #         if v not in self.variables:  # it won't be in self.variables either (in the first time)
            #             self.changed_variables[v] = log_variables[v]
            #             self.variables[v] = None

            if self.get_variable('realpower') is not None and self.get_variable('realpower') < 0:
                self.set_variable('realpower', -1 * float(self.get_variable('realpower')))
            if self.get_variable('reactivepower') is not None and self.get_variable('reactivepower') < 0:
                self.set_variable('reactivepower', -1 * float(self.get_variable('reactivepower')))
            if self.get_variable('apparentpower') is not None and self.get_variable('apparentpower') < 0:
                self.set_variable('apparentpower', -1 * float(self.get_variable('apparentpower')))
            self.postgresAPI()

            #firebase
            try:
                data = PowerMeter.variables['grid_activePower']
                db.child(gateway_id).child(agent_id).child("grid_activePower").set(data)
                if (agent_id == "5PMCP270121595"):
                    db.child(gateway_id).child('1PV221445K1200100').child("inverter_activePower").set(data)
                else:
                    print("not solar no need to update to firebase")

            except Exception as er:
                print er

            try:
                streamer = Streamer(bucket_name="srisaengtham", bucket_key="WSARH9FBXEBX",
                                    access_key="4YM0GM6ZNUAZtHT8LYWxQSAdrqaxTipw")
                streamer.log(str(PowerMeter.variables['agent_id'] + '_grid_voltage'),
                             float(PowerMeter.variables['grid_voltage']))
                streamer.log(str(PowerMeter.variables['agent_id'] + '_grid_current'),
                             float(PowerMeter.variables['grid_current']))
                streamer.log(str(PowerMeter.variables['agent_id'] + '_grid_activePower'),
                             float(PowerMeter.variables['grid_activePower']))
                streamer.log(str(PowerMeter.variables['agent_id'] + '_grid_reactivePower'),
                             float(PowerMeter.variables['grid_reactivePower']))
            except Exception as er:
                print "update data base error: {}".format(er)

            # x = {}
            # x["agent_id"] = PowerMeter.variables['agent_id']
            # x["dt"] = datetime.datetime.now().replace(microsecond=0).isoformat()
            # x["gridvoltage"] = PowerMeter.variables['grid_voltage']
            # x["gridcurrent"] = PowerMeter.variables['grid_current']
            # x["gridactivePower"] = PowerMeter.variables['grid_activePower']
            # x["gridreactivePower"] = PowerMeter.variables['grid_reactivePower']
            # x["device_type"] = 'powermeter'
            #
            # discovered_address = iotmodul.iothub_client_sample_run(x)
            #
            # print x

        def postgresAPI(self):

            self.connect_postgresdb()
            try:
                self.cur.execute("SELECT * from power_meter WHERE power_meter_id=%s", (agent_id,))
                if bool(self.cur.rowcount):
                    pass
                else:
                    self.cur.execute(
                        """INSERT INTO power_meter (power_meter_id, last_scanned_time) VALUES (%s, %s);""",
                        (agent_id, datetime.datetime.now()))
                    self.con.commit()
            except:
                print "Data base error"
            #
            try:
                self.cur.execute("""
                    UPDATE power_meter
                    SET load_activepower=%s, last_scanned_time=%s
                    WHERE power_meter_id=%s""", (
                    PowerMeter.variables['grid_activePower'], datetime.datetime.now(), agent_id))
                self.con.commit()
                print "update database: success"
            except Exception as er:
                print "update data base error: {}".format(er)
            #
            # try:
            #     self.cur.execute(
            #         """INSERT INTO ts_power_meter (datetime,grid_current, grid_activepower, grid_reactivepower,
            #         grid_apparentpower, grid_powerfactor, grid_quadrant,grid_phaseshift,network_status,power_meter_id,load_current, load_activepower, load_reactivepower,
            #         load_apparentpower, load_powerfactor, load_quadrant,load_phaseshift,
            #         solar_current, solar_activepower, solar_reactivepower,
            #         solar_apparentpower, solar_powerfactor, solar_quadrant,solar_phaseshift
            #         ) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s,%s, %s, %s, %s, %s,%s, %s,%s, %s, %s, %s, %s);""",
            #         (
            #         datetime.datetime.now(), PowerMeter.variables['grid_current'], PowerMeter.variables['grid_activePower'],
            #         PowerMeter.variables['grid_reactivePower'],
            #         PowerMeter.variables['grid_apparentPower'], PowerMeter.variables['grid_powerfactor'],
            #         PowerMeter.variables['grid_quadrant'], PowerMeter.variables['grid_phaseshift'],
            #         PowerMeter.variables['network_status'],agent_id,
            #         PowerMeter.variables['load_current'], PowerMeter.variables['load_activePower'],
            #         PowerMeter.variables['load_reactivePower'],
            #         PowerMeter.variables['load_apparentPower'], PowerMeter.variables['load_powerfactor'],
            #         PowerMeter.variables['load_quadrant'], PowerMeter.variables['load_phaseshift'],
            #         PowerMeter.variables['solar_current'], PowerMeter.variables['solar_activePower'],
            #         PowerMeter.variables['solar_reactivePower'],
            #         PowerMeter.variables['solar_apparentPower'], PowerMeter.variables['solar_powerfactor'],
            #         PowerMeter.variables['solar_quadrant'], PowerMeter.variables['solar_phaseshift']
            #         ))
            #     self.con.commit()
            #     print "insert database: success"
            # except Exception as er:
            #     print "insert data base error: {}".format(er)

            try:
                self.cur.execute(
                    """INSERT INTO ts_power_meter (datetime, grid_voltage, grid_current, grid_activepower, 
                    grid_accumulated_energy, grid_energy, power_meter_id, gateway_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                    (
                    datetime.datetime.now(), PowerMeter.variables['grid_voltage'], PowerMeter.variables['grid_current'],
                    PowerMeter.variables['grid_activePower'], PowerMeter.variables['grid_accumulated_energy'], self.grid_energy, agent_id, '1'
                    ))
                self.con.commit()
                print "insert database: success"
            except Exception as er:
                print "insert data base error: {}".format(er)


            self.disconnect_postgresdb()

        def device_offline_detection(self):
            self.cur.execute("SELECT nickname FROM " + db_table_power_meter + " WHERE power_meter_id=%s",
                             (agent_id,))
            print agent_id
            if self.cur.rowcount != 0:
                device_nickname = self.cur.fetchone()[0]
                print device_nickname
            else:
                device_nickname = ''
            _db_notification_subject = 'BEMOSS Device {} {} went OFFLINE!!!'.format(device_nickname, agent_id)
            _email_subject = '#Attention: BEMOSS Device {} {} went OFFLINE!!!'.format(device_nickname, agent_id)
            _email_text = '#Attention: BEMOSS Device {}  {} went OFFLINE!!!'.format(device_nickname, agent_id)
            self.cur.execute("SELECT network_status FROM " + db_table_power_meter + " WHERE power_meter_id=%s",
                             (agent_id,))
            self.network_status = self.cur.fetchone()[0]
            print self.network_status
            if self.network_status == "OFFLINE":
                print "Found Device OFFLINE"
                self.cur.execute("SELECT id FROM " + db_table_active_alert + " WHERE event_trigger_id=%s", ('5',))
                self._active_alert_id = self.cur.fetchone()[0]
                self.cur.execute(
                    "SELECT id FROM " + db_table_temp_time_counter + " WHERE alert_id=%s AND device_id=%s",
                    (str(self._active_alert_id), agent_id,))
                # If this is the first detected violation
                if self.cur.rowcount == 0:
                    print "first device offline detected"
                    # create counter in DB
                    self.cur.execute(
                        "INSERT INTO " + db_table_temp_time_counter + " VALUES(DEFAULT,%s,%s,%s,%s,%s)",
                        (self._active_alert_id, agent_id, '0', '0', '0'))
                    self.con.commit()
                    self.send_device_notification_db(_db_notification_subject, self._active_alert_id)
                    # Send email if exist
                    self.cur.execute(
                        "SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",
                        (self._active_alert_id, '1'))
                    if self.cur.rowcount != 0:
                        self._alert_email = self.cur.fetchall()
                        for single_email_1 in self._alert_email:
                            print single_email_1[0]
                            self.send_device_notification_email(single_email_1[0], _email_subject, _email_text)

                    # Send SMS if provided by user
                    self.cur.execute(
                        "SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",
                        (self._active_alert_id, '2'))
                    if self.cur.rowcount != 0:
                        self._alert_sms_phone_no = self.cur.fetchall()
                        for single_number in self._alert_sms_phone_no:
                            print single_number[0]
                            self.send_device_notification_sms(single_number[0], _email_subject)
                else:
                    self.priority_counter(self._active_alert_id, _db_notification_subject)
            else:
                print "The Device is ONLINE"

        def send_device_notification_db(self, _tampering_device_msg, _active_alert_id):
            print " INSIDE send_device_notification_db"

            # Find the priority id
            self.cur.execute(
                "SELECT priority_id FROM " + db_table_active_alert + " WHERE id=%s",
                (str(_active_alert_id),))
            self.priority_id = self.cur.fetchone()[0]

            # Find the priority level
            self.cur.execute(
                "SELECT priority_level FROM " + db_table_priority + " WHERE id=%s",
                str(self.priority_id))
            self.priority_level = self.cur.fetchone()[0]

            # Insert into DB the notification
            self.cur.execute("INSERT INTO " + db_table_bemoss_notify + " VALUES(DEFAULT,%s,%s,%s,%s)",
                             (_tampering_device_msg,
                              str(datetime.datetime.now()), 'Alert', str(self.priority_level)))
            self.con.commit()

            # Find the number of notifications sent for the same alert and device
            self.cur.execute(
                "SELECT no_notifications_sent FROM " + db_table_temp_time_counter + " WHERE alert_id=%s AND device_id=%s",
                (str(_active_alert_id), agent_id,))
            self._no_notifications_sent = self.cur.fetchone()[0]
            self.con.commit()
            print self._no_notifications_sent
            self._no_notifications_sent = int(self._no_notifications_sent) + 1
            print self._no_notifications_sent
            self.cur.execute(
                "UPDATE " + db_table_temp_time_counter + " SET no_notifications_sent=%s WHERE alert_id=%s AND device_id=%s",
                (str(self._no_notifications_sent), str(_active_alert_id), agent_id,))
            self.con.commit()

        def send_device_notification_email(self, _active_alert_email, _email_subject, _email_text):
            # _email_subject = '#Attention: BEMOSS Device {} has detected a high level of CO2!!!'.format(agent_id)
            # _email_text = 'Here is the detail of device status\n' + str(_tampering_device_msg) \
            # _email_text = 'The CO2 level has exceeded the defined range'
            emailService = EmailService()

            # Send Email
            emailService.sendEmail(email_fromaddr, _active_alert_email, email_username,
                                   email_password, _email_subject, _email_text, email_mailServer)

        def send_device_notification_sms(self, _active_alert_phone_number_misoperation, _sms_subject):
            print "INSIDE send_device_notification_sms"
            print _active_alert_phone_number_misoperation
            smsService = SMSService()
            smsService.sendSMS(email_fromaddr, _active_alert_phone_number_misoperation, email_username, email_password,
                               _sms_subject, email_mailServer)

        def priority_counter(self, _active_alert_id, _tampering_device_msg_1):
            # Find the priority counter limit then compare it with priority_counter in priority table
            # if greater than the counter limit then send notification and reset the value
            # else just increase the counter
            print "INSIDE the priority_counter"
            _email_subject = '#Attention: BEMOSS Device {} went OFFLINE!!!'.format(agent_id)
            _email_text = '#Attention: BEMOSS Device {} went OFFLINE!!!'.format(agent_id)
            self.cur.execute(
                "SELECT priority_counter FROM " + db_table_temp_time_counter + " WHERE alert_id=%s AND device_id=%s",
                (str(_active_alert_id), agent_id,))
            self.priority_count = self.cur.fetchone()[0]
            self.con.commit()

            # Find the priority id from active alert table
            self.cur.execute(
                "SELECT priority_id FROM " + db_table_active_alert + " WHERE id=%s",
                (str(_active_alert_id),))
            self.priority_id = self.cur.fetchone()[0]
            self.con.commit()

            # Find the priority limit from the priority table
            self.cur.execute(
                "SELECT priority_counter FROM " + db_table_priority + " WHERE id=%s",
                (str(self.priority_id),))
            self.priority_limit = self.cur.fetchone()[0]
            self.con.commit()

            # If the counter reaches the limit
            if int(self.priority_count) > int(self.priority_limit):
                # self._no_notifications_sent = int(self._no_notifications_sent) + 1
                self.send_device_notification_db(_tampering_device_msg_1, _active_alert_id)
                self.cur.execute(
                    "UPDATE " + db_table_temp_time_counter + " SET priority_counter=%s WHERE alert_id=%s AND device_id=%s",
                    ('0', str(_active_alert_id), agent_id,))
                self.con.commit()

                print "INSIDE the priority counter exceeded the defined range"
                # Send email if exist
                self.cur.execute(
                    "SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",
                    (self._active_alert_id, '1'))
                if self.cur.rowcount != 0:
                    self._alert_email = self.cur.fetchall()
                    for single_email_1 in self._alert_email:
                        print single_email_1[0]
                        self.send_device_notification_email(single_email_1[0], _email_subject, _email_text)

                # Send SMS if provided by user
                self.cur.execute(
                    "SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",
                    (self._active_alert_id, '2'))
                if self.cur.rowcount != 0:
                    self._alert_sms_phone_no = self.cur.fetchall()
                    for single_number in self._alert_sms_phone_no:
                        print single_number[0]
                        self.send_device_notification_sms(single_number[0], _email_subject)
            else:
                self.priority_count = int(self.priority_count) + 1
                self.cur.execute(
                    "UPDATE " + db_table_temp_time_counter + " SET priority_counter=%s WHERE alert_id=%s AND device_id=%s",
                    (str(self.priority_count), str(_active_alert_id), agent_id,))

        def updateUI(self):
            topic = '/agent/ui/' + device_type + '/device_status_response/' + _topic_Agent_UI_tail
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
                headers_mod.FROM: agent_id,
                headers_mod.TO: 'ui'
            }
            _data = PowerMeter.variables

            try:
                _data['grid_energy'] = self.grid_energy
            except Exception as er:
                print "add data error: {}".format(er)

            message = json.dumps(_data)
            # message = message.encode(encoding='utf_8')
            print("{} published topic: {} and message {}".format(agent_id, topic, message))
            self.publish(topic, headers, message)

        # 4. updateUIBehavior (generic behavior)
        @matching.match_exact('/ui/agent/' + device_type + '/device_status/' + _topic_Agent_UI_tail)
        def updateUIBehavior(self, topic, headers, message, match):
            print agent_id + " got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            self.updateUI()

        # 5. deviceControlBehavior (generic behavior)
        @matching.match_exact('/ui/agent/' + device_type + '/update/' + _topic_Agent_UI_tail)
        def deviceControlBehavior(self, topic, headers, message, match):
            print agent_id + " got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            # step1: change device status according to the receive message
            if self.isPostmsgValid(message[0]):  # check if the data is valid
                setDeviceStatusResult = PowerMeter.setDeviceStatus(json.loads(message[0]))
                # TODO need to do additional checking whether the device setting is actually success!!!!!!!!
                # step2: update agent's knowledge on this device
                topic = '/agent/ui/' + device_type + '/update_response/' + _topic_Agent_UI_tail
                # now = datetime.utcnow().isoformat(' ') + 'Z'
                headers = {
                    'AgentID': agent_id,
                    headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                    # headers_mod.DATE: now,
                }
                if setDeviceStatusResult:
                    message = 'success'
                else:
                    message = 'failure'
            else:
                print("The POST message is invalid, check setting and try again\n")
                message = 'failure'
            self.publish(topic, headers, message)
            self.deviceMonitorBehavior()

        def isPostmsgValid(self, postmsg):  # check validity of postmsg
            dataValidity = True
            return dataValidity

        # 6. deviceIdentifyBehavior (generic behavior)
        @matching.match_exact('/ui/agent/' + device_type + '/identify/' + _topic_Agent_UI_tail)
        def deviceIdentifyBehavior(self, topic, headers, message, match):
            print agent_id + " got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            # step1: change device status according to the receive message
            identifyDeviceResult = PowerMeter.identifyDevice()
            # TODO need to do additional checking whether the device setting is actually success!!!!!!!!
            # step2: send reply message back to the UI
            topic = '/agent/ui/identify_response/' + device_type + '/' + _topic_Agent_UI_tail
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.PLAIN_TEXT,
                # headers_mod.DATE: now,
            }
            if identifyDeviceResult:
                message = 'success'
            else:
                message = 'failure'
            self.publish(topic, headers, message)

        # 9. update Postgres database
        def updateDB(self, table, column, column_ref, column_data, column_ref_data):
            self.cur.execute("UPDATE " + table + " SET " + column + "=%s "
                                                                    "WHERE " + column_ref + "=%s",
                             (column_data, column_ref_data))
            self.con.commit()

        @matching.match_exact('/ui/agent/' + device_type + '/add_notification_event/' + _topic_Agent_UI_tail)
        def add_notification_event(self, topic, headers, message, match):
            print agent_id + " got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}".format(message=message)
            # reply message
            topic = '/agent/ui/' + device_type + '/add_notification_event_response/' + _topic_Agent_UI_tail
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
                headers_mod.FROM: agent_id,
                headers_mod.TO: 'ui'
            }
            # add event_id to self.event_ids
            _data = json.loads(message[0])
            event_id = _data['event_id']
            print "{} added notification event_id: {}".format(agent_id, event_id)
            self.event_ids.append(event_id)
            _data = "success"
            message = _data
            # message = json.dumps(_data)
            # message = message.encode(encoding='utf_8')
            self.publish(topic, headers, message)

        @matching.match_exact('/ui/agent/' + device_type + '/remove_notification_event/' + _topic_Agent_UI_tail)
        def remove_notification_event(self, topic, headers, message, match):
            print agent_id + " got\nTopic: {topic}".format(topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}".format(message=message)
            # reply message
            topic = '/agent/ui/' + device_type + '/remove_notification_event_response/' + _topic_Agent_UI_tail
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
                headers_mod.FROM: agent_id,
                headers_mod.TO: 'ui'
            }
            # add event_id to self.event_ids
            _data = json.loads(message[0])
            event_id = _data['event_id']
            print "{} removed notification event_id: {}".format(agent_id, event_id)
            self.event_ids.remove(event_id)
            _data = "success"
            message = _data
            # message = json.dumps(_data)
            # message = message.encode(encoding='utf_8')
            self.publish(topic, headers, message)

        def track_event_send_notification(self):
            for event_id in self.event_ids:
                print "{} is monitoring event_id: {}\n".format(agent_id, event_id)
                # collect information about event from notification_event table
                self.cur.execute("SELECT event_name, notify_device_id, triggered_parameter, comparator,"
                                 "threshold, notify_channel, notify_address, notify_heartbeat  FROM "
                                 + db_table_notification_event + " WHERE event_id=%s", (event_id,))
                if self.cur.rowcount != 0:
                    row = self.cur.fetchone()
                    event_name = str(row[0])
                    notify_device_id = str(row[1])
                    triggered_parameter = str(row[2])
                    comparator = str(row[3])
                    threshold = row[4]
                    notify_channel = str(row[5])
                    notify_address = row[6]
                    notify_heartbeat = row[7] if row[7] is not None else self.notify_heartbeat
                    _event_has_triggered = False
                    print "{} triggered_parameter:{} self.get_variable(triggered_parameter):{} comparator:{} threshold:{}" \
                        .format(agent_id, triggered_parameter, self.get_variable(triggered_parameter), comparator,
                                threshold)
                    # check whether message is already sent
                    try:
                        if (datetime.datetime.now() - self.time_sent_notifications[
                            event_id]).seconds > notify_heartbeat:
                            if notify_device_id == agent_id:
                                if comparator == "<":
                                    threshold = float(threshold)
                                    if self.get_variable(triggered_parameter) < threshold: _event_has_triggered = True
                                elif comparator == ">":
                                    threshold = float(threshold)
                                    if self.get_variable(triggered_parameter) > threshold: _event_has_triggered = True
                                    print "{} triggered_parameter:{} self.get_variable(triggered_parameter):{} comparator:{} threshold:{}" \
                                        .format(agent_id, triggered_parameter, self.get_variable(triggered_parameter),
                                                comparator, threshold)
                                    print "{} _event_has_triggerered {}".format(agent_id, _event_has_triggered)
                                elif comparator == "<=":
                                    threshold = float(threshold)
                                    if self.get_variable(triggered_parameter) <= threshold: _event_has_triggered = True
                                elif comparator == ">=":
                                    threshold = float(threshold)
                                    if self.get_variable(triggered_parameter) >= threshold: _event_has_triggered = True
                                elif comparator == "is":
                                    if threshold == "True":
                                        threshold = True
                                    elif threshold == "False":
                                        threshold = False
                                    else:
                                        threshold = str(threshold)
                                    if self.get_variable(triggered_parameter) is threshold: _event_has_triggered = True
                                elif comparator == "isnot":
                                    if threshold == "True":
                                        threshold = True
                                    elif threshold == "False":
                                        threshold = False
                                    else:
                                        threshold = str(threshold)
                                    if self.get_variable(
                                            triggered_parameter) is not threshold: _event_has_triggered = True
                                else:
                                    pass
                                if _event_has_triggered:  # notify the user if triggered
                                    # step2 notify user to notify_channel at notify_address with period notify_heartbeat
                                    if notify_channel == 'email':
                                        _email_text = '{} notification event triggered_parameter: {}, comparator: {}, ' \
                                                      'threshold: {}\n now the current status of triggered_parameter: {} is {}' \
                                            .format(agent_id, triggered_parameter, comparator, threshold,
                                                    triggered_parameter, self.get_variable(triggered_parameter))
                                        emailService = EmailService()
                                        emailService.sendEmail(email_fromaddr, notify_address, email_username,
                                                               email_password,
                                                               self.subject, _email_text, email_mailServer)
                                        # self.send_notification_status = True
                                        # TODO store time_send_notification for each event
                                        self.time_sent_notifications[event_id] = datetime.datetime.now()
                                        print "time_sent_notifications is {}".format(
                                            self.time_sent_notifications[event_id])
                                        print('{} >> sent notification message for {}'.format(agent_id, event_name))
                                        print(
                                            '{} notification event triggered_parameter: {}, comparator: {}, threshold: {}'
                                                .format(agent_id, triggered_parameter, comparator, threshold))
                                    else:
                                        print "{} >> notification channel: {} is not supported yet".format(agent_id,
                                                                                                           notify_channel)
                                else:
                                    print "{} >> Event is not triggered".format(agent_id)
                            else:
                                "{} >> this event_id {} is not for this device".format(agent_id, event_id)
                        else:
                            "{} >> Email is already sent, waiting for another heartbeat period".format(agent_id)
                    except:
                        # step1 compare triggered_parameter with comparator to threshold
                        # step1.1 classify comparator <,>,<=,>=,is,isnot
                        # case1 comparator <
                        print "{} >> first time trigger notification".format(agent_id)
                        if notify_device_id == agent_id:
                            if comparator == "<":
                                threshold = float(threshold)
                                if self.get_variable(triggered_parameter) < threshold: _event_has_triggered = True
                            elif comparator == ">":
                                threshold = float(threshold)
                                if self.get_variable(triggered_parameter) > threshold: _event_has_triggered = True
                                print "{} triggered_parameter:{} self.get_variable(triggered_parameter):{} comparator:{} threshold:{}" \
                                    .format(agent_id, triggered_parameter, self.get_variable(triggered_parameter),
                                            comparator, threshold)
                                print "{} _event_has_triggerered {}".format(agent_id, _event_has_triggered)
                            elif comparator == "<=":
                                threshold = float(threshold)
                                if self.get_variable(triggered_parameter) <= threshold: _event_has_triggered = True
                            elif comparator == ">=":
                                threshold = float(threshold)
                                if self.get_variable(triggered_parameter) >= threshold: _event_has_triggered = True
                            elif comparator == "is":
                                if threshold == "True":
                                    threshold = True
                                elif threshold == "False":
                                    threshold = False
                                else:
                                    threshold = str(threshold)
                                if self.get_variable(triggered_parameter) is threshold: _event_has_triggered = True
                            elif comparator == "isnot":
                                if threshold == "True":
                                    threshold = True
                                elif threshold == "False":
                                    threshold = False
                                else:
                                    threshold = str(threshold)
                                if self.get_variable(triggered_parameter) is not threshold: _event_has_triggered = True
                            else:
                                pass
                            print "{} >> _event_has_triggered {}".format(agent_id, _event_has_triggered)
                            if _event_has_triggered:  # notify the user if triggered
                                # step2 notify user to notify_channel at notify_address with period notify_heartbeat
                                if notify_channel == 'email':
                                    _email_text = '{} notification event triggered_parameter: {}, comparator: {}, ' \
                                                  'threshold: {}\n now the current status of triggered_parameter: {} is {}' \
                                        .format(agent_id, triggered_parameter, comparator, threshold,
                                                triggered_parameter, self.get_variable(triggered_parameter))
                                    emailService = EmailService()
                                    emailService.sendEmail(email_fromaddr, notify_address, email_username,
                                                           email_password,
                                                           self.subject, _email_text, email_mailServer)
                                    # self.send_notification_status = True
                                    # store time_send_notification for each event
                                    self.time_sent_notifications[event_id] = datetime.datetime.now()
                                    print "{} >> time_sent_notifications is {}".format(agent_id,
                                                                                       self.time_sent_notifications[
                                                                                           event_id])
                                    print('{} >> sent notification message for {}'.format(agent_id, event_name))
                                    print('{} notification event triggered_parameter: {}, comparator: {}, threshold: {}'
                                          .format(agent_id, triggered_parameter, comparator, threshold))
                                else:
                                    print "{} >> notification channel: {} is not supported yet".format(agent_id,
                                                                                                       notify_channel)
                            else:
                                print "{} >> Event is not triggered".format(agent_id)
                        else:
                            "{} >> this event_id {} is not for this device".format(agent_id, event_id)
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

    Agent.__name__ = 'PowerMeterAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(powermeteragent,
                       description='Power Meter agent',
                       argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass