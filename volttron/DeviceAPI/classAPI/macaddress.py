import re
from uuid import getnode


# to get physical address:
original_mac_address = getnode()
print("MAC Address: " + str(original_mac_address)) # this output is in raw format

#convert raw format into hex format
hex_mac_address = str(":".join(re.findall('..', '%012x' % original_mac_address)))
print("HEX MAC Address: " + hex_mac_address)
mac = hex_mac_address.replace(':','')
print mac