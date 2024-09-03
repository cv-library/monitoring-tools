import re

def parse_config(file_path):
    with open(file_path, 'r') as file:
        config_text = file.read()

    # Split the text by "listen" to get individual blocks
    blocks = config_text.strip().split("listen")[1:]  # Skip the first split as it would be empty

    results = []
    for block in blocks:
        lines = block.strip().splitlines()
        listen_name = lines[0].strip()

        bind_port = ""
        httpchk = ""
        servers = []
        port_target = ""

        for line in lines[1:]:
            line = line.strip()

            # Extract bind port
            if line.startswith("bind"):
                bind_port = line.split(":")[1]

            # Extract httpchk
            elif line.startswith("option httpchk"):
                httpchk = line.split("httpchk", 1)[1].strip()

            # Extract server information
            elif line.startswith("server"):
                server_info = line.split()
                server_name = server_info[1]
                port_target = server_info[2].split(":")[1]
                servers.append(server_name)

        # Append the parsed data to results
        results.append({
            "listen": listen_name,
            "bind_port": bind_port,
            "httpchk": httpchk,
            "target_servers": servers,
            "target_port": port_target
        })

    return results