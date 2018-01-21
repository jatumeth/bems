# -*- coding: utf-8 -*-
'''
Copyright (c) 2017, HiVE Team (PEA - Provincial Electricity Authority)
All rights reserved.

#__author__ = "HiVE Team"
#__credits__ = ""
#__version__ = "1.0"
#__maintainer__ = "HiVE Team"
#__email__ = "teerapong.pon@gmail.com"
#__website__ = "www.pea.co.th"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2017-08-15 19:09:33"
'''

import sys
import json
import importlib
import datetime
import psycopg2
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
from volttron.platform.messaging import headers as headers_mod
from bemoss_lib.communication.Email import EmailService
from bemoss_lib.communication.sms import SMSService
import psycopg2.extras
import settings
import socket

def TplinkAgent(config_path, **kwargs):

    config = utils.load_config(config_path)

    def get_config(name):
        try:
            return kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    #1. @params agent
    agent_id = get_config('agent_id')
    device_monitor_time = get_config('device_monitor_time')
    max_monitor_time = int(settings.DEVICES['max_monitor_time'])
    cassandra_update_time = int(settings.DEVICES['cassandra_update_time'])

    debug_agent = False
    #Dictionary of Variables supposed to be saved in postgress database
    agentAPImapping = dict(status=[], power=[], energy=[])

    #Dictionary of Variables supposed to be saved into timeseries database
    log_variables = dict(status='text',power='double',energy='double',offline_count='int')

    tolerance = 0.5 #if the numerical variables change less than this percent, its not conisdered change and not logged
    building_name = get_config('building_name')
    zone_id = get_config('zone_id')
    model = get_config('model')
    device_type = get_config('type')
    macaddress = get_config('macaddress')
    address_get = get_config('address_get')
    address_put = get_config('address_put')
    vendor = get_config('vendor')
    auth_header = get_config('auth_header')
    smt_username = get_config('smt_username')
    smt_password = get_config('smt_password')
    address = get_config('address')
    cloudUserName = get_config('cloudUserName')
    cloudPassword = get_config('cloudPassword')
    deviceid = get_config('deviceid')

    _address = address
    _address = _address.replace('http://', '')
    _address = _address.replace('https://', '')
    try:  # validate whether or not address is an ip address
        socket.inet_aton(_address)
        ip_address = _address
        # print "yes ip_address is {}".format(ip_address)
    except socket.error:
        # print "yes ip_address is None"
        ip_address = None
    identifiable = get_config('identifiable')
    # mac_address = get_config('mac_address')
    #TODO get database parameters from settings.py, add db_table for specific table
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_table_Tplink = settings.DATABASES['default']['TABLE_Tplink']
    db_table_notification_event = settings.DATABASES['default']['TABLE_notification_event']
    db_table_active_alert = settings.DATABASES['default']['TABLE_active_alert']
    db_table_device_type = settings.DATABASES['default']['TABLE_device_type']
    db_table_bemoss_notify = settings.DATABASES['default']['TABLE_bemoss_notify']
    db_table_alerts_notificationchanneladdress = settings.DATABASES['default']['TABLE_alerts_notificationchanneladdress']
    db_table_temp_time_counter = settings.DATABASES['default']['TABLE_temp_time_counter']
    db_table_priority = settings.DATABASES['default']['TABLE_priority']
    #construct _topic_Agent_UI based on data obtained from DB
    _topic_Agent_UI_tail = building_name + '/' + str(zone_id) + '/' + agent_id
    api = get_config('api')
    apiLib = importlib.import_module("DeviceAPI.classAPI."+api)

    #4.1 initialize tplink device object
    if vendor == 'Digi':
        gateway_id = get_config('gateway_id')
        Tplink = apiLib.API(gateway_id=gateway_id, model=model, device_type=device_type, api=api, address=address,
                              macaddress = macaddress, agent_id=agent_id,  db_host=db_host, db_port=db_port,
                              db_user=db_user, db_password=db_password, db_database=db_database,cloudUserName=cloudUserName,cloudPassword=cloudPassword,deviceid=deviceid)
    else:
        Tplink = apiLib.API(model=model, device_type=device_type, api=api, address=address, macaddress = macaddress,
                              agent_id=agent_id, db_host=db_host, db_port=db_port, db_user=db_user,
                              db_password=db_password, db_database=db_database, config_path=config_path,cloudUserName=cloudUserName,cloudPassword=cloudPassword,deviceid=deviceid)

    print("{0}agent is initialized for {1} using API={2} at {3}".format(agent_id,
                                                                        Tplink.get_variable('model'),
                                                                        Tplink.get_variable('api'),
                                                               Tplink.get_variable('address')))

    iotmodul = importlib.import_module("azure-iot-sdk-python.device.samples.iothub_client_sample2")


    connection_renew_interval = Tplink.variables['connection_renew_interval']

    #params notification_info
    send_notification = False
    email_fromaddr = settings.NOTIFICATION['email']['fromaddr']
    email_recipients = settings.NOTIFICATION['email']['recipients']
    email_username = settings.NOTIFICATION['email']['username']
    email_password = settings.NOTIFICATION['email']['password']
    email_mailServer = settings.NOTIFICATION['email']['mailServer']
    notify_heartbeat = settings.NOTIFICATION['heartbeat']

    class Agent(PublishMixin, BaseAgent):
        """Agent for querying WeatherUndergrounds API"""

        # 1. agent initialization
        def __init__(self, **kwargs):
            #1. initialize all agent variables
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            self.valid_data = False
            self._keep_alive = True
            self.flag = 1
            self.event_ids = list()
            self.time_sent_notifications = {}
            self.notify_heartbeat = notify_heartbeat
            self.ip_address = ip_address if ip_address != None else None
            self.changed_variables = None
            self.lastUpdateTime = None
            self.subscriptionTime = datetime.datetime.now()
            self.already_offline = False
            #2. setup connection with db -> Connect to bemossdb database
            # try:
            #     self.con = psycopg2.connect(host=db_host, port=db_port, database=db_database, user=db_user,
            #                                 password=db_password)
            #     self.cur = self.con.cursor()  # open a cursor to perfomm database operations
            #     print("{} connects to the database name {} successfully".format(agent_id, db_database))
            # except:
            #     print("ERROR: {} fails to connect to the database name {}".format(agent_id, db_database))
            #3. send notification to notify building admin
            self.send_notification = send_notification
            self.subject = 'Message from ' + agent_id

        # These set and get methods allow scalability
        def set_variable(self,k,v): #k=key, v=value
            self.variables[k] = v

        def get_variable(self,k):
            return self.variables.get(k, None) #default of get_variable is none

        # 2. agent setup method
        def setup(self):
            super(Agent, self).setup()

            self.timer(1, self.deviceMonitorBehavior)

        #Re-login / re-subcribe to devices periodically. The API might choose to have empty function if not necessary
        # @periodic(connection_renew_interval)
        # def renewConnection(self):
        #     Tplink.renewConnection()

        @periodic(device_monitor_time)
        def deviceMonitorBehavior(self):
            try:
                Tplink.getDeviceStatus()
                self.variables['status'] = Tplink.variables['status']
            except Exception as er:
                print er
                print "device connection for {} is not successful".format(agent_id)
            # self.postgresAPI()
            self.updateStatus()
            x = {}
            x["agent_id"] = Tplink.variables['agent_id']
            x["dt"] = datetime.datetime.now().replace(microsecond=0).isoformat()
            x["plstatus"] = Tplink.variables['status']
            x["plcurrent"] = Tplink.variables['current']
            x["plvolt"] = Tplink.variables['volt']
            x["plpower"] = Tplink.variables['power']
            x["device_type"] = 'plugload'

            discovered_address = iotmodul.iothub_client_sample_run(x)


        def postgresAPI(self):

            self.connect_postgresdb()

            try:
                self.cur.execute("""
                    UPDATE tplink
                    SET status=%s, power=%s, last_scanned_time=%s
                    WHERE Tplink_id=%s
                 """, (Tplink.variables['status'], Tplink.variables['power'],
                       datetime.datetime.now(), agent_id))
                self.con.commit()

                self.cur.execute('UPDATE device_info SET status=%s WHERE device_id=%s',
                                 (Tplink.variables['status'], agent_id))
                self.con.commit()
                print "Update database: success"
            except Exception as er:
                print "Update database error: {}".format(er)

            try:
                self.cur.execute("""
                    INSERT INTO ts_Tplink
                    (datetime, status, power, Tplink_id, gateway_id)
                    VALUES (%s, %s, %s, %s, %s);""",
                    (datetime.datetime.now(), Tplink.variables['status'], Tplink.variables['power'], agent_id, '1'))
                self.con.commit()
                print 'Insert database: success'
            except Exception as er:
                print "Insert database error: {}".format(er)

            self.disconnect_postgresdb()

        def device_offline_detection(self):
            self.cur.execute("SELECT nickname FROM " + db_table_Tplink + " WHERE Tplink_id=%s",
                             (agent_id,))
            print agent_id
            if self.cur.rowcount != 0:
                device_nickname=self.cur.fetchone()[0]
                print device_nickname
            else:
                device_nickname = ''
            _db_notification_subject = 'BEMOSS Device {} {} went OFFLINE!!!'.format(device_nickname,agent_id)
            _email_subject = '#Attention: BEMOSS Device {} {} went OFFLINE!!!'.format(device_nickname,agent_id)
            _email_text = '#Attention: BEMOSS Device {}  {} went OFFLINE!!!'.format(device_nickname,agent_id)
            self.cur.execute("SELECT network_status FROM " + db_table_Tplink + " WHERE Tplink_id=%s",
                             (agent_id,))
            self.network_status = self.cur.fetchone()[0]
            print self.network_status
            if self.network_status=="OFFLINE":
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
                    self.cur.execute("SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",(self._active_alert_id,'1'))
                    if self.cur.rowcount != 0:
                        self._alert_email = self.cur.fetchall()
                        for single_email_1 in self._alert_email:
                            print single_email_1[0]
                            self.send_device_notification_email(single_email_1[0], _email_subject, _email_text)

                    # Send SMS if provided by user
                    self.cur.execute("SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",(self._active_alert_id,'2'))
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
            #_email_subject = '#Attention: BEMOSS Device {} has detected a high level of CO2!!!'.format(agent_id)
            # _email_text = 'Here is the detail of device status\n' + str(_tampering_device_msg) \
            #_email_text = 'The CO2 level has exceeded the defined range'
            emailService = EmailService()

            # Send Email
            emailService.sendEmail(email_fromaddr, _active_alert_email, email_username,
                                   email_password, _email_subject, _email_text, email_mailServer)

        def send_device_notification_sms(self, _active_alert_phone_number_misoperation, _sms_subject):
            print "INSIDE send_device_notification_sms"
            print _active_alert_phone_number_misoperation
            smsService = SMSService()
            smsService.sendSMS(email_fromaddr, _active_alert_phone_number_misoperation, email_username, email_password, _sms_subject, email_mailServer)

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
                self.cur.execute("SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",(self._active_alert_id,'1'))
                if self.cur.rowcount != 0:
                    self._alert_email = self.cur.fetchall()
                    for single_email_1 in self._alert_email:
                        print single_email_1[0]
                        self.send_device_notification_email(single_email_1[0], _email_subject, _email_text)

                # Send SMS if provided by user
                self.cur.execute("SELECT notify_address FROM " + db_table_alerts_notificationchanneladdress + " WHERE active_alert_id=%s AND notification_channel_id=%s",(self._active_alert_id,'2'))
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

        def updateStatus(self,states=None):

            # if states is not None:
            #     print "got state change:",states
            #     self.changed_variables = dict()
            #     if(self.get_variable('status') != 'ON' if states['status']==1 else 'OFF'):
            #         self.set_variable('status','ON' if states['status']==1 else 'OFF')
            #         self.changed_variables['status'] = log_variables['status']
            #     if 'power' in states:
            #         if(self.get_variable('power') != states['power']):
            #             self.changed_variables['power'] = log_variables['power']
            #             self.set_variable('power',states['power'])

                    # self.updatePostgresDB()

            topic = '/agent/ui/'+device_type+'/device_status_response/'+_topic_Agent_UI_tail
            # now = datetime.utcnow().isoformat(' ') + 'Z'
            headers = {
                'AgentID': agent_id,
                headers_mod.CONTENT_TYPE: headers_mod.CONTENT_TYPE.JSON,
                # headers_mod.DATE: now,
            }

            print topic
            #
            # if self.get_variable('power') is not None:
            #     _data={'device_id':agent_id, 'status':self.get_variable('status'), 'power':self.get_variable('power')}
            # else:
            #     _data={'device_id':agent_id, 'status':self.get_variable('status')}
            #
            # print topic
            # print "published!!!!! :{}".format(self.get_variable('status'))
            # message = json.dumps(_data)
            # message = message.encode(encoding='utf_8')
            # self.publish(topic, headers, message)

        # 4. updateUIBehavior (generic behavior)
        @matching.match_exact('/ui/agent/'+device_type+'/device_status/'+_topic_Agent_UI_tail)
        def updateUIBehavior(self, topic, headers, message, match):
            print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"), topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            #reply message
            self.updateStatus()

        # 5. deviceControlBehavior (generic behavior)
        @matching.match_exact('/ui/agent/'+device_type+'/update/'+_topic_Agent_UI_tail)
        def deviceControlBehavior(self,topic,headers,message,match):
            print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"),topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            #step1: change device status according to the receive message
            if self.isPostmsgValid(message[0]):  # check if the data is valid
                setDeviceStatusResult = Tplink.setDeviceStatus(json.loads(message[0]))
                #send reply message back to the UI
                topic = '/agent/ui/'+device_type+'/update_response/'+_topic_Agent_UI_tail
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
                print("The POST message is invalid, check status setting and try again\n")
                message = 'failure'
            self.publish(topic, headers, message)
            self.deviceMonitorBehavior() #Get device status, and get updated data

        def isPostmsgValid(self, postmsg):  # check validity of postmsg
            dataValidity = False
            try:
                _data = json.dumps(postmsg)
                _data = json.loads(_data)
                for k,v in _data.items():
                    if k == 'status':
                        dataValidity = True
                        break
            except:
                dataValidity = True
                print("dataValidity failed to validate data comes from UI")
            return dataValidity

        # 6. deviceIdentifyBehavior (generic behavior)
        @matching.match_exact('/ui/agent/'+device_type+'/identify/'+_topic_Agent_UI_tail)
        def deviceIdentifyBehavior(self,topic,headers,message,match):
            print "{} agent got\nTopic: {topic}".format(self.get_variable("agent_id"),topic=topic)
            print "Headers: {headers}".format(headers=headers)
            print "Message: {message}\n".format(message=message)
            #step1: change device status according to the receive message
            identifyDeviceResult = Tplink.identifyDevice()
            #TODO need to do additional checking whether the device setting is actually success!!!!!!!!
            #step2: send reply message back to the UI
            topic = '/agent/ui/identify_response/'+device_type+'/'+_topic_Agent_UI_tail
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


    Agent.__name__ = 'TplinkAgent'
    return Agent(**kwargs)

def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(TplinkAgent,
                       description='Tplink agent',
                       argv=argv)

if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
