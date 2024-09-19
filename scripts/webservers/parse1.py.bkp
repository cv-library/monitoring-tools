import json
import re
import yaml


list3_formated={}
list4_formated={}
list5_formated={}
list7_formated={}

with open('list1.txt', 'r') as f:
    list1 = f.readlines()

with open('list2.txt', 'r') as f:
    list2 = f.read()

with open('list3.txt', 'r') as f:
    list3 = f.read()

with open('list4.txt', 'r') as f:
    list4 = f.read()

with open('list5.txt', 'r') as f:
    list5 = f.read()

with open('list7.txt', 'r') as f:
    list7 = f.read()


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


def format_list3(list3_dict):
    
    for key, value in list3_dict.items():
        sqs_list = []
        for i in value['SQS']:
            parts = i.split(':')
            desired_value = parts[-1]
            sqs_list.append(desired_value)
            list3_formated[key]=sqs_list
    return list3_formated


def format_list4(list4_dict):    
    for key, value in list4_dict.items():
        list4_formated[key]=value
    return list4_formated

def format_list5(list5_dict):    
    for key, value in list5_dict.items():
        list5_formated[key]=value
    return list5_formated

def format_list7(list7_dict):    
    for key, value in list7_dict.items():
        list7_formated[key]=value
    return list7_formated

list2_blocks = list2.split('\n\n')  # Assuming each block is separated by double newlines, please use the script to generate list2 <><><>
list2_details = [parse_list2(block) for block in list2_blocks]
list3_dict = yaml.safe_load(list3)
list4_dict = yaml.safe_load(list4)
list5_dict = yaml.safe_load(list5)
list7_dict = yaml.safe_load(list7)

formated_list3=format_list3(list3_dict)
formated_list4=format_list4(list4_dict)
formated_list5=format_list5(list5_dict)
formated_list7=format_list7(list7_dict)



for line in list1:
    service_name, service_ports = parse_list1(line)
    print(f"{service_name}:")
    for key, value in formated_list4.items():
        if key == service_name:
            if re.match(r"(?i)yes", value['Nagios']):
                nagios_yes = True
                print("    Nagios: YES")
                print("        comments: |")
                for line in value['comments'].splitlines():
                    print(f"           {line.strip()}")
            else:
                print("    Nagios: NO")
    for key, value in formated_list5.items():
        if key == service_name:
            if re.match(r"(?i)yes", value['Logs']):
                
                print("    Logs: YES")
                print("        comments: |")
                for line in value['comments'].splitlines():
                    print(f"           {line.strip()}")
            else:
                print("    Logs: NO")
            
    print("    Dashboards: []")
    print("    Metrics: []")
               

    if service_name in formated_list3:
        print(f"    SQS: \"{formated_list3[service_name]}\"")
    else:
        print(f"    SQS: NO")
    for port, details in service_ports.items():
        host_port = details[0]['HostPort']
        for listen, bind_port, httpchk, servers, port_target in list2_details:
            if host_port == port_target:
                print("    haproxy:")
                print(f"        listen: \"{listen}\"")
                print(f"        bind_port: \"{bind_port}\"")
                print(f"        httpchk: \"{httpchk}\"")
                print(f"        servers: {servers}")
                print(f"        port_target: \"{port_target}\"")
    print(f"    host_port: \"{host_port}\"\n\n\n")


for key, value in formated_list7.items():
    print(f"{key}:")
    if re.match(r"(?i)yes", value['Nagios']):
        print("    Nagios: YES")
        print("        comments: |")
        for line in value['nagios_comments'].splitlines():
            print(f"           {line.strip()}")
    if re.match(r"(?i)yes", value['Dashboard']):
        print("    Dashboards: YES")
        print("        comments: |")
        for line in value['dashboard_comments'].splitlines():
            print(f"           {line.strip()}")
