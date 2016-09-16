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
from bemoss_lib.databases.cassandraAPI.cassandraDB import retrieve
import scipy
from scipy import integrate
import datetime
from dateutil.relativedelta import relativedelta
from bemoss_lib.databases.cassandraAPI import cassandraDB

utils.setup_logging()
_log = logging.getLogger(__name__)

publish_periodic = 5
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
                        'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0}
    def __init__(self, config_path, **kwargs):
        super(PowermeterAppAgent, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)

    def setup(self):
        # Demonstrate accessing a value from the config file
        _log.info(self.config['message'])
        self._agent_id = self.config['agentid']
        # Always call the base class setup()
        super(PowermeterAppAgent, self).setup()

    def parse_resultset(self, variables, data_point, result_set):
        x = [[lst[variables.index('time')], lst[variables.index(data_point)] + 0.0]
             for lst in result_set if lst[variables.index(data_point)] is not None]

        y = [lst[variables.index('time')]
             for lst in result_set if lst[variables.index(data_point)] is not None]

        newTime = []
        checkEle = x[0][0]
        newTime.append(checkEle)

        newData = []
        checkData = x[0][1]
        newData.append(x[0][1])

        for lst in x:
            if (lst[0] != checkEle):
                newTime.append(int(checkEle))
                newData.append(lst[1])
            else:
                if (lst[1] > checkData):
                    newData[-1:] = checkData
            checkEle = lst[0]

        del newTime[0]
        del newData[0]

        return newTime, newData

    def integrate_power(self, AgentID, variable, start_time, end_time, ):
        data_points, rs = retrieve(AgentID, vars=['time', variable], startTime=start_time,
                                   endTime=end_time)
        try:
            time, data = self.parse_resultset(data_points, variable, rs)
            wattsec = scipy.integrate.simps(data, time, axis=-1, even='avg')
            energy_kWh = wattsec / (3600 * 1000 * 1000)
        except:
            energy_kWh = 0
        return energy_kWh

    def daily_energy_calculate(self):
        data = {}
        time_now = datetime.datetime.now()
        weekday = time_now.weekday()
        end_time = time_now
        start_time = end_time.replace(hour=0, minute=0, second=0)
        data['solar_daily_energy'] = self.integrate_power('SmappeePowerMeter', 'solar_activepower', start_time, end_time)
        if (weekday == 5)|(weekday == 6)|(weekday == 7):  #provide "weekday = 7" for holiday rate
            data['daily_energy'] = self.integrate_power('SmappeePowerMeter', 'load_activepower', start_time, end_time)
            data['daily_bill'] = data['daily_energy'] * OFFPEAK_RATE
            data['daily_light_energy'] = data['daily_energy'] * 0.01
            data['daily_light_bill'] = data['daily_light_energy'] * OFFPEAK_RATE
            data['daily_AC_energy'] = data['daily_energy'] * 0.5
            data['daily_AC_bill'] = data['daily_light_energy'] * OFFPEAK_RATE
            data['daily_plug_energy'] = data['daily_energy'] * 0.3
            data['daily_plug_bill'] = data['daily_light_energy'] * OFFPEAK_RATE
            data['daily_EV_energy'] = data['daily_energy'] * 0.19
            data['daily_EV_bill'] = data['daily_light_energy'] * OFFPEAK_RATE
        else:
            #Peak Period --- 09:00 - 22:00
            end_time = time_now.replace(hour=22, minute=0, second=0)
            start_time = time_now.replace(hour=9, minute=0, second=1)
            data['daily_energy_peak'] = self.integrate_power('SmappeePowerMeter', 'load_activepower', start_time, end_time)
            data['daily_bill_peak'] = data['daily_energy_peak'] * PEAK_RATE
            data['daily_light_energy_peak'] = data['daily_energy_peak'] * 0.01
            data['daily_light_bill_peak'] = data['daily_light_energy_peak'] * PEAK_RATE
            data['daily_AC_energy_peak'] = data['daily_energy_peak'] * 0.5
            data['daily_AC_bill_peak'] = data['daily_AC_energy_peak'] * PEAK_RATE
            data['daily_plug_energy_peak'] = data['daily_energy_peak'] * 0.3
            data['daily_plug_bill_peak'] = data['daily_plug_energy_peak'] * PEAK_RATE
            data['daily_EV_energy_peak'] = data['daily_energy_peak'] * 0.5
            data['daily_EV_bill_peak'] = data['daily_EV_energy_peak'] * PEAK_RATE

            #Off Peak Period 1  --- 0:00 - 09:00
            end_time = time_now.replace(hour=9, minute=0, second=0)
            start_time = time_now.replace(hour=0, minute=0, second=0)
            data['daily_energy_offpeak1'] = self.integrate_power('SmappeePowerMeter', 'load_activepower', start_time, end_time)
            data['daily_bill_offpeak1'] = data['daily_energy_offpeak1'] * OFFPEAK_RATE
            data['daily_light_energy_offpeak1'] = data['daily_energy_offpeak1'] * 0.01
            data['daily_light_bill_offpeak1'] = data['daily_light_energy_offpeak1'] * OFFPEAK_RATE
            data['daily_AC_energy_offpeak1'] = data['daily_energy_offpeak1'] * 0.5
            data['daily_AC_bill_offpeak1'] = data['daily_AC_energy_offpeak1'] * OFFPEAK_RATE
            data['daily_plug_energy_offpeak1'] = data['daily_energy_offpeak1'] * 0.3
            data['daily_plug_bill_offpeak1'] = data['daily_plug_energy_offpeak1'] * OFFPEAK_RATE
            data['daily_EV_energy_offpeak1'] = data['daily_energy_offpeak1'] * 0.5
            data['daily_EV_bill_offpeak1'] = data['daily_EV_energy_offpeak1'] * OFFPEAK_RATE

            #Off Peak Period 2 --- 22:00 - 23:59
            end_time = time_now.replace(hour=23, minute=59, second=59)
            start_time = time_now.replace(hour=22, minute=0, second=1)
            data['daily_energy_offpeak2'] = self.integrate_power('SmappeePowerMeter', 'load_activepower', start_time, end_time)
            data['daily_bill_offpeak2'] = data['daily_energy_offpeak2'] * OFFPEAK_RATE
            data['daily_light_energy_offpeak2'] = data['daily_energy_offpeak2'] * 0.01
            data['daily_light_bill_offpeak2'] = data['daily_light_energy_offpeak2'] * OFFPEAK_RATE
            data['daily_AC_energy_offpeak2'] = data['daily_energy_offpeak2'] * 0.5
            data['daily_AC_bill_offpeak2'] = data['daily_AC_energy_offpeak2'] * OFFPEAK_RATE
            data['daily_plug_energy_offpeak2'] = data['daily_energy_offpeak2'] * 0.3
            data['daily_plug_bill_offpeak2'] = data['daily_plug_energy_offpeak2'] * OFFPEAK_RATE
            data['daily_EV_energy_offpeak2'] = data['daily_energy_offpeak2'] * 0.5
            data['daily_EV_bill_offpeak2'] = data['daily_EV_energy_offpeak2'] * OFFPEAK_RATE

            #sum all period
            data['daily_energy'] = data['daily_energy_peak'] + data['daily_energy_offpeak1'] + data['daily_energy_offpeak2']
            data['daily_bill'] = data['daily_bill_peak'] + data['daily_bill_offpeak1'] + data['daily_bill_offpeak2']
            data['daily_light_energy'] = data['daily_light_energy_peak'] + data['daily_light_energy_offpeak1'] + data['daily_light_energy_offpeak2']
            data['daily_light_bill'] = data['daily_light_bill_peak'] + data['daily_light_bill_offpeak1'] + data['daily_light_bill_offpeak2']
            data['daily_AC_energy'] = data['daily_AC_energy_peak'] + data['daily_AC_energy_offpeak1'] + data['daily_AC_energy_offpeak2']
            data['daily_AC_bill'] = data['daily_AC_bill_peak'] + data['daily_AC_bill_offpeak1'] + data['daily_AC_bill_offpeak2']
            data['daily_plug_energy'] = data['daily_plug_energy_peak'] + data['daily_plug_energy_offpeak1'] + data['daily_plug_energy_offpeak2']
            data['daily_plug_bill'] = data['daily_plug_bill_peak'] + data['daily_plug_bill_offpeak1'] + data['daily_plug_bill_offpeak2']
            data['daily_EV_energy'] = data['daily_EV_energy_peak'] + data['daily_EV_energy_offpeak1'] + data['daily_EV_energy_offpeak2']
            data['daily_EV_bill'] = data['daily_EV_bill_peak'] + data['daily_EV_bill_offpeak1'] + data['daily_EV_bill_offpeak2']

        #------Daily_Energy_Backup-------
        end_day_time = time_now.replace(hour=23, minute=59, second=59)
        delta_time = datetime.timedelta(seconds=19)
        if ((time_now >= (end_day_time - delta_time))&(time_now <= end_day_time)):
            try:
                variables = {'load_energy': data['daily_energy'], 'solar_energy': data['solar_daily_energy'],
                             'load_bill': data['daily_bill'], 'light_energy':data['daily_light_energy'],
                             'light_bill': data['daily_light_bill'], 'AC_energy': data['daily_AC_energy'],
                             'AC_bill': data['daily_AC_bill'], 'plug_energy': data['daily_plug_energy'],
                             'plug_bill': data['daily_plug_bill'], 'EV_energy': data['daily_EV_energy'],
                             'EV_bill': data['daily_EV_bill']}
                cassandraDB.insert('DailyData', variables, log_variables)
                print('Data Pushed to cassandra as a backup')
            except Exception as er:
                print("ERROR: {} fails to update cassandra database".format('DailyData'))
                print er

        return data

    def last_day_energy_calculate(self):
        data = {}
        time_now = datetime.datetime.now()
        delta_time = datetime.timedelta(days=1)
        time = time_now - delta_time
        end_time = time.replace(hour=23, minute=59, second=59)
        start_time = time.replace(hour=0, minute=0, second=0)
        try:
            data_points, rs = retrieve('DailyData', vars=['load_energy', 'solar_energy', 'load_bill', 'light_energy',
                                                      'light_bill', 'AC_energy', 'AC_bill', 'plug_energy', 'plug_bill',
                                                      'EV_energy', 'EV_bill'], startTime=start_time, endTime=end_time)
            data['last_day_energy'] = rs[0]
            data['solar_last_day_energy'] = rs[1]
            data['last_day_bill'] = rs[2]
            data['last_day_light_energy'] = rs[3]
            data['last_day_light_bill'] = rs[4]
            data['last_day_AC_energy'] = rs[5]
            data['last_day_AC_bill'] = rs[6]
            data['last_day_plug_energy'] = rs[7]
            data['last_day_plug_bill'] = rs[8]
            data['last_day_EV_energy'] = rs[9]
            data['last_day_EV_bill'] = rs[10]
        except:
            data['last_day_energy'] = 0
            data['solar_day_energy'] = 0
            data['last_day_bill'] = 0
            data['last_day_light_energy'] = 0
            data['last_day_light_bill'] = 0
            data['last_day_AC_energy'] = 0
            data['last_day_AC_bill'] = 0
            data['last_day_plug_energy'] = 0
            data['last_day_plug_bill'] = 0
            data['last_day_EV_energy'] = 0
            data['last_day_EV_bill'] = 0

        return data

    def monthly_energy_usage_calculate(self):
        date_end_month = datetime.datetime.now() + relativedelta(day=31)
        end_time = date_end_month.replace(hour=23, minute=59, second=59)
        start_time = date_end_month.replace(day=1, hour=0, minute=0, second=0)
        data_points, rs = retrieve('SmappeePowerMeter', vars=['time', 'load_activepower'], startTime=start_time,
                                   endTime=end_time)

        try:
            time, data = self.parse_resultset(data_points, 'load_activepower', rs)
            wattsec = scipy.integrate.simps(data, time, axis=-1, even='avg')
            energy_kWh = wattsec / (3600 * 1000 * 1000)
        except:
            energy_kWh = 0

        return energy_kWh

    def last_month_energy_usage_calculate(self):
        last_month = datetime.datetime.now() - relativedelta(months=1)
        end_day_in_last_month = last_month + relativedelta(day=31)

        end_time = end_day_in_last_month.replace(hour=23, minute=59, second=59)
        start_time = last_month.replace(day=1, hour=0, minute=0, second=0)
        data_points, rs = retrieve('SmappeePowerMeter', vars=['time', 'load_activepower'], startTime=start_time,
                                   endTime=end_time)

        try:
            time, data = self.parse_resultset(data_points, 'load_activepower', rs)
            wattsec = scipy.integrate.simps(data, time, axis=-1, even='avg')
            energy_kWh = wattsec / (3600 * 1000 * 1000)
        except:
            energy_kWh = 0

        return energy_kWh

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
        daily_data = self.daily_energy_calculate()
        if (daily_data['daily_energy'] < PowermeterAppAgent.check_daily_data['daily_energy']):
            daily_data['daily_energy'] = PowermeterAppAgent.check_daily_data['daily_energy']

        if (daily_data['daily_bill'] < PowermeterAppAgent.check_daily_data['daily_bill']):
            daily_data['daily_bill'] = PowermeterAppAgent.check_daily_data['daily_bill']

        if (daily_data['daily_light_bill'] < PowermeterAppAgent.check_daily_data['daily_light_bill']):
            daily_data['daily_light_bill'] = PowermeterAppAgent.check_daily_data['daily_light_bill']

        if (daily_data['daily_AC_bill'] < PowermeterAppAgent.check_daily_data['daily_AC_bill']):
            daily_data['daily_AC_bill'] = PowermeterAppAgent.check_daily_data['daily_AC_bill']

        if (daily_data['daily_plug_bill'] < PowermeterAppAgent.check_daily_data['daily_plug_bill']):
            daily_data['daily_plug_bill'] = PowermeterAppAgent.check_daily_data['daily_plug_bill']

        if (daily_data['daily_EV_bill'] < PowermeterAppAgent.check_daily_data['daily_EV_bill']):
            daily_data['daily_EV_bill'] = PowermeterAppAgent.check_daily_data['daily_EV_bill']

        daily_energy_usage = round(daily_data['daily_energy'], 2)
        daily_electricity_bill = round(daily_data['daily_bill'], 2)
        daily_bill_light = round(daily_data['daily_light_bill'], 2)
        daily_bill_AC = round(daily_data['daily_AC_bill'], 2)
        daily_bill_plug = round(daily_data['daily_plug_bill'], 2)
        daily_bill_EV = round(daily_data['daily_EV_bill'], 2)

        last_day_data = self.last_day_energy_calculate()
        last_day_energy_usage = round(last_day_data['last_day_energy'], 2)
        last_day_bill = round(last_day_data['last_day_bill'], 2)
        last_day_bill_compare = round(daily_electricity_bill - last_day_bill, 2)
        last_day_bill_light = round(last_day_data['last_day_light_bill'], 2)
        last_day_bill_AC = round(last_day_data['last_day_AC_bill'], 2)
        last_day_bill_plug = round(last_day_data['last_day_plug_bill'], 2)
        last_day_bill_EV = round(last_day_data['last_day_EV_bill'], 2)

        monthly_energy_usage = round(self.monthly_energy_usage_calculate(), 2)
        last_month_energy_usage = round(self.last_month_energy_usage_calculate(), 2)
        monthly_electricity_bill = round(monthly_energy_usage * 3.5, 2)
        last_month_bill = round(last_month_energy_usage * 3.5, 2)
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

        monthly_bill_AC = round(monthly_electricity_bill * 0.5, 2)
        monthly_bill_light = round(monthly_electricity_bill * 0.05, 2)
        monthly_bill_plug = round(monthly_electricity_bill * 0.15, 2)
        monthly_bill_EV = round(monthly_electricity_bill * 0.3, 2)

        last_month_bill_AC = last_month_bill * 0.5
        last_month_bill_light = last_month_bill * 0.05
        last_month_bill_plug = last_month_bill * 0.15
        last_month_bill_EV = last_month_bill * 0.2

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
        netzero_condition = random.choice([True, False])
        if (netzero_condition):
            netzero_onsite_generation = round((monthly_electricity_bill/3.5*0.7*12), 2)
            netzero_energy_consumption = round((monthly_electricity_bill/3.5*0.3*12), 2)
        else:
            netzero_onsite_generation = round((monthly_electricity_bill / 3.5 * 0.3 * 12), 2)
            netzero_energy_consumption = round((monthly_electricity_bill / 3.5 * 0.7 * 12), 2)

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
