import json
import requests

deviceid = "8006E7877A3FE301BC47DEB0D4FBA67219E731A2"
cloudUserName = 'smarthome.pea@gmail.com'
cloudPassword = '28Sep1960'
response = requests.post(
    url="https://wap.tplinkcloud.com",
    headers={
        "Content-Type": "application/json",
    },
    data=json.dumps({
        "method": "login",
        "params": {
            "cloudUserName": cloudUserName,
            "appType": "Kasa_Android",
            "terminalUUID": "MY_UUID_v4",
            "cloudPassword": cloudPassword
        }
    })
)
print('Response HTTP Status Code: {status_code}'.format(
    status_code=response.status_code))
print('Response HTTP Response Body: {content}'.format(
    content=response.content))

find_token = json.loads(response.text)
token = (find_token['result']['token']).encode("utf-8")

print token
try:
    r0 = requests.post(
        url="https://wap.tplinkcloud.com/",
        params={
            "token": token,
        },
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "method": "getDeviceList"
        })
    )
    w = json.loads(r0.text)
    print w
    status = w['result']['deviceList'][0]['status']
    r = requests.post(
        url="https://wap.tplinkcloud.com/",
        params={
            "token": token,
        },
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "method": "passthrough",
            "params": {
                "requestData": "{\"emeter\":{\"get_realtime\":{}}}",
                "deviceId": deviceid
            }
        })
    )

    b = json.loads(r.text)
    c = b['result']['responseData']
    d = json.loads(c)
    current = d['emeter']['get_realtime']['current']
    volt = d['emeter']['get_realtime']['voltage']
    power = d['emeter']['get_realtime']['power']
    power0 = float(d['emeter']['get_realtime']['power'])  # /10000
    print status
except:
    print "newtoken"