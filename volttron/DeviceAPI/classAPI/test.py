# -*- coding: utf-8 -*-
from __future__ import absolute_import

from exponent_server_sdk import DeviceNotRegisteredError
from exponent_server_sdk import PushClient
from exponent_server_sdk import PushMessage
from exponent_server_sdk import PushResponseError
from exponent_server_sdk import PushServerError
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError


for i in range(1,1000,1):
    print i
    text = str('CO2 over '+str(i))
    response = PushClient().publish(
        PushMessage(to='ExponentPushToken[91i8j-MX3a2QeJm-vNP2Ax]',
                    body=text,
                    data=None))
