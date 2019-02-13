import time

from pymodbus.client.sync import ModbusTcpClient
# from pymodbus.constants.Defaults import ModbusTcpClient
from pymodbus.constants import Defaults
Defaults.Parity='E'
Defaults.Baudrate = 9600
client = ModbusTcpClient('192.168.1.116', port=502)
client.connect()
print(client.connect())
# print ModbusTcpClient.port
# request = client.read_holding_registers(0, 8, unit=1,parity= 'E',stopbits=1,bytesize=8,baudrate=9600)
# request = client.read_holding_registers(2000, 32, unit=1)
startregis = 2000


#register 1 step 1 read data sheet
#register 1 step 2 convert HEX to Deciman
# input1 == # open (1)/close (0)
# input1 == # 5761 / 5 = speed H  / 7= swing / 6=fix / 1 = 0n
firsthex= '5661' #input in HEX  Fan speed high =5061  Fan speed low =1061
firtdec = int(firsthex, 16)
print firtdec
result= client.write_register(startregis, firtdec, unit= 1) # open /close



# input2 == # 0200== FAN , 0202 = cool, 0207 = Dry
# secondhex= '0000' #input in HEX
# seconddec = int(secondhex, 16)
# print('second in dec: {}'.format(seconddec))
# result= client.write_register((startregis+1), 0000, unit= 1) # mode  2 == cooling  7 == dry mode 0207  #512==FAN  #514 == Cool  #519=Dry



# input3 in temp*10 , ex temp = 22 , input = 220
# result= client.write_register(startregis+2, 240, unit= 1) # temp 25 == 250

# time.sleep(5)
# #
# #
# print "send __________________"
# result= client.read_holding_registers(startregis, 3, unit= 1)
# print(result.registers)
# print(" temp= {}".format(result.registers[2]/10))
# regis0 = hex(result.registers[0])
# print regis0
#
#
# print "reading input register __________________"
# result1= client.read_input_registers(startregis, 6, unit= 1)
# print result1.registers
#
#
# print hex(result1.registers[1])
# if str((regis0)) == '0':
#     print (" status= {}".format('off'))
# elif str((regis0)) == '1':
#     print (" status= {}".format('on'))
# #
# r00 = (str((regis0))[-4])
# r01 = str(((regis0))[-3])
# r02 = str(((regis0))[-2])
# r03 = str(((regis0))[-1])
#
# if r00 == '0':
#     print(" status= {}".format('on'))
# elif r00 == '1':
#     print (" status= {}".format('off'))
#
#
# if r02 == '7':
#     print(" fan= {}".format('swing'))
# elif r02 == '6':
#     print (" fan= {}".format('no swing'))
#
#
# if r03 == '5':
#     print(" fan= {}".format('High'))
# elif r03 == '3':
#     print (" fan= {}".format('Medium'))
# elif r03 == '2':
#     print (" fan= {}".format('Low'))


# result= client.read_input_registers(2008, 32, unit= 1) #address 31002 6 address per 1 unit
# print('result: {}'.format(result))
# print(result.registers)
# print(len(result.registers))

#Closes the underlying socket connection
client.close()