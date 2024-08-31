import sqlite3
import yaml
import glob

def create_db_schema(conn):
    cursor = conn.cursor()
    
    # Servers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hostname TEXT NOT NULL,
        os_info TEXT
    )
    ''')
    
    # Network Interfaces table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS NetworkInterfaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        interface TEXT,
        ip_addresses TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')
    
    # Services table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        service TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')

    # Docker Containers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DockerContainers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        container_id TEXT,
        image TEXT,
        name TEXT,
        ip TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ActiveConnections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        endpoint TEXT,
        process TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')

    # Filesystems table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Filesystems (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        source TEXT,
        fstype TEXT,
        size TEXT,
        used TEXT,
        avail TEXT,
        pcent TEXT,
        target TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')
    # Docker Connections
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DockerConnections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_name TEXT,
        container_id TEXT,
        pid TEXT,
        connections TEXT,
        FOREIGN KEY (container_id) REFERENCES DockerContainers(container_id)
    )
    ''')

    # Docker Services
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DockerServices (
        server_name TEXT,
        container_id TEXT,
        container_port TEXT,
        host_port TEXT,
        proto TEXT,
        FOREIGN KEY (container_id) REFERENCES DockerContainers(container_id)
    )
    ''')

    # Host Connections
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS HostConnections (
        server_id INTEGER,
        pid TEXT,
        ip_address TEXT,
        host_port TEXT,
        proto TEXT,
        FOREIGN KEY (server_id) REFERENCES Servers(id)
    )
    ''')

    conn.commit()

def format_ip_info(addr_info):
    ip_entries = []
    for entry in addr_info:
        if 'local' in entry and 'prefixlen' in entry:
            ip_address = entry['local']
            prefix_len = entry['prefixlen']
            ip_entries.append(f"{ip_address}/{prefix_len}")    
    return ", ".join(ip_entries)

def get_docker_ip(container_info):
    ip_entries = []
    networks = container_info['NetworkSettings']['Networks']
    for network_name, network in networks.items():
        ip_address = network.get('IPAddress')
        if ip_address:
            ip_entries.append(ip_address)
    return ", ".join(ip_entries)



def server_exists(cursor, hostname):
    # Query to check if the server with the given hostname already exists
    cursor.execute('''
    SELECT COUNT(*) FROM Servers WHERE hostname = ?
    ''', (hostname,))
    return cursor.fetchone()[0] > 0

def insert_data(conn, yaml_file):
    cursor = conn.cursor()

    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    # Insert into Servers table
    if server_exists(cursor, data['hostname']):
        print(f"Server with hostname '{data['hostname']}' already exists. Skipping insertion.")
        #return    
    cursor.execute('''
    INSERT INTO Servers (hostname, os_info)
    VALUES (?, ?)
    ''', (data['hostname'], data['os_info']))
    server_id = cursor.lastrowid

# Insert docker connections
    for docker_conn in data['docker_connections']:
        ip_entries = []
        for connection in docker_conn['connections']:
            ip_entries.append(f"{connection}")
            ip_connections = ", ".join(ip_entries)
        cursor.execute('''
        INSERT INTO DockerConnections (server_name, container_id, pid, connections)
        VALUES (?, ?, ?, ?)
        ''', (data['hostname'], docker_conn['container_id'],  docker_conn['pid'],  ip_connections ))

# Insert docker services
    for docker_svc in data['docker_containers']:
        svc_port_bindings = []
        container_id = docker_svc['Config']['Hostname']
        portbindings = docker_svc['HostConfig']['PortBindings']
        for ct_port, hst_pt in portbindings.items():
            container_port, proto = ct_port.split('/')
            host_port = hst_pt[0] #.get('HostPort')
            print(host_port)
            cursor.execute('''
            INSERT INTO DockerServices (server_name, container_id, container_port, host_port, proto)
            VALUES (?, ?, ?, ?, ?)
            ''', (data['hostname'], container_id,  container_port,  host_port['HostPort'], proto ))


# Insert Host Connections
    host_conn = data['host_connections']
    for pid_key, conn_values in host_conn.items():
        print(pid_key)
        print(conn_values['ip'])
        cursor.execute('''
        INSERT INTO HostConnections (server_id, pid, ip_address, host_port, proto)
        VALUES (?, ?, ?, ?, ?)
        ''', (server_id, pid_key, conn_values['ip'], conn_values['port'], conn_values['protocol'] ))


    # Insert into NetworkInterfaces table
    for iface in data['network_info']:
#        for ifopts in iface['addr_info']:
#            if "label" in ifopts and "local" in ifopts :
#                print(ifopts)
#                addr_info_str = format_ip_info(ifopts)
#                cursor.execute('''
#                INSERT INTO NetworkInterfaces (server_id, interface, ip_addresses)
#                VALUES (?, ?, ?)
#                ''', (server_id, iface['ifname'], str(iface['addr_info'])))
        addr_info_str = format_ip_info(iface['addr_info'])
        cursor.execute('''
        INSERT INTO NetworkInterfaces (server_id, interface, ip_addresses)
        VALUES (?, ?, ?)
        ''', (server_id, iface['ifname'], str(addr_info_str)))    
    # Insert into Services table
    for service in data['services']:
        cursor.execute('''
        INSERT INTO Services (server_id, service)
        VALUES (?, ?)
        ''', (server_id, service))
    
    # Insert into DockerContainers table
    for container in data['docker_containers']:
        docker_ip = get_docker_ip(container)
        container_name = container['Name'] if container['Name'] else "null"
        container_id = container['Config']['Hostname']
        container_image = container['Config']['Image']

        cursor.execute('''
        INSERT INTO DockerContainers (server_id, container_id, image, name, ip)
        VALUES (?, ?, ?, ?, ?)
        ''', (server_id, container_id, container_image, container_name, docker_ip))


    # Insert into Filesystems table
    for fs in data['filesystems']:
        fields = fs.split()
        cursor.execute('''
        INSERT INTO Filesystems (server_id, source, fstype, size, used, avail, pcent, target)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (server_id, *fields))
    
    conn.commit()

if __name__ == "__main__":
    db_conn = sqlite3.connect('cmdb.db')
    create_db_schema(db_conn)

    # Assuming all YAML files are in the current directory
    yaml_files = glob.glob("*.yaml")
    for yaml_file in yaml_files:
        insert_data(db_conn, yaml_file)
        print(f"Imported data from {yaml_file} into the database")

    db_conn.close()
    print("All data imported successfully.")
