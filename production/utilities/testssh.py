import os,sys,time

import paramiko


# print(os.path(os.curdir))
slcServerIP = '192.168.1.122'
user = 'bret'
keyFile = 'C:\\Users\\Bret\\.ssh\\id_ed25519'
k = paramiko.Ed25519Key.from_private_key_file(keyFile)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=slcServerIP, username=user, pkey=k)
ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('ls')
stdout = ssh_stdout.readlines()
stderr = ssh_stderr.readlines()
for line in stdout:
    print(line)

print('Errors')
for line in stderr:
    print(line)
# if output != "":
#     print (output)
#     output
# else:
#     print
#     "There was no output for this command"
# # print(ssh_stdin, ssh_stdout, ssh_stderr)
