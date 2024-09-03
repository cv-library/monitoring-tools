import sqlite3
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

def fetch_data_from_db(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Fetch Servers and their IDs
    cursor.execute("SELECT id, hostname FROM Servers")
    servers = cursor.fetchall()
    
    # Fetch Active Connections

    cursor.execute("SELECT server_id, ip_address FROM HostConnections")
    connections = cursor.fetchall()
    
    conn.close()
    return servers, connections

def create_graph(servers, connections):
    G = nx.DiGraph()

    # Add server nodes
    server_dict = {server_id: hostname for server_id, hostname in servers}
    for server_id, hostname in server_dict.items():
        G.add_node(hostname, type='server')

    # Add connection edges
    for server_id, ip_address  in connections:
        server_name = server_dict.get(server_id)
        G.add_node(ip_address, type='endpoint')  
        G.add_edge(server_name, ip_address, label=ip_address)

    return G

def display_graph(G):
    plt.figure(figsize=(12, 12))

    # Use graphviz_layout for tree-like structure
    pos = graphviz_layout(G, prog="dot")
    
    # Draw the network graph
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=3000, font_size=10, font_weight='bold', arrows=True)
    
    # Draw edge labels (process names)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

    plt.title("CMDB Service Dependency Graph")
    plt.show()

if __name__ == "__main__":
    db_file = 'cmdb.db'
    
    # Fetch data from the database
    servers, connections = fetch_data_from_db(db_file)
    
    # Create the graph
    G = create_graph(servers, connections)
    
    # Display the graph
    display_graph(G)
