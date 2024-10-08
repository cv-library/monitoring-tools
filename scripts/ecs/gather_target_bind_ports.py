import re

def parse_config(file_path):
    with open(file_path, 'r') as file:
        config_text = file.read()
  
#    blocks = config_text.strip().split("listen")  
    blocks = config_text.strip().split("listen")[1:]

    results = []
    for block in blocks:
        lines = block.strip().splitlines()
        #print(lines)
        listen_name = lines[0].strip()

        bind_port = None
        httpchk = None
        servers = []
        port_target = None

        for line in lines[1:]:
            line = line.strip()

            if line.startswith("bind"):
                bind_port = line.split(":")[1]

            elif line.startswith("option httpchk"):
                httpchk = line.split("httpchk", 1)[1].strip()

            elif line.startswith("server"):
                server_info = line.split()
                server_name = server_info[1]
                port_target = server_info[2].split(":")[1]
                servers.append(server_name)

        results.append({
            "listen": listen_name,
            "bind port": bind_port,
            "httpchk": httpchk,
            "servers": servers,
            "port_target": port_target
        })

    return results

file_path = 'web04.txt' 
parsed_data = parse_config(file_path)

for data in parsed_data:
    print(f"listen: {data['listen']}")
    print(f"bind port: {data['bind port']}")
    if data['httpchk']:
        print(f"httpchk: {data['httpchk']}")
    print(f"servers: {data['servers']}")
    print(f"port_target: {data['port_target']}")
    print("\n")

