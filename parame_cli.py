import sys
import os
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
d = sys.argv[1] + ' ' + os.getcwd() + ' ' + ' '.join(sys.argv[2:])
print(d)
s.sendto(d.encode(), ('127.0.0.1', 1337))
s.settimeout(2)

try:
    ret = s.recv(1024)
    print(ret.decode())
except socket.timeout:
    print('no response!')