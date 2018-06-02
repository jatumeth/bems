import urllib2
import base64

body = 'https://graph-na02-useast1.api.smartthings.com/location/devices/6ce285b4-a2dd-4eea-8343-7a7449941130'
print body
_request = urllib2.Request(body)
# _request.add_header("Content-Type","application/json;charset=UTF-8")
# username = 'kwarodom@hotmail.com'
# password = 'w3300136'
base64string = base64.encodestring('%s:%s' % ('smarthomepea@gmail.com', '28Sep1960')).replace('\n', '')
_request.add_header("Authorization", "Basic 5f599c0a-190c-4235-9a65-fef4fce8eb39")
deviceInfoUrl = urllib2.urlopen(_request)  # when include data this become a POST command
x = deviceInfoUrl.read().decode("utf-8")


