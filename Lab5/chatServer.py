import socket
import threading
import json
import os

HOST = '127.0.0.1'
PORT = 12345

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")

# Create a dictionary to store clients and their associated rooms
clients = {}


def handle_client(client_socket, client_address):
    global room_name, client_name
    print(f"Accepted connection from {client_address}")

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        message_json = json.loads(message)
        message_type = message_json.get('type', '')

        if message_type == 'connect':
            # Handle connection request and send acknowledgment
            client_name = message_json['payload']['name']
            room_name = message_json['payload']['room']
            print(f"{client_name} connected to {room_name}")
            acknowledgment_json = {
                "type": "connect_ack",
                "payload": {
                    "message": "Connected to the room."
                }
            }
            client_socket.send(json.dumps(acknowledgment_json).encode('utf-8'))

            # Store the client's room association
            clients[client_socket] = room_name

            # Send previous messages in the room to the new client
            for msg_socket, msg_room in clients.items():
                if msg_socket != client_socket and msg_room == room_name:
                    msg_socket.send(json.dumps(message_json).encode('utf-8'))

        elif message_type == 'message':
            sender = message_json['payload']['sender']
            room = clients[client_socket]
            text = message_json['payload']['text']
            print(f"Received from {sender} in {room}: {text}")

            # Broadcast the message to clients in the same room
            for msg_socket, msg_room in clients.items():
                if msg_socket != client_socket and msg_room == room:
                    msg_socket.send(json.dumps(message_json).encode('utf-8'))
        elif message_type == 'file_command':
            command = message_json['payload']['command']
            if command.startswith('upload:'):
                file_path = command.split(': ')[1]
                if os.path.exists(file_path):
                    # Ensure that the room-specific folder exists
                    room_folder = os.path.join('Server_media', room_name)
                    os.makedirs(room_folder, exist_ok=True)  # Create folder if it doesn't exist

                    # Read the file and send it to the server
                    with open(file_path, 'rb') as file:
                        file_data = file.read()
                        file_name = os.path.basename(file_path)
                        server_media_path = os.path.join(room_folder, file_name)
                        with open(server_media_path, 'wb') as server_file:
                            server_file.write(file_data)

                    # Notify clients in the same room, including the client that uploaded the file
                    for msg_socket, msg_room in clients.items():
                        if msg_room == room_name:
                            msg_socket.send(json.dumps({
                                "type": "notification",
                                "payload": {
                                    "message": f"User {client_name} uploaded {file_name}."
                                }
                            }).encode('utf-8'))
                else:
                    # Notify the client that the file doesn't exist
                    client_socket.send(json.dumps({
                        "type": "notification",
                        "payload": {
                            "message": f"File {file_path} doesn't exist."
                        }
                    }).encode('utf-8'))
            elif command.startswith('download:'):
                requested_file = command.split(': ')[1]
                server_media_path = os.path.join('Server_media', room_name, requested_file)

                if os.path.exists(server_media_path):
                    with open(server_media_path, 'rb') as file:
                        file_data = file.read()

                    client_socket.send(file_data)

                    client_media_folder = os.path.join('Downloads', client_name)
                    os.makedirs(client_media_folder, exist_ok=True)
                    client_file_path = os.path.join(client_media_folder, requested_file)

                    with open(client_file_path, 'wb') as client_file:
                        client_file.write(file_data)

                    # Notify the client that the file was downloaded successfully
                    client_socket.send(json.dumps({
                        "type": "notification",
                        "payload": {
                            "message": f"File {requested_file} downloaded."
                        }
                    }).encode('utf-8'))
                else:
                    client_socket.send(json.dumps({
                        "type": "notification",
                        "payload": {
                            "message": f"The {requested_file} doesn't exist."
                        }
                    }).encode('utf-8'))
    del clients[client_socket]
    client_socket.close()


while True:
    client_socket, client_address = server_socket.accept()
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()