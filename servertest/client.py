import socket
# RASPBERRY PI RUNS THIS
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 0 #Need IP of the laptop
port = 9988
s.connect((host, port))
s.sendall('PLZ PRINT THIS, I WILL BE V HAPPY')
s.close()