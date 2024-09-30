import yaml

# Function to generate Confluence table from YAML data
def generate_confluence_table(data):
    confluence_output = ""

    # Iterate through each key in the data
    for service, details in data.items():
        if details is None:
            continue  # Skip if no details are provided for the service

        confluence_output += f"### **{service}**\n\n"
        confluence_output += "| **Category** | **Status** | **Comments** |\n"
        confluence_output += "|--------------|------------|--------------|\n"

        # Process Nagios, Logs, SQS and other details
        nagios_status = "✔ YES" if str(details.get('Nagios')) == 'YES' else "❌ NO"
        logs_status = "✔ YES" if str(details.get('Logs')) == 'YES' else "❌ NO"
        
        # Extract comments
        nagios_comments = details.get('nagios_comments', '').replace('\n', '\n|||')
        logs_comments = details.get('log_comments', '').replace('\n', '\n')

        # Add rows for Nagios, Logs, and SQS
        confluence_output += f"| **Nagios** | {nagios_status} | {nagios_comments} |\n"
        confluence_output += f"| **Logs** | {logs_status} | {logs_comments} |\n"

        # Handle Dashboards and Metrics
        #confluence_output += f"| **Dashboards** | ✔ {details.get('Dashboards', '')} | |\n"

        # Handle HAProxy details
        if 'haproxy' in details:
            haproxy = details['haproxy']
            listen = haproxy.get('listen', '')
            bind_port = haproxy.get('bind_port', '')
            httpchk = haproxy.get('httpchk', 'None')
            servers = ', '.join(haproxy.get('servers', []))
            port_target = haproxy.get('port_target', '')
            haproxy_details = (        
                f"**Bind Port**: {bind_port}, "
                f"**Httpchk**: {httpchk}, "
                f"**Servers**: **<<** {servers} **>>** and "
                f"**Port Target**: {port_target}"
            )
            confluence_output += f"| **HAProxy** | ✔ YES | {haproxy_details} |\n"

        # Handle HostServers
        confluence_output += f"| **HostServers** | ✔ {details.get('HostServers', 'No apply')} | |\n"

        # Handle host_port
        confluence_output += f"| **host_port** | ✔ {details.get('host_port', 'No apply')} | |\n"

        confluence_output += "\n"

    return confluence_output

# Main function to read YAML file and convert to Confluence format
def yaml_to_confluence(input_file):
    # Read the YAML file
    with open(input_file, 'r') as file:
        data = yaml.safe_load(file)

    # Generate Confluence table
    confluence_output = generate_confluence_table(data)

    return confluence_output

# Replace 'input.yaml' with your YAML file path
input_file = 'input.yaml'

# Convert the YAML to Confluence format and print the result
confluence_output = yaml_to_confluence(input_file)
print(confluence_output)