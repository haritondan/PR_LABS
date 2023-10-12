import socket
import threading
import json

# Server configuration
HOST = '127.0.0.1'  # Loopback address for localhost
PORT = 12345  # Port to listen on

previous_message=''

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the specified address and port
server_socket.bind((HOST, PORT))

# Listen for incoming connections
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

# Store client information in a dictionary
clients = {}  # {client_socket: {"name": name, "room": room}}

# Function to handle a client's messages
def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            message_json = json.loads(message)
            message_type = message_json.get("type")
            
            if message_type == "connect":
                name = message_json["payload"]["name"]
                room = message_json["payload"]["room"]
                clients[client_socket] = {"name": name, "room": room}
                
                # Notify the client of successful connection
                connect_ack_message = {
                    "type": "connect_ack",
                    "payload": {
                        "message": "Connected to the room."
                    }
                }
                client_socket.sendall(json.dumps(connect_ack_message).encode('utf-8'))
                
                # Notify other clients in the room about the new user
                notification_message = {
                    "type": "notification",
                    "payload": {
                        "message": f"{name} has joined the room."
                    }
                }
                broadcast_message_to_room(notification_message, room)
            
            elif message_type == "message":
                sender_name = clients[client_socket]["name"]
                room = clients[client_socket]["room"]
                text = message_json["payload"]["text"]
                
                # Broadcast the message to all clients in the same room
                message_to_broadcast = {
                    "type": "message",
                    "payload": {
                        "sender": sender_name,
                        "room": room,
                        "text": text
                    }
                }
                broadcast_message_to_room(message_to_broadcast, room)

            elif message_type == "upload":
                # Extract the filename and file data from the message
                filename = message_json["payload"]["filename"]
                file_data = message_json["payload"]["data"]

                # Save the file data to a file in the SERVER_MEDIA directory
                with open(f"SERVER_MEDIA/{filename}", 'w') as file:
                    file.write(file_data)

                # Send a response to the client indicating that the upload was successful
                upload_ack_message = {
                    "type": "upload_ack",
                    "payload": {
                        "message": f"User {clients[client_socket]['name']} uploaded the {filename} file."
                    }
                }
                client_socket.sendall(json.dumps(upload_ack_message).encode('utf-8'))

                # Notify other clients in the room about the new file
                notification_message = {
                    "type": "notification",
                    "payload": {
                        "message": f"User {clients[client_socket]['name']} has uploaded a new file: {filename}."
                    }
                }
                broadcast_message_to_room(notification_message, clients[client_socket]["room"])

        except (json.JSONDecodeError, KeyError):
            # Handle JSON decoding errors or missing keys
            pass
        except:
            break  # Exit the loop when the client disconnects
    
    # Remove the client from the dictionary
    if client_socket in clients:
        del clients[client_socket]
    
    client_socket.close()

# Function to broadcast a message to all clients in a specific room
def broadcast_message_to_room(message, room):
    # Display the message in the format: [Room Name]: [Sender's Name]: [Message Text]
    if message['type'] == 'notification':
        formatted_message = f"{room}: {message['payload']['message']}"
    elif message['type'] == 'message':
        formatted_message = f"{room}: {message['payload']['sender']}: {message['payload']['text']}"
    print(formatted_message)

    for client_socket, client_info in clients.items():
        if client_info["room"] == room:
            client_socket.sendall(json.dumps(message).encode('utf-8'))

while True:
    client_socket, client_address = server_socket.accept()
    clients[client_socket] = {"name": None, "room": None}
    
    # Start a thread to handle the client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
