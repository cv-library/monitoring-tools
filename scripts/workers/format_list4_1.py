import json
import re
import yaml


with open('list0.txt', 'r') as f:
    list1 = f.readlines()

def parse_list1(line):
    return line.strip()

for line in list1:
    service_name = parse_list1(line)
    print(f"{service_name}:")
    print("    Nagios: \"no\"")
    print("    comments: |")
    print("        - ")

