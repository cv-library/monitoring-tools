import json
import re
import yaml


list7_formated={}

with open('list7.txt', 'r') as f:
    list7 = f.read()



def format_list7(list7_dict):    
    for key, value in list7_dict.items():
        list7_formated[key]=value
    return list7_formated

list7_dict = yaml.safe_load(list7)

formated_list7=format_list7(list7_dict)


for key, value in formated_list7.items():
    print(f"{key}:")
    if re.match(r"(?i)yes", value['Nagios']):
        print("    Nagios: \"YES\"")
        print("    nagios_comments: |")
        for line in value['nagios_comments'].splitlines():
            print(f"           {line.strip()}")
    if re.match(r"(?i)yes", value['Dashboard']):
        print("    Dashboards: YES")
        print("    dashboard_comments: |")
        for line in value['dashboard_comments'].splitlines():
            print(f"           {line.strip()}")
