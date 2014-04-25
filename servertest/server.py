import socket
#LAPTOP!!!!!!
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 9988
s.bind(('',port))
s.listen(1)

#while True:
conn, addr = s.accept()
data = conn.recv(1024)
conn.close()
print data
#break