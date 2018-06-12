from azure.servicebus import ServiceBusService
from azure.servicebus import Message


sbs = ServiceBusService(
    service_namespace='peahiveservicebusv2',
    shared_access_key_name='RootManageSharedAccessKey',
    shared_access_key_value='F6hM22kIHgfzKmt2GF0NtGlrVZtapYHOG3gMb7doaM4=')


msg = Message('Hello World777777')
sbs.send_topic_message('hivecdf12345', msg)
print "nnn"