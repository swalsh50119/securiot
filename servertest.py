import subprocess

def read_server(file_name="info.txt"):
	subprocess.call("./to_receive " + file_name, shell=True)
	fil = open(file_name,"r")
	message = fil.readline()
	return message

def write_server(file_name="info.txt",message=""):
	if file_name == "info.txt":
		fil = open(file_name,"w")
		fil.write(message)
		fil.close()
	subprocess.call("./to_send " + file_name, shell=True)

write_server(message="THIS IS SEAN HELLO")
message = read_server()
print message
write_server("after.h264")

