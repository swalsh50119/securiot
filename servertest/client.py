import socket
# RASPBERRY PI RUNS THIS
# 140.247.148.132 PI ADDR
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '140.247.148.132' #Need IP of the laptop
port = 9988
s.connect((host, port))
s.sendall('PLZ PRINT THIS, I WILL BE V HAPPY')
s.close()