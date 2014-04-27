import subprocess
import time

def read_server(file_name="info.txt"):
	subprocess.call("./to_receive " + file_name, shell=True)
	#fil = open(file_name,"r")
	#message = fil.readline()
	#return message

def write_server(file_name="info.txt",message=""):
	if file_name == "info.txt":
		fil = open(file_name,"w")
		fil
		fil.write(message)
		fil.close()
	subprocess.call("./to_send " + file_name, shell=True)

#write_server(message="cameraon")
#time.sleep(15)
write_server(message="cameraoff")
#write_server(message="target(200,200,400,400)")
#time.sleep(20)
#write_server(message="requestsnapshot")
#read_server(file_name="snapshot.jpg")
#read_server(file_name="before.h264")
#read_server(file_name="after.h264")