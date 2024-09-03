import json
import re

with open('list1.txt', 'r') as f:
    list1 = f.readlines()

with open('list2.txt', 'r') as f:
    list2 = f.read()

def parse_list1(line):
    service, ports = line.split(maxsplit=1)
    ports_dict = json.loads(ports)
    return service.strip(), ports_dict

def parse_list2(config_block):
    listen_match = re.search(r'listen: (.+)', config_block)
    bind_port_match = re.search(r'bind port: (\d+)', config_block)
    httpchk_match = re.search(r'httpchk: (.+)', config_block)
    servers_match = re.search(r'servers: (\[.+\])', config_block)
    port_target_match = re.search(r'port_target: (\d+)', config_block)

    listen = listen_match.group(1) if listen_match else None
    bind_port = bind_port_match.group(1) if bind_port_match else None
    httpchk = httpchk_match.group(1) if httpchk_match else None
    servers = eval(servers_match.group(1)) if servers_match else []
    port_target = port_target_match.group(1) if port_target_match else None
    
    return listen, bind_port, httpchk, servers, port_target

list2_blocks = list2.split('\n\n')  # Assuming each block is separated by double newlines, please use the script to generate list2
list2_details = [parse_list2(block) for block in list2_blocks]

for line in list1:
    service_name, service_ports = parse_list1(line)
    match_found = False
    
    for port, details in service_ports.items():
        host_port = details[0]['HostPort']
        
        for listen, bind_port, httpchk, servers, port_target in list2_details:
            if host_port == port_target:
                match_found = True
                print(f"{service_name}:")
                print("    Nagios: []")
                print("    Dashboards: []")
                print("    Metrics: []")
                print("    Logs: []")
                print("    haproxy:")
                print(f"        listen: \"{listen}\"")
                print(f"        bind_port: \"{bind_port}\"")
                print(f"        httpchk: \"{httpchk}\"")
                print(f"        servers: {servers}")
                print(f"        port_target: \"{port_target}\"")
                print(f"    host_port: \"{host_port}\"\n")
    
    if not match_found:
        print(f"{service_name}:")
        print("    Nagios: []")
        print("    Dashboards: []")
        print("    Metrics: []")
        print("    Logs: []")
        print("    haproxy:")
        print("        listen: \"\"")
        print("        bind_port: \"\"")
        print("        httpchk: \"\"")
        print("        servers: []")
        print("        port_target: \"\"")
        print(f"    host_port: \"{host_port}\"\n")
