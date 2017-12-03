import psycopg2
try:
    conn = psycopg2.connect(host="peahivedev.postgres.database.azure.com", port="5432",
                            user="peahive@peahivedev", password="28Sep1960",
                            dbname="postgres")
except:
    print "I am unable to connect to the database."


cur = conn.cursor()
# cur.execute("SELECT * from device_info where device_id=%s", ("2HUE0017881cab4kib",))
# if bool(cur.rowcount):
#     print "yes"
# else:
#     print "no"
#
# cur = conn.cursor()  # open a cursor to perform database operations
#
# print "{} >> Done 1: connect to database name {}".format(agent_id, db_database)



cur.execute("INSERT INTO inverter "
            "(inverter_id, grid_voltage) "
            "VALUES ('1PV221445K1200138','221')")

conn.commit()


# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('ACD1200138','AC','Daikin','AC','1DAIK','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('3WIS221445K1200321','plugload','belkinwemo','step dim  ballast','2WL','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','step dim  ballas','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('1FN221445K1200138','relaysw','hatari','relaysw','2WL','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','hatario','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('2SDB0001','step dim  ballast','step dim  ballast','step dim  ballast','2SDB','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','step dim  ballas','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('2WSL0001','wattstopper','wattstopper','wattstopper_modelA','2WSL','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','wattstopper_A','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('3MOD0001','smartplug','smartplug','smartplug_modelA','3MOD','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','smartplug_A','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('3WP0001','wattstopper plugload','wattstopper plugload','wattstopper plugload_modelA','3WP','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','wattstopper plugload_A','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('1PV221445K1200138','PV_Inverter','MUST','PV3000','4INV','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','MUST','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('Smappee001','PowerMeter','Smappee','3phasersolar','5SMP','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','smappee','APR')")
#
# conn.commit()
#
# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('6SAM0001','SmartCamera','Samsung','indoor','6SAM','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','samsung','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('1MS221445K1200132','multisensor','Fibaro','indoor','8FIB','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','fibaro','APR')")
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('9REF01','refrigurator','Mitsubishi','indoor','9REF','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','mitsubishi','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('10SONOS01','speaker','sonos','indoor','10SON','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','sonos','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('1LG221445K1200137','TV','LG','indoor','11LGT','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','LG','APR')")
#
# conn.commit()
#
# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('Netatmo002','netatmo','netatmo','indoor','12NET','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','Netatmo','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('13ECH01','speaker','Amazon Echo','indoor','13ECH','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','Alexa','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('14HGW01','gateway','Dell','indoor','14HGW','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','Dell','APR')")
#
# conn.commit()
#
# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('15FIT01','fitbit','fitbit','fitbit','15FIT','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','fitbit','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info "
#             "(device_id, device_type, vendor_name, device_model, device_model_id, mac_address,min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) "
#             "VALUES ('16SCH001','EV','Schider','EV','16SCH','0a4f437e63c1',100,0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','Schider','APR')")
#
# conn.commit()

# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('2HUE001','lighting','Philips','Philips Hue','2HUE','0a4f437e63c2',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','hue001','APR')")
#
# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('1DAIK001','airconditioner','Daikin','Daikin Inverter','1DAIK','0a4f437e63c1',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin001','APR')")
#
# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('1DAIK001','airconditioner','Daikin','Daikin Inverter','1DAIK','0a4f437e63c1',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin001','APR')")
#
# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('1DAIK001','airconditioner','Daikin','Daikin Inverter','1DAIK','0a4f437e63c1',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin001','APR')")
#
# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('1DAIK001','airconditioner','Daikin','Daikin Inverter','1DAIK','0a4f437e63c1',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin001','APR')")
#
# cur.execute("INSERT INTO device_info (device_id, device_type, vendor_name, device_model, device_model_id, mac_address, \
#
#                           min_range, max_range, identifiable, communication, date_added, factory_id, approval_status) \
#
#                           VALUES ('1DAIK001','airconditioner','Daikin','Daikin Inverter','1DAIK','0a4f437e63c1',100,\
#
#                           0,True,'WiFi','2017-08-12 21:45:58.208000 +07:00','daikin001','APR')")

