import requests
import json
import time

while True:
    time.sleep(8)
    # print "------------------iothub-------------ON-------"
    # response = requests.post(
    #     url="https://peahivebackend.azurewebsites.net//api/v2.0/deviceControlIoTHub/",
    #     headers={
    #         "Cookie": "ARRAffinity=b9b60e53ee09dea570fc7fba49ab6b7106edaae66df0c503a6cadd7d7b7bcd1c",
    #         "Authorization": "Token f11a08be805ab763521124e89a1fb82e26d464d4",
    #         "Content-Type": "application/json; charset=utf-8",
    #     },
    #     data=json.dumps({
    #         "topic": "hivedevhub13",
    #         "message": {
    #             "status": "ON",
    #             "device": "02ORV0017886",
    #             "type": "devicecontrol"
    #         }
    #     })
    # )
    # print('Response HTTP Status Code: {status_code}'.format(
    #     status_code=response.status_code))
    # print('Response HTTP Response Body: {content}'.format(
    #     content=response.content))
    #
    # time.sleep(8)
    #
    # print "------------------iothub-------------OFF-------"
    # response = requests.post(
    #     url="https://peahivebackend.azurewebsites.net//api/v2.0/deviceControlIoTHub/",
    #     headers={
    #         "Cookie": "ARRAffinity=b9b60e53ee09dea570fc7fba49ab6b7106edaae66df0c503a6cadd7d7b7bcd1c",
    #         "Authorization": "Token f11a08be805ab763521124e89a1fb82e26d464d4",
    #         "Content-Type": "application/json; charset=utf-8",
    #     },
    #     data=json.dumps({
    #         "topic": "hivedevhub13",
    #         "message": {
    #             "status": "OFF",
    #             "device": "02ORV0017886",
    #             "type": "devicecontrol"
    #         }
    #     })
    # )
    # print('Response HTTP Status Code: {status_code}'.format(
    #     status_code=response.status_code))
    # print('Response HTTP Response Body: {content}'.format(
    #     content=response.content))



    print "------------------mqtt-------------ON-------"
    response = requests.post(
        url="https://peahivebackend.azurewebsites.net/api/v2.0/devicecontrol/",
        headers={
            "Cookie": "ARRAffinity=b9b60e53ee09dea570fc7fba49ab6b7106edaae66df0c503a6cadd7d7b7bcd1c",
            "Authorization": "Token f11a08be805ab763521124e89a1fb82e26d464d4",
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "topic": "hivedevhub13",
            "message": {
                "status": "ON",
                "device": "02ORV0017886",
                "type": "devicecontrol"
            }
        })
    )
    print('Response HTTP Status Code: {status_code}'.format(
        status_code=response.status_code))
    print('Response HTTP Response Body: {content}'.format(
        content=response.content))

    time.sleep(8)

    print "------------------mqtt-------------OFF-------"
    response = requests.post(
        url="https://peahivebackend.azurewebsites.net/api/v2.0/devicecontrol/",
        headers={
            "Cookie": "ARRAffinity=b9b60e53ee09dea570fc7fba49ab6b7106edaae66df0c503a6cadd7d7b7bcd1c",
            "Authorization": "Token f11a08be805ab763521124e89a1fb82e26d464d4",
            "Content-Type": "application/json; charset=utf-8",
        },
        data=json.dumps({
            "topic": "hivedevhub13",
            "message": {
                "status": "OFF",
                "device": "02ORV0017886",
                "type": "devicecontrol"
            }
        })
    )
    print('Response HTTP Status Code: {status_code}'.format(
        status_code=response.status_code))
    print('Response HTTP Response Body: {content}'.format(
        content=response.content))