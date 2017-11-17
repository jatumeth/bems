from __future__ import division
#from datetime import datetime
from datetime import *
from volttron.platform.agent import BaseAgent, PublishMixin, periodic
from volttron.platform.agent import utils, matching
#from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import *
from volttron.platform.messaging import headers as headers_mod

import settings
import json
import psycopg2
import psycopg2.extras
import datetime
import logging
import sys
import numpy as np
import calendar

import requests
from pandas import DataFrame
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler



utils.setup_logging()
_log = logging.getLogger(__name__)
publish_periodic = 86400

def LoadForecastAppAgent(config_path, **kwargs):
    config = utils.load_config(config_path)

    def get_config(name):
        try:
            kwargs.pop(name)
        except KeyError:
            return config.get(name, '')

    # 1. @params agent
    agent_id = get_config('agent_id')

    # 2. @param DB interfaces
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    db_database = settings.DATABASES['default']['NAME']
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    # db_table_load_ac = "ts_feature_load"
    # db_table_load_fc = "ts_load_fc"
    
    class Agent(PublishMixin, BaseAgent):
        '''Calculate energy and bill from evergy power sources'''

        def __init__(self, **kwargs):
            super(Agent, self).__init__(**kwargs)
            self.variables = kwargs
            print("init")

        def set_variable(self, k, v):  # postgre k=key, v=value
            self.variables[k] = v

        def get_variable(self, k):
            return self.variables.get(k, None)  # default of get variable is none

        def setup(self):
            super(Agent, self).setup()
            # Demonstrate accessing value from the config file
            _log.info(config['message'])
            self._agent_id = agent_id
            self.publish_forecast()

        @periodic(publish_periodic)
        def publish_forecast(self):
            self.connect_postgresdb()
            self.collect_data()
            self.get_load_forecast()
            self.disconnect_postgresdb()
            print("new forecast: success")

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

        def collect_data(self):
            self.query_df = "SELECT * FROM ts_feature_load ORDER BY datetime"
            self.data_set = pd.read_sql_query(self.query_df,self.con)
            print("collect data: success")

        def get_load_forecast(self):
            try:
                x_value = self.data_set[['tempc','humidity','h0','h1','h2','h3','h4','h5','h6','h7','h8','h9','h10','h11', 'h12', 'h13','h14','h15','h16','h17','h18','h19','h20','h21','h22','h23']]
                print('OK')
            except Exception as er:
                print "update data base error: {}".format(er)

            try:
                y_value = self.data_set['power']
                print('OK')
            except Exception as er:
                print "update data base error: {}".format(er)


            x_train, x_test, y_train, y_test = train_test_split(x_value,y_value, test_size=0.3, random_state=101)
            scaler = MinMaxScaler()
            x_train = pd.DataFrame(data=scaler.fit_transform(x_train), columns=x_train.columns)
            x_test = pd.DataFrame(data=scaler.fit_transform(x_test), columns=x_test.columns)
            y_train = y_train.reset_index()['power']
            y_test = y_test.reset_index()['power']

            tempc = tf.feature_column.numeric_column('tempc')
            humidity = tf.feature_column.numeric_column('humidity')
            hour0 = tf.feature_column.numeric_column('h0')
            hour1 = tf.feature_column.numeric_column('h1')
            hour2 = tf.feature_column.numeric_column('h2')
            hour3 = tf.feature_column.numeric_column('h3')
            hour4 = tf.feature_column.numeric_column('h4')
            hour5 = tf.feature_column.numeric_column('h5')
            hour6 = tf.feature_column.numeric_column('h6')
            hour7 = tf.feature_column.numeric_column('h7')
            hour8 = tf.feature_column.numeric_column('h8')
            hour9 = tf.feature_column.numeric_column('h9')
            hour10 = tf.feature_column.numeric_column('h10')
            hour11 = tf.feature_column.numeric_column('h11')
            hour12 = tf.feature_column.numeric_column('h12')
            hour13 = tf.feature_column.numeric_column('h13')
            hour14 = tf.feature_column.numeric_column('h14')
            hour15 = tf.feature_column.numeric_column('h15')
            hour16 = tf.feature_column.numeric_column('h16')
            hour17 = tf.feature_column.numeric_column('h17')
            hour18 = tf.feature_column.numeric_column('h18')
            hour19 = tf.feature_column.numeric_column('h19')
            hour20 = tf.feature_column.numeric_column('h20')
            hour21 = tf.feature_column.numeric_column('h21')
            hour22 = tf.feature_column.numeric_column('h22')
            hour23 = tf.feature_column.numeric_column('h23')
            fea_cols = [tempc, humidity, hour0, hour1, hour2, hour3, hour4, hour5, hour6, hour7,
                        hour8, hour9, hour10, hour11, hour12, hour13, hour14, hour15, hour16,
                        hour17, hour18, hour19, hour20, hour21, hour22, hour23]
            print("dataset: success")

            input_func = tf.estimator.inputs.pandas_input_fn(x=x_train, y=y_train, batch_size=10, num_epochs=500, shuffle=False)
            model = tf.estimator.DNNRegressor(hidden_units=[6,6,6], feature_columns=fea_cols)
            model.train(input_fn=input_func, steps=10000)
            print("training")

            predict_input_func = tf.estimator.inputs.pandas_input_fn(x=x_test, batch_size=10, num_epochs=1, shuffle=False)
            pred_gen = model.predict(predict_input_func)
            predictions = list(pred_gen)
            print("predicting")

            final_preds = []
            for pred in predictions:
                final_preds.append(pred['predictions'])

            self.fc_data = final_preds[-24:]
            self.fc_time = self.data_set['datetime'][-24:]
            # print(self.fc_time[23])

            for i in range(len(self.fc_data)):

                # update load forecast to database
                try:
                    self.cur.execute("""
                        UPDATE forecast_set
                        SET datetime_load=%s, fc_load=%s
                        WHERE hours_id=%s""", (
                        self.fc_time[i], float(self.fc_data[i]), (i+1)))
                    self.con.commit()
                    print "update database: success"
                except Exception as er:
                    print "update data base error: {}".format(er)


    Agent.__name__ = 'LoadForecastAppAgent'
    return Agent(**kwargs)


def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    utils.default_main(LoadForecastAppAgent,
                       description='LoadForecastApp agent',
                       argv=argv)


if __name__ == '__main__':
    # Entry point for script
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass