# -*- coding: utf-8 -*-
'''

#__author__ = "PEA Team"
#__credits__ = ""
#__version__ = "1.0"
#__maintainer__ = "PEA Team"
#__created__ = "2016-09-18 17:21:50"
#__lastUpdated__ = "2016-09-18 17:21:50"
'''
from bemoss_lib.databases.cassandraAPI.cassandraDB import retrieve
import scipy
from scipy import integrate
import datetime
import numpy as np
from dateutil.relativedelta import relativedelta
from bemoss_lib.databases.cassandraAPI import cassandraDB

#Global variables
OFFPEAK_RATE = 2.6369
PEAK_RATE = 5.7982
connection_established = False
bCluster, bSpace, keyspace_name, replication_factor = None, None, None, None

check_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                    'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0}

check_last_day_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                       'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0}

#Dictionary of Variables supposed to be saved into timeseries database
log_variables = {'load_energy': 'double', 'solar_energy': 'double', 'load_bill':'double',
                 'light_energy': 'double', 'light_bill': 'double', 'AC_energy':'double', 'AC_bill':'double',
                 'plug_energy': 'double', 'plug_bill': 'double', 'EV_energy': 'double', 'EV_bill' :'double'}

def parse_resultset(variables, data_point, result_set):
    x = [[lst[variables.index('time')], lst[variables.index(data_point)] + 0.0]
         for lst in result_set if lst[variables.index(data_point)] is not None]
    newTime = []
    checkEle = x[0][0]
    newTime.append(checkEle)

    newData = []
    checkData = x[0][1]
    newData.append(x[0][1])

    for lst in x:
        if (lst[0] > checkEle):
            if ((lst[0] - checkEle) < 30000):
                # print "less than 1 minute"
                # print ("lst : {}".format(lst[0]))
                # print ("checkEle : {}".format(checkEle))
                newTime.append(int(checkEle))
                newData.append(lst[1])
                # checkEle = lst[0]
                # checkData = lst[1]
            else:
                # print "more than 1 minute"
                # print ("lst : {}".format(lst[0]))
                # print ("checkEle : {}".format(checkEle))
                newTime.append(int(checkEle)+1)
                newData.append(0)
                checkEle = lst[0]
                checkData = 0
                continue
            # checkEle = lst[0]
            # checkData = lst[1]
        elif lst[0] is checkEle:
            if (lst[1] > checkData):
                newData[-1:] = checkData
            # checkEle = lst[0]
            # checkData = lst[1]
        # else:
        #     checkEle = lst[0]
        #     checkData = lst[1]
        checkEle = lst[0]
        checkData = lst[1]

    del newTime[0]
    del newData[0]

    len_newTime = len(newTime)
    len_newData = len(newData)

    if not ((len_newData%2)&(len_newTime%2)):
        del newTime[len(newTime)-1]
        del newData[len(newData)-1]

    return newTime, newData


def integrate_power(AgentID, variable, start_time, end_time):
    # time_now = datetime.datetime.now()
    # end_time = time_now.replace(day=20, hour=17, minute=59, second=59)
    # start_time = time_now.replace(day=20, hour=0, minute=00, second=0)
    # # start_time = end_time.replace(hour=13)

    try:
        data_points, rs = retrieve(AgentID, vars=['time', str(variable)], startTime=start_time, endTime=end_time)
        # print rs
        if (len(rs)):
            try:
                time, data = parse_resultset(data_points, str(variable), rs)
                wattsec = scipy.integrate.simps(data, time, even='first')
                energy_kWh = wattsec / (3600 * 1000 * 1000)
                result = True
            except:
                energy_kWh = 0
                result = False
        else:
            energy_kWh = 0
            result = True
    except:
        energy_kWh = 0
        result = False
    return energy_kWh, result


def energy_calculate(AgentID, parameter, date):
    ''' : AgentID is the name of table in Bemossspace (Cassandra DB)
        : parameter is the name of column in table that will be integrated
        : date is day that would like to know how much energy in that day
        if would like to know the energy in all day should send by using following example:
        >> time_now = datetime.datetime.now()
        >> date = time_now.replace(hour=23, minute=59, second=59)'''
    data = {}
    weekday = date.weekday()

    # Off Peak Period 1  --- 0:00 - 09:00
    end_time = date.replace(hour=9, minute=0, second=0)
    start_time = date.replace(hour=0, minute=0, second=0)
    data['daily_energy_offpeak1'], result = integrate_power(str(AgentID), str(parameter), start_time, end_time)
    if result is True:
        data['daily_bill_offpeak1'] = data['daily_energy_offpeak1'] * OFFPEAK_RATE
    else:
        data['daily_energy'] = 0
        data['daily_bill'] = 0
        return data, True

    if (date > end_time):
        # Peak Period --- 09:00 - 15:00
        end_time = date.replace(hour=15, minute=0, second=0)
        start_time = date.replace(hour=9, minute=0, second=1)
        # print end_time
        # print start_time
        data['daily_energy_peak1'], result = integrate_power(AgentID, parameter, start_time, end_time)
        if result is True:
            if (weekday == 5) | (weekday == 6) | (weekday == 7):
                data['daily_bill_peak1'] = data['daily_energy_peak1'] * OFFPEAK_RATE
            else:
                data['daily_bill_peak1'] = data['daily_energy_peak1'] * PEAK_RATE
        else:
            data['daily_energy'] = data['daily_energy_offpeak1']
            data['daily_bill'] = data['daily_bill_offpeak1']
            return data, True

        if (date > end_time):
            # Peak Period --- 15:00 - 22:00
            end_time = date.replace(hour=22, minute=0, second=0)
            start_time = date.replace(hour=15, minute=0, second=1)
            # print end_time
            # print start_time
            data['daily_energy_peak2'], result = integrate_power(AgentID, parameter, start_time, end_time)
            if result is True:
                if (weekday == 5) | (weekday == 6) | (weekday == 7):
                    data['daily_bill_peak1'] = data['daily_energy_peak1'] * OFFPEAK_RATE
                else:
                    data['daily_bill_peak2'] = data['daily_energy_peak2'] * PEAK_RATE
            else:
                data['daily_energy'] = data['daily_energy_offpeak1'] + data['daily_energy_peak1']
                data['daily_bill'] = data['daily_bill_offpeak1'] + data['daily_bill_peak1']
                return data, True

            if (date >= end_time):
                # Off Peak Period 2 --- 22:00 - 23:59
                end_time = date.replace(hour=23, minute=59, second=59)
                start_time = date.replace(hour=22, minute=0, second=1)
                data['daily_energy_offpeak2'], result = integrate_power(str(AgentID), str(parameter), start_time, end_time)
                if result is True:
                    data['daily_bill_offpeak2'] = data['daily_energy_offpeak2'] * OFFPEAK_RATE
                else:
                    data['daily_energy'] = data['daily_energy_offpeak1'] + data['daily_energy_peak1'] + data['daily_energy_peak2']
                    data['daily_bill'] = data['daily_bill_offpeak1'] + data['daily_bill_peak1'] + data['daily_bill_peak2']
                    return data, True
            else:
                data['daily_energy_offpeak2'] = 0
                data['daily_bill_offpeak2'] = 0
        else:
            data['daily_energy_peak2'] = 0
            data['daily_bill_peak2'] = 0
            data['daily_energy_offpeak2'] = 0
            data['daily_bill_offpeak2'] = 0
    else:
        data['daily_energy_peak1'] = 0
        data['daily_bill_peak1'] = 0
        data['daily_energy_peak2'] = 0
        data['daily_bill_peak2'] = 0
        data['daily_energy_offpeak2'] = 0
        data['daily_bill_offpeak2'] = 0
    # sum all period
    data['daily_energy'] = data['daily_energy_peak1'] + data['daily_energy_peak2'] + data['daily_energy_offpeak1'] + data['daily_energy_offpeak2']
    data['daily_bill'] = data['daily_bill_peak1'] + data['daily_bill_peak2'] + data['daily_bill_offpeak1'] + data['daily_bill_offpeak2']
    return data, result


def daily_energy_calculate(column_name, day):

    if column_name is "load":
        AgentID = 'SmappeePowerMeter'
        variable = 'load_activepower'
    elif column_name is "solar":
        AgentID = 'SmappeePowerMeter'
        variable = 'solar_activepower'
    elif column_name is "grid":
        AgentID = 'SmappeePowerMeter'
        variable = 'grid_activepower'
    elif column_name is "EV":
        AgentID = '3WIS221445K1200321'
        variable = 'power'

    count = 0
    data, result = energy_calculate(AgentID, variable, day)
    while result is False:
        if count < 10:
            data, result = energy_calculate(AgentID, variable, day)
        else:
            data['daily_energy'] = 0
            data['daily_bill'] = 0
            break
        count += 1

    return data


def day_energy_bill_calculation(check_data, day):
    data = {}
    load_data = daily_energy_calculate("load", day)
    EV_data = daily_energy_calculate("EV", day)
    solar_data = daily_energy_calculate("solar", day)
    grid_data = daily_energy_calculate("grid", day)

    data['daily_energy'] = load_data['daily_energy']
    data['daily_bill'] = grid_data['daily_bill']
    data['daily_light_energy'] = (load_data['daily_energy'] - EV_data['daily_energy']) * 0.2
    data['daily_light_bill'] = (load_data['daily_bill'] - EV_data['daily_bill']) * 0.2
    data['daily_AC_energy'] = (load_data['daily_energy'] - EV_data['daily_energy']) * 0.5
    data['daily_AC_bill'] = (load_data['daily_bill'] - EV_data['daily_bill']) * 0.5
    data['daily_plug_energy'] = (load_data['daily_energy'] - EV_data['daily_energy']) * 0.3
    data['daily_plug_bill'] = (load_data['daily_bill'] - EV_data['daily_bill']) * 0.3
    data['daily_EV_energy'] = EV_data['daily_energy']
    data['daily_EV_bill'] = EV_data['daily_bill']
    data['solar_energy'] = solar_data['daily_energy']

    if (data['daily_energy'] < check_data['daily_energy']):
        data['daily_energy'] = check_data['daily_energy']
        if (data['daily_energy'] < 0):
            data['daily_energy'] = 0

    if (data['daily_bill'] < check_data['daily_bill']):
        data['daily_bill'] = check_data['daily_bill']
        if (data['daily_bill'] < 0):
            data['daily_bill'] = 0

    if (data['daily_light_bill'] < check_data['daily_light_bill']):
        data['daily_light_bill'] = check_data['daily_light_bill']
        if (data['daily_light_bill'] < 0):
            data['daily_light_bill'] = 0

    if (data['daily_AC_bill'] < check_data['daily_AC_bill']):
        data['daily_AC_bill'] = check_data['daily_AC_bill']
        if (data['daily_AC_bill'] < 0):
            data['daily_AC_bill'] = 0

    if (data['daily_plug_bill'] < check_data['daily_plug_bill']):
        data['daily_plug_bill'] = check_data['daily_plug_bill']
        if (data['daily_plug_bill'] < 0):
            data['daily_plug_bill'] = 0

    if (data['daily_EV_bill'] < check_data['daily_EV_bill']):
        data['daily_EV_bill'] = check_data['daily_EV_bill']
        if (data['daily_EV_bill'] < 0):
            data['daily_EV_bill'] = 0

    if (data['solar_energy'] < check_data['solar_energy']):
        data['solar_energy'] = check_data['solar_energy']
        if (data['solar_energy'] < 0):
            data['solar_energy'] = 0

    # ------Daily_Energy_Backup-------
    time_now = datetime.datetime.now()
    end_day_time = time_now.replace(hour=23, minute=59, second=59)
    delta_time = datetime.timedelta(seconds=19)
    if ((time_now >= (end_day_time - delta_time)) & (time_now <= end_day_time)):
        try:
            variables = {'load_energy': data['daily_energy'],
                         'solar_energy': data['solar_daily_energy'],
                         'load_bill': data['daily_bill'], 'light_energy': data['daily_light_energy'],
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


def monthly_energy_bill_calculation(month):
    month_data = {}
    if month is "Current":
        month_time = datetime.datetime.now()
        end_date_of_month = month_time.day
        end_day_of_month = month_time
    elif month is "Last":
        month_time = datetime.datetime.now() - relativedelta(months=1)
        end_last_month = month_time + relativedelta(day=31)
        end_date_of_month = end_last_month.day
        end_day_of_month = end_last_month

    month_data['month_energy'] = 0
    month_data['month_bill'] = 0
    month_data['month_light_bill'] = 0
    month_data['month_AC_bill'] = 0
    month_data['month_plug_bill'] = 0
    month_data['month_EV_bill'] = 0

    check_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                  'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0, 'solar_energy': 0.0}

    for n in np.arange(1, end_date_of_month, 1):
        date = month_time.replace(day=n, hour=23, minute=59, second=59)
        data = last_day_usage(date)
        month_data['month_energy'] = month_data['month_energy'] + data['last_day_energy']
        month_data['month_bill'] = month_data['month_bill'] + data['last_day_bill']
        month_data['month_light_bill'] = month_data['month_light_bill'] + data['last_day_light_bill']
        month_data['month_AC_bill'] = month_data['month_AC_bill'] + data['last_day_AC_bill']
        month_data['month_plug_bill'] = month_data['month_plug_bill'] + data['last_day_plug_bill']
        month_data['month_EV_bill'] = month_data['month_EV_bill'] + data['last_day_EV_bill']

    data = day_energy_bill_calculation(check_data, end_day_of_month)
    month_data['month_energy'] = month_data['month_energy'] + data['daily_energy']
    month_data['month_bill'] = month_data['month_bill'] + data['daily_bill']
    month_data['month_light_bill'] = month_data['month_light_bill'] + data['daily_light_bill']
    month_data['month_AC_bill'] = month_data['month_AC_bill'] + data['daily_AC_bill']
    month_data['month_plug_bill'] = month_data['month_plug_bill'] + data['daily_plug_bill']
    month_data['month_EV_bill'] = month_data['month_EV_bill'] + data['daily_EV_bill']
    return month_data


def annual_energy_calculate():

    annual_load_energy = 0
    annual_solar_energy = 0
    time_now = datetime.datetime.now()
    start_date = time_now.replace(month=1, day=1, hour=0, minute=0, second=0)
    delta_date = datetime.timedelta(days=1)
    check_data = {'daily_energy': 0.0, 'daily_bill': 0.0, 'daily_light_bill': 0.0, 'daily_AC_bill': 0.0,
                  'daily_plug_bill': 0.0, 'daily_EV_bill': 0.0, 'solar_energy': 0.0}

    while (start_date < time_now):

        date = start_date.replace(hour=23, minute=59, second=59)
        last_data = last_day_usage(date)
        annual_load_energy = annual_load_energy + last_data['last_day_energy']
        annual_solar_energy = annual_solar_energy + last_data['solar_last_day_energy']
        start_date = start_date + delta_date

    daily_data = day_energy_bill_calculation(check_data, time_now)
    annual_load_energy = annual_load_energy + daily_data['daily_energy']
    annual_solar_energy = annual_solar_energy + daily_data['solar_energy']

    return annual_load_energy, annual_solar_energy


def last_day_usage(end_time):
    data = {}
    # start_time = end_time.replace(hour=10, minute=10, second=50)
    start_time = end_time.replace(hour=23, minute=59, second=50)
    try:
        data_points, rs = retrieve('DailyData', vars=['load_energy', 'solar_energy', 'load_bill', 'light_energy',
                                                      'light_bill', 'AC_energy', 'AC_bill', 'plug_energy', 'plug_bill',
                                                      'EV_energy', 'EV_bill'], startTime=start_time, endTime=end_time)
        data['last_day_energy'] = rs[len(rs) - 1][0]
        data['solar_last_day_energy'] = rs[len(rs) - 1][1]
        data['last_day_bill'] = rs[len(rs) - 1][2]
        data['last_day_light_energy'] = rs[len(rs) - 1][3]
        data['last_day_light_bill'] = rs[len(rs) - 1][4]
        data['last_day_AC_energy'] = rs[len(rs) - 1][5]
        data['last_day_AC_bill'] = rs[len(rs) - 1][6]
        data['last_day_plug_energy'] = rs[len(rs) - 1][7]
        data['last_day_plug_bill'] = rs[len(rs) - 1][8]
        data['last_day_EV_energy'] = rs[len(rs) - 1][9]
        data['last_day_EV_bill'] = rs[len(rs) - 1][10]
    except:
        data['last_day_energy'] = 0
        data['solar_last_day_energy'] = 0
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


if __name__ == '__main__':
    print ("test")
    # end_time = datetime.datetime.now()
    # # start_time = end_time.replace(hour=13)
    # start_time = end_time.replace(hour=14, minute=00, second=59)
    # end_time = end_time.replace(hour=17, minute=30)
    # data_points, rs = retrieve('3WIS221445K1200321', vars=['time', 'power', 'status'], startTime=start_time, endTime=end_time)
    # x, y = parse_resultset(data_points, 'power', rs)
    # print y
    #
    # a, b = parse_resultset(data_points, 'status', rs)
    # print b

    # EV_data = daily_energy_calculate("load", start_time)
    # print EV_data

    # annual_load_energy, annual_solar_energy = annual_energy_calculate()
    # print annual_load_energy
    # print annual_solar_energy
