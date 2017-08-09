from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
import time

'''
The following code creates a ServiceBusService object.
 Replace mynamespace, sharedaccesskeyname, and sharedaccesskey
 with your namespace, shared access signature (SAS) key name, and value.
 The values for the SAS key name and value can be found in the Azure portal
connection information, or in the Visual Studio Properties pane
when selecting the Service Bus namespace in Server Explorer
(as shown in the previous section).
'''
# service_namespace='homespace',


sbs = ServiceBusService(
    service_namespace='hiveservicebus',
    shared_access_key_name='RootManageSharedAccessKey',
    shared_access_key_value='vZmK7ee4YhIbaUEW5e/sgT0S8JV09LnToCOEqIU+7Qw=')

'''
create_queue also supports additional options,
which enable you to override default queue settings such as message time
to live (TTL) or maximum queue size. The following example sets t
he maximum queue size to 5 GB, and the TTL value to 1 minute
'''

def pubazure(topic,rawmsg):
    print ("start public")
    sbs.create_topic(topic)

    for x in range(2):
        print("message sented!!!")
        msg = Message(rawmsg)
        sbs.send_topic_message(topic, msg)
        print(msg.body)
        time.sleep(1)

if __name__ == '__main__':
    # print ("\nPython %s" % sys.version)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01','{"status": "OFF", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)
    pubazure('tp01', '{"status": "ON", "brightness": "99", "color": [1, 50, 100]}')
    time.sleep(3)