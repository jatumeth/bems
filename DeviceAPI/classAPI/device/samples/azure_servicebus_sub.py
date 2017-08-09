from azure.servicebus import ServiceBusService, Message, Topic, Rule, DEFAULT_RULE_NAME
import time
import json

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

sbs.create_subscription('tp01', 'client1')


while True:
    print ""
    print("message received!!!")
    msg = sbs.receive_subscription_message('tp01', 'client1', peek_lock=False)
    print(msg.body)
    # print type(msg.body)
    loadmessage = json.loads(msg.body)
    # print loadmessage
    # print(" grid_activePower = {}".format(loadmessage['grid_activePower']))
    # print(" solar_activePower = {}".format(loadmessage['solar_activePower']))
    # print(" load_activePower = {}".format(loadmessage['load_activePower']))
    # print "-------------------------------------------------------------------"
    # print ""
    # print ""
    # time.sleep(2)
