
import socket

TCP_IP = '192.168.1.32'
TCP_PORT = 6000
BUFFER_SIZE = 1024
MESSAGE = "REQ200010010A"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()
print "received data:", data