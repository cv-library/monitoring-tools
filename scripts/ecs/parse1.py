import json
import re
import yaml


list3_formated={}
list4_formated={}
list5_formated={}
list7_formated={}


with open('list0.txt', 'r') as f:
    list0 = f.read()

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




formated_list0=list0.split('\n')
list4_dict = yaml.safe_load(list4)
list5_dict = yaml.safe_load(list5)
list7_dict = yaml.safe_load(list7)
formated_list3="abobrinha" #format_list3(list3_dict)
formated_list4=format_list4(list4_dict)
formated_list5=format_list5(list5_dict)
formated_list7=format_list7(list7_dict)


######################list0
host_port=""
service_ports=""
for line in formated_list0:
    service_name=line
    print(f"{service_name}:")
    for key, value in formated_list4.items():
        if key == service_name:
            if re.match(r"(?i)yes", value['Monitoring']):
                nagios_yes = True
                print("    Monitoring: \"YES\"")
                print("    monitoring_comments: |")
                for line in value['comments'].splitlines():
                    print(f"           {line.strip()}")
            else:
                print("    Monitoring: \"NO\"")
    for key, value in formated_list5.items():
        if key == service_name:
            if re.match(r"(?i)yes", value['Logs']):
                
                print("    Logs: \"YES\"")
                print("    log_comments: |")
                for line in value['comments'].splitlines():
                    print(f"           {line.strip()}")
            else:
                print("    Logs: \"NO\"")
            
   
    print(f"    \n\n\n")

