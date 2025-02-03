import paramiko

def execute_remote_command(server_ip, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(server_ip, username=username, password=password)
    
    # Concatenate command, first activate conda environment, then run Python script.
    full_command = 'source ~/.bashrc && conda activate moon && ' + command
    
    stdin, stdout, stderr = ssh.exec_command(full_command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    ssh.close()
    
    return output, error

server_ip = 'xxxx'
username = 'xxx'
password = '258147963'
command = 'python ~/aaaPROJECTS/moondream/inference.py'

output, error = execute_remote_command(server_ip, username, password, command)
print("Output:", output)
print("Error:", error)


# 9d8de4b9c90141b3ac72e018f17617c1