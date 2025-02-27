# =========================================================
# Filename: s1<yzhou253>s2<ibae>Server.py
# Description: Server for our chat program
# Author: Harrison Zhou, Inha Bae
# Date Created: <2024-11-24>
# Last Modified: <Last Modified Date>
# Version: 1.0
# =========================================================
import socket
import argparse
import select
import sys


# =========================================================
# Pseudocode OUTDATED!
# =========================================================
# Parse input arguments: --port <Server port>: int
# If port argument is invalid:
#     Then, print to stdout error.
# Else:
#   Create a TCP socket and bind it to the specified port.
#   Start listening for incoming client connections.
#   Run indefinitely:
#       Accept new connections from clients.
#       For each new client:
#           Add client to the list of active connections.
#           Process client commands (i.e. /id, /register, /bridge, /chat, etc.).
#           If client sends /chat:
#               If client is in 'Wait' state:
#                   Wait for another client to connect.
#               If client is in 'Chat' state:
#                   Exchange messages between clients.
#           If KeyboardInterrupt:
#               Terminate the server.
#           Else:
#               Show an error message for wrong input.
#   Terminate program.


# =========================================================
# Parse input arguments
# =========================================================
parser = argparse.ArgumentParser(prog='Chat Program',
                    description='servers for clients',
                    epilog='this is the epilog')

parser.add_argument("--port", type=int, required=True, help="This is the Server Port")
args = parser.parse_args()

server_port = args.port

if not (server_port):
    print("PortError: Invalid server port number")
    exit(1)


# =========================================================
# Helper Function
# =========================================================
def send_message(sock, request_type, headers):
    message = f"{request_type}\r\n"
    for key, value in headers.items():
        message += f"{key}: {value}\r\n"
    message += "\r\n" 
    sock.send(message.encode())


#where we store client contact information
clients = {}
    
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        host_address = socket.gethostbyname(socket.gethostname())
        server_socket.bind((host_address, server_port))
        server_socket.listen(3)
        
        # list to monitor sockets and stdin
        sockets = [server_socket, sys.stdin]

        print("Server listening on", host_address + ":" + str(server_port))
        
        while True:
            readable, writable, exceptional = select.select(sockets, [], [])
            for s in readable:
                # New client connection
                if s is server_socket:
                    client_socket, client_address = server_socket.accept()
                    #client_host, client_port = client_address
                    sockets.append(client_socket)
                
                #if input is from stdin
                elif s is sys.stdin:
                    command = sys.stdin.readline().strip()
                    if command == "/info":
                        if clients:
                            for i in clients:
                                name, addr, port = clients[i] 
                                print(name, addr+":"+str(port))
                        else:
                            print("No clients yet!")
                else:
                    #recive the msg from client
                    #client_socket = s
                    data = s.recv(1024).decode()
                    if not data:
                        print("NO DATA")
                        break

                    # Split received message into request type and headers
                    lines = data.split("\r\n")
                    #getting the request type
                    request_type = lines[0]
                    #getting the header from the received message
                    headers = {i.split(":")[0].strip(): i.split(":")[1].strip() for i in lines[1:] if i}
                    #if "clientID" in headers:
                    #print(headers)
                    client_id = headers["clientID"]
                    

                    # =========================================================
                    # Command processing
                    # =========================================================
                    #/register
                    if request_type == "REGISTER":
                        #adding to the register header
                        headers["Status"] = "registered"
                        #store info
                        client_host = headers["IP"]
                        client_port = headers["Port"]
                        clients[client_id] = (client_id, client_host,client_port)

                        send_message(s, "REGACK", headers)

                        #Terminal output messages
                        print("REGISTER:",client_id,"from",client_host+":"+str(client_port), "received" )
                        

                    #/bridge
                    elif request_type == "BRIDGE":
                        #check to see if there are peers
                        peer = set(clients.keys()) - {client_id}
                        if peer:
                            peer_name = peer.pop()
                            #get peer values
                            #print(clients[peer_name])
                            peer_id, peer_host, peer_port = clients[peer_name] 
                            #update header
                            headers["clientID"] = peer_id
                            headers["IP"] = peer_host
                            headers["Port"] = peer_port

                            send_message(s, "BRIDGEACK", headers)

                            #Terminal output messages
                            print("BRIDGE:",client_id, client_host + ":" + str(client_port), peer_id, peer_host+":"+str(peer_port))
                            #exit(0)

                        #if no client has registered yet, then the header values are empty.
                        else:
                            headers["clientID"] = ''
                            headers["IP"] = ''
                            headers["Port"] = ''
                            send_message(s, "BRIDGEACK", headers)
                            #exit(0)


                    else:
                        print("Invalid Request Type.")

# =========================================================
# Exceptions
# =========================================================
except KeyboardInterrupt:
    print("\nProgram terminated by user.")
    exit(0)


# =========================================================
# Sources used
# =========================================================
#slide 14&15 multi socket monitoring - https://docs.google.com/presentation/d/1o1aN_iNx63fDRtfHwJfN1JtHGqJtmQlF2Z2XSanv5TY/edit#slide=id.g317e185fcce_0_514 