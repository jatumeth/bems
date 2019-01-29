# Install the Python Requests library:
# `pip install requests`

import requests

response = requests.put(
    url="http://peahivebackend3-peahivebackendmobiledev.azurewebsites.net/api/v2.0/devices/",
    headers={
        # "Cookie": "ARRAffinity=07a82a476c1a9d46f79b4aa1046b1065697bf1a5504cf6eb563339d7fc73fda5",
        "Authorization": "Token 5aecc823567f49f3b0a2f2d8e25e439ce5fd4682",
        # "Content-Type": "multipart/form-data; charset=utf-8; boundary=__X_PAW_BOUNDARY__",
    },
    files={
        "status": "ON",
        "device_name": "MY HUE",
        "color": "(25,30,40)",
        "device_id": "02HUE1234560",
        "brightness": "100",
        "room_id": "8",
        "network_status": "ONLINE",
        "device_type": "lightinglogging",
    },
)

print('Response HTTP Status Code: {status_code}'.format(
    status_code=response.status_code))
print('Response HTTP Response Body: {content}'.format(
    content=response.content))


