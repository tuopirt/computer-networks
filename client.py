# =========================================================
# Filename: s1<yzhou253>s2<ibae>Client2.py
# Description: clients for our chat program
# Author: Harrison Zhou, Inha Bae
# Date Created: <2024-11-20>
# Last Modified: <Last Modified Date>
# Version: 1.0
# =========================================================
import socket
import argparse
import sys


# =========================================================
# Pseudocode
# =========================================================
# Parse input arguments: --id <ClientID> --port <Client port>: int, --server <Server IP: Port number>: str
# If port and server argument are not valid. 
#   Then, print to stdout error.
# Else:
# 	Run indefinitely:
# 		Get input 
# 	  If input is /id: Return id of the user
#     Else if input is /register: Send a register request to the server
#     Else if input is /bridge: Send a bridge request to the server & process the response you get
#     Else if KeyboardInterrupt: terminate
#     Else: show an error message for wrong input
# Terminate program 

# =========================================================
# Parse input arguments
# =========================================================
parser = argparse.ArgumentParser(prog='Chat Program',
                    description='client to connect to server',
                    epilog='this is the epilog')

# add_argument skeleton
# ArgumentParser.add_argument(name, *[, action][, nargs][, const][, default][, type][, choices][, required]
#                             [, help][, metavar][, dest][, deprecated])Â¶
parser.add_argument("--id", required=True, help="This is the Client ID")
parser.add_argument("--port", type=int, required=True, help="This is the Client Port")
parser.add_argument("--server", type=str, required=True, help="This is the Server IP:PORT#")

#run the parser
args = parser.parse_args()
#print("argparse.Namespace object: ",args.id, args.port, args.server)

#renaming
client_id = args.id
client_port = args.port
server_address, server_port = args.server.split(":")
server_port = int(server_port)

# =========================================================
# Port/Server validation
# =========================================================
# Validate port and server arguments
if not (client_port or server_address or server_port):
    print("Error: Invalid port number(s) or Server ip")
    exit(1)


def send_message(sock, request_type, headers):
    message = f"{request_type}\r\n"
    for key, value in headers.items():
        message += f"{key}: {value}\r\n"
    message += "\r\n"  

    sock.send(message.encode())

STATE = "NONE"  

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #configuration of the socket
        host_address = socket.gethostbyname(socket.gethostname())
        client_socket.bind((host_address, client_port))  #bind the local port
        client_socket.connect((server_address, server_port))
        REGACK_RECEIVED = False

        #reports to terminal after client start
        print(client_id, "running on", host_address + ":" + str(client_port))
        
        while True:
            # Get input 
            command = sys.stdin.readline().strip()
            #print("command ",command)
            # =========================================================
            # Command processing
            # =========================================================
            # If input is /id: Return id of the user
            if command == "/id":
                #print(client_id)
                sys.stdout.write(client_id + '\n')
            
            # Else if input is /register: Send a register request to the server
            elif command == "/register":
                headers = {
                    "clientID": client_id,
                    "IP": host_address,
                    "Port": client_port
                }
                send_message(client_socket, "REGISTER", headers)
                #print("waiting response")
                response = client_socket.recv(1024).decode()
                #print(response)
                if "REGACK" in response:
                    REGACK_RECEIVED = True
                else:
                    print("Error: No REGACK received")
                    client_socket.close()
                    exit(1)

            # Else if input is /bridge: Send a bridge request to the server & process the response you get
            elif command == "/bridge":
                if not REGACK_RECEIVED:
                    print("/register comes before /bridge")
                else:
                    headers = {
                        "clientID": client_id
                    }
                    send_message(client_socket, "BRIDGE", headers)

                    # Receive the response
                    response = client_socket.recv(1024).decode()
                    #print(response)

                    lines = response.split("\r\n")
                    respond_type = lines[0]
                    peer_info = {i.split(":")[0].strip(): i.split(":")[1].strip() for i in lines[1:] if i}

                    if respond_type == "BRIDGEACK":
                        #attempt to get peer info
                        peer_id =  peer_info["clientID"]
                        peer_host = peer_info["IP"]
                        peer_port = peer_info["Port"]
                        #if we got info, means there is a peer
                        if peer_host and peer_port:
                            STATE = "CHAT"
                            #print("\npeer found:", peer_id, peer_host, peer_port)
                        #empty ACK goes to wait
                        else:
                            STATE = "WAIT"
                            #print("\nno peers yet, going into waiting")
                    else:
                        print("Error: No BRIDGEACK received")
                        client_socket.close()
                        exit(1)

            #process /chat
            elif command == "/chat":
                #if we can chat
                if STATE == "CHAT":
                    #we start the chat here
                    #print("\nAttemping to start chat with:", peer_id, peer_host, peer_port)

                    #new chat socket
                    chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    chat_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    chat_socket.bind((host_address, client_port))
                    chat_socket.connect((peer_host, int(peer_port)))

                    #print("\nConnected to peer. Start conversation.")
                    while True:
                        #print("This terminal: ")
                        send_msg = sys.stdin.readline().strip()
                        if send_msg == "/quit":
                            print("\nCHAT: sending client termination message")
                            chat_socket.sendall("/quit".encode())
                            chat_socket.close()
                            exit(0)
                        chat_socket.sendall(send_msg.encode())
                        #chat_socket.sendall((client_id+""+send_msg).encode())
                        recv_msg = chat_socket.recv(1024).decode()
                        if recv_msg == "/quit":
                            print("\nCHAT: recived termination message, closing")
                            chat_socket.close()
                            exit(0)
                        #print("recv: ", recv_msg)
                        print(recv_msg)

                #do we need this else?
                else:
                    print("awaiting chat reuqest")
                    pass

            #handle /quit
            elif command == "/quit":
                print("Program terminated.")
                client_socket.close()
                exit(0)

            # Else: show an error message for wrong input
            else:
                print("InputError: Invalid command")

            #catching clients that has transitioned into wait
            if STATE == "WAIT":
                #new socket to listen from peer
                listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                listen_socket.bind((host_address, client_port))
                listen_socket.listen(3)

                #print("\nWaiting for chat requests...")
                incoming_socket, incoming_address = listen_socket.accept()
                incoming_host, incoming_port = incoming_address
                #print(incoming_socket, incoming_address)
                if incoming_socket:
                    print("Incoming chat request from",client_id, incoming_host+":"+str(incoming_port))
                    while True:
                        recv_msg = incoming_socket.recv(1024).decode()
                        if recv_msg == "/quit":
                            print("\nWAIT: recived termination message, closing")
                            incoming_socket.close()
                            exit(0)
                        #print("recv: ", recv_msg)
                        print(recv_msg)
                        #print("This terminal: ")
                        send_msg = sys.stdin.readline().strip()
                        if send_msg == "/quit":
                            print("\nWAIT: sending client termination message")
                            incoming_socket.sendall("/quit".encode())
                            incoming_socket.close()
                            exit(0)
                        incoming_socket.sendall(send_msg.encode())
                        #incoming_socket.sendall((client_id+""+send_msg).encode())


            

# =========================================================
# Exceptions
# =========================================================
#ctrl + c
except KeyboardInterrupt:
    print("\nProgram termianted by user.")
    client_socket.close()
    exit(0)
#multi port use
except socket.error:
    print("SocketError: Port already in use", client_port)
    client_socket.close()
    exit(1)

# =========================================================
# Sources used
# =========================================================
# parsing: https://docs.python.org/3/library/argparse.html
# ctrl+c termination: https://www.geeksforgeeks.org/how-to-catch-a-keyboardinterrupt-in-python/
# socket binding: https://www.ibm.com/docs/en/zos/2.4.0?topic=functions-bind-bind-name-socket 
# socket reconfiguration: https://docs.python.org/3/library/socket.html (all the way at the bottom)