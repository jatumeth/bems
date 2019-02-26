
import urllib3
import json


url = 'https://cplservice.com/apixmobile.php/cpletrix?filter=device_id,eq,250883398&order=trans_id,desc&page=1'
http = urllib3.PoolManager()
r = http.request('GET', url)


conve_json = json.loads(r.data)
print conve_json


value1 = (conve_json['cpletrix'])
print (" value1  = {}".format(value1))

value2 = (conve_json['cpletrix']['records'])
print (" value2  = {}".format(value2))


value3 = (conve_json['cpletrix']['records'][0])
print (" value3  = {}".format(value3))

value4 = (conve_json['cpletrix']['records'][0][9])
print (" value4  = {}".format(value4))
# #
# print (" activepower  = {}".format(activepower))
#
# print (" all power meter value = {}".format(conve_json))



# print conve_json

