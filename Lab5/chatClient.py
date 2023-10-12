import socket
import threading
import json
import os

HOST = '127.0.0.1'
PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")  # Move this line to the beginning

# Prompt the user for their name and desired room
name = input("Enter your name: ")
room = input("Enter the room you want to connect: ")

# Create a "connect" type message for the initial connection
connect_message = {
    "type": "connect",
    "payload": {
        "name": name,
        "room": room
    }
}
# Send the "connect" message to the server
client_socket.send(json.dumps(connect_message).encode('utf-8'))


def receive_messages():
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break

            message_json = json.loads(message.decode('utf-8'))
            message_type = message_json.get('type', '')

            if message_type == 'message':
                sender = message_json['payload']['sender']
                text = message_json['payload']['text']
                print(f"{sender}: {text}")
            elif message_type == 'notification':
                notification_message = message_json['payload']['message']
                print(f"Notification: {notification_message}")

        except UnicodeDecodeError:
            # Handle binary data, such as file transfers
            # You can implement the handling of binary data here
            pass

receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()


while True:
    message_text = input("Enter a message or file command (e.g., 'upload: <path>' or 'download: <file.extention>') or 'exit' to quit: ")

    if message_text.lower() == 'exit':
        break

    if message_text.startswith('upload:'):
        file_path = message_text.split(': ')[1]
        if os.path.exists(file_path):
            message_json = {
                "type": "file_command",
                "payload": {
                    "command": f"upload: {file_path}"
                }
            }
            client_socket.send(json.dumps(message_json).encode('utf-8'))
        else:
            print(f"File {file_path} doesn't exist.")
    elif message_text.startswith('download:'):
        message_json = {
            "type": "file_command",
            "payload": {
                "command": message_text
            }
        }
        client_socket.send(json.dumps(message_json).encode('utf-8'))
    else:
        # Handle regular text messages
        message_json = {
            "type": "message",
            "payload": {
                "sender": name,
                "room": room,
                "text": message_text
            }
        }
        client_socket.send(json.dumps(message_json).encode('utf-8'))


client_socket.close()