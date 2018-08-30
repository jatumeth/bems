# newdeveloper is for the old version of Hue hub, might no longer be useful in future version.
import requests
import json
import time

url = 'http://192.168.1.121:80' + '/api/newdeveloper'
req = requests.get(url)
result = json.loads(req.content)
message = json.dumps(result)
message = message.encode(encoding='utf_8')

substring = "unauthorized user"
no_name = substring in message

if no_name:
    cnt = 60
    while cnt > 0:
        body = {"devicetype": "my_hue_app#bemoss"}
        url = 'http://192.168.1.121:80' + '/api'

        r = requests.post(url, json.dumps(body))
        print r.content
        substring = "link button not pressed"
        if substring in r.content:
            time.sleep(0.5)
            cnt -= 1
            print cnt
        else:
            exp = '\"username\":\"(.*?)\"'
            # pattern = re.compile(exp, re.S)
            # result = re.findall(pattern, r.content)
            hub_name = result[0]
            break
else:
    hub_name = 'newdeveloper'

print hub_name
