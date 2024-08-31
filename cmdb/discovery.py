import os
import yaml
import subprocess
import socket

def get_container_pid(container_id):
    try:
        pid = subprocess.check_output(['docker', 'inspect', '--format', '{{.State.Pid}}', container_id])
        return pid.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting PID for container {container_id}: {e}")
        return None

def get_established_connections(pid):
    connections = set()  # Use a set to store unique IP addresses
    
    # Use docker exec to run the netstat command within the container
    try:
#        pid = subprocess.check_output(['docker', 'inspect', '--format', '{{.State.Pid}}', container_id])
#        pid = pid.decode('utf-8').strip()
        nsenter_command = ['nsenter', '--target', pid, '--net', 'netstat', '-tun']
        output = subprocess.check_output(nsenter_command).decode('utf-8')
#        output = subprocess.check_output(
#            ['docker', 'exec', container_id, 'netstat', '-tun'],
#            text=True
#        )
        
        # Process the output, skipping the headers
        for line in output.splitlines()[2:]:  # Skip headers
            parts = line.split()
            if parts[5] == 'ESTABLISHED':  # Check if the connection is established
                ip_address = parts[4].split(':')[0]  # Extract IP address (ignore port)
                connections.add(ip_address)
                
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving connections for container {container_id}: {e}")
    
    return list(connections)  # Convert set to list before returning

def gather_container_connections():
    container_connections = []
    
    # Get a list of running containers
    container_ids = subprocess.check_output(['docker', 'ps', '-q']).decode('utf-8').strip().split('\n')
    
    for container_id in container_ids:
        pid=get_container_pid(container_id)
        connections = get_established_connections(pid)
        container_info = {
            "container_id": container_id,
            "connections": connections,
            "pid": pid
            
        }
        container_connections.append(container_info)
    
    return container_connections


def get_hostname():
    return socket.gethostname()

def get_os_info():
    return subprocess.getoutput("lsb_release -d|sed 's/Description:	//g' ")

def get_network_info():
    return subprocess.getoutput("ip -j addr show")

def get_services():
    return subprocess.getoutput("systemctl list-units --type=service --state=running --no-pager")

def get_docker_containers():
    return subprocess.getoutput("docker ps|awk '{print $1}'|grep -v CONTAINER|xargs -I ARGS docker inspect --format '{{json .}}' ARGS")
#    return subprocess.getoutput("docker ps --format '{{json .}}'")

def get_filesystems():
    return subprocess.getoutput("df -h --output=source,fstype,size,used,avail,pcent,target -x tmpfs -x devtmpfs")


def gather_system_info():
    system_info = {
        "hostname": get_hostname(),
        "os_info": get_os_info(),
        "network_info": yaml.safe_load(get_network_info()),
        "services": get_services().splitlines(),
        "docker_containers": [yaml.safe_load(line) for line in get_docker_containers().splitlines()],
        "filesystems": get_filesystems().splitlines()[1:],  # Skip header
        "docker_connections": gather_container_connections()
    }
    return system_info

def save_to_yaml(data, filename):
    with open(filename, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False)

if __name__ == "__main__":
    data = gather_system_info()
    yaml_filename = f"{data['hostname']}_cmdb.yaml"
    save_to_yaml(data, yaml_filename)
    print(f"System information saved to {yaml_filename}")