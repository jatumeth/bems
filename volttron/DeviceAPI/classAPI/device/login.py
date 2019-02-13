# Install the Python Requests library:
# `pip install requests`

import requests
import json



response = requests.post(
    url="https://peahivemobilebackends.azurewebsites.net/api/v2.0/login",
    headers={
        "Cookie": "ARRAffinity=7a61890acf45375324c89f5a36c34fdce248b2320085ab76f0044c87619baa49",
        "Content-Type": "application/json; charset=utf-8",
    },
    data=json.dumps({
        "noti_token": "ExponentPushToken[t9ufzPGg-D_0Qx0Xgh-44-]",
        "username": "hive5",
        "password": "28Sep1960"
    })
)
print('Response HTTP Status Code: {status_code}'.format(
    status_code=response.status_code))
print('Response HTTP Response Body: {content}'.format(
    content=response.content))



