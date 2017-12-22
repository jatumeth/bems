
from pymodbus.client.sync import ModbusTcpClient
# from pymodbus.constants.Defaults import ModbusTcpClient
from pymodbus.constants import Defaults
Defaults.Parity='E'
Defaults.Baudrate = 9600
client = ModbusTcpClient('192.168.1.4', port=502)
client.connect()
print(client.connect())
# print ModbusTcpClient.port
# request = client.read_holding_registers(0, 8, unit=1,parity= 'E',stopbits=1,bytesize=8,baudrate=9600)
# request = client.read_holding_registers(2000, 32, unit=1)
# result= client.read_holding_registers(2000, 32, unit= 1)


result= client.read_input_registers(1002, 32, unit= 1) #address 31002
print('result: {}'.format(result))
print(result.registers)
print(len(result.registers))

#Closes the underlying socket connection
client.close()