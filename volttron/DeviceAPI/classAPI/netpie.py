import microgear.client as microgear
import time
import logging

appid = "RSDPEA"
gearkey = "5xeHHg4vpGAYTzj"
gearsecret =  "N2hc2XaAriu2grlvRO0kEEglE"

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
    logging.debug("Now I am connected with netpie")

def subscription(topic,message):
    logging.debug(topic+" "+message)
    print message

def disconnect():
	logging.debug("disconnect is work")

microgear.setalias("doraemon")
microgear.on_connect = connection
microgear.on_message = subscription
microgear.on_disconnect = disconnect
microgear.subscribe("/SMH/pushbutton")
x = microgear.subscribe("/SMH/pushbutton")
print "x:{}".format(x)
microgear.connect(False)

#
while True:
     #microgear.chat("doraemon","Hello world."+str(int(time.time())))
   # microgear.subscribe("/SMH/pushbutton")
    time.sleep(2)