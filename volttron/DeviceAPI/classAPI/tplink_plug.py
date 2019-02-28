import time
import json
import socket
from struct import pack

def encrypt(string):
    key = 171
    result = pack('>I', len(string))
    for i in string:
        a = key ^ ord(i)
        key = a
        result += chr(a)
    return result

def decrypt(string):
    key = 171
    result = ""
    for i in string:
        a = key ^ ord(i)
        key = ord(i)
        result += chr(a)
    return result

ip = '192.168.1.104'
port = 9999
#r = '{"system":{"get_sysinfo":{}}}'
r = '{"emeter":{"get_realtime":{}}}'
sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tcp.connect((ip, port))
sock_tcp.send(encrypt(r))
da = sock_tcp.recv(2048)
sock_tcp.close()

conve_json = json.loads(decrypt(da[4:]))

print(conve_json)

value1 = (conve_json['emeter'])
print (" value1  = {}".format(value1))

value2 = (conve_json['emeter']['get_realtime'])
print (" value2  = {}".format(value2))

value3 = (conve_json['emeter']['get_realtime']['current'])
print (" value3  = {}".format(value3))

value4 = (conve_json['emeter']['get_realtime']['power'])
print (" value4  = {}".format(value4))