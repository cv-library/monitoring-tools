import json
import re
import yaml


with open('list1.txt', 'r') as f:
    list1 = f.readlines()

def parse_list1(line):
    service, ports = line.split(maxsplit=1)
    ports_dict = json.loads(ports)
    return service.strip(), ports_dict

for line in list1:
    service_name, service_ports = parse_list1(line)
    print(f"{service_name}:")
    print("    Nagios: \"no\"")
    print("    comments: |")
    print("        - ")

