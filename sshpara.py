import paramiko
ssh = paramiko.SSHClient()
yoloswag=True
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('1.1.1.2', port=22, username = 'ipschool',password='python')
stdin, stdout, stderr = ssh.exec_command('ls')
while(yoloswag):
	output = stdout.readlines()
	type(output) #will printout list
	print '\n'.join(output)
	if(output[0] != "Turtlebot is searching..."):
		yoloswag=False
print "this is the real thing we want"
print output
#use the os command to execute python go_to_v1.py +" output"
