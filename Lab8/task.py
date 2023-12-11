import uuid
import requests
import socket
import json
import random
from flask import Flask, request


class CRUD:
    is_leader: bool
    followers: dict

    records: dict

    def __init__(self, is_leader, followers):
        self.records = {}
        self.is_leader = is_leader

        if self.is_leader:
            self.followers = followers

    def create_record(self, record_data):
        if 'id' not in record_data.keys():
            record_data['id'] = str(uuid.uuid4())

        self.records[record_data['id']] = record_data

        if self.is_leader:
            for follower in self.followers:
                requests.post(
                    f"http://127.0.0.1:{follower['port']}/scooter/create",
                    json=record_data,
                    headers={'Token': "Leader"}
                )

        return {'message': "Record created"}, 200

    def read_records(self):
        return_data = {}
        return_data['records'] = []

        for key in self.records.keys():
            return_data['records'].append(self.records[key])

        return return_data, 200

    def update(self, requested_id, new_data):
        if requested_id in self.records:
            self.records[requested_id].update(new_data)

            if self.is_leader:
                for follower in self.followers:
                    requests.put(
                        f"http://127.0.0.1:{follower['port']}/scooter/update-scooter/{requested_id}",
                        json=new_data,
                        headers={'Token': "Leader"}
                    )

            return {'message': "Record updated"}, 200
        else:
            return {'mesage': "Record doesn't exist"}, 404

    def delete_records(self, requested_id):
        if requested_id in self.records:
            self.records.pop(requested_id)

            if self.is_leader:
                for follower in self.followers:
                    requests.delete(
                        f"http://127.0.0.1:{follower['port']}/scooter/delete-scooter/{requested_id}",
                        headers={'Token': "Leader"}
                    )

            return {'message': "Record was deleted"}, 200
        else:
            return {'message': "Record doesn't exist"}, 404


class RAFT():
    def __init__(self, udp_host, udp_port):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def elections(self, http_service, num_followers):
        max_msg_num = num_followers * 2
        elections = {}

        try:
            self.udp_socket.bind((self.udp_host, self.udp_port))

            elections['role_assigned'] = "Leader"
            elections['leader'] = None
            elections['followers'] = []

            msg_count = 0

            while True:
                message, address = self.udp_socket.recvfrom(2048)

                if message.decode() == "Accept":
                    msg_count += 1
                    self.udp_socket.sendto(str.encode(json.dumps(http_service)), address)
                else:
                    msg_count += 1
                    elections['followers'].append(json.loads(message.decode()))

                if msg_count >= max_msg_num:
                    break

        except:
            self.udp_socket.bind((self.udp_host, self.udp_port + random.randint(1, 666)))

            elections['role_assigned'] = "Follower"
            elections['leader'] = self.send_accept("Accept")
            elections['followers'] = None
            self.send_accept(http_service)

        self.udp_socket.close()
        return elections

    def send_accept(self, msg):
        if type(msg) is str:
            self.udp_socket.sendto(str.encode(msg), (self.udp_host, self.udp_port))
            response = self.udp_socket.recvfrom(2048)[0]
            return json.loads(response.decode())
        else:
            self.udp_socket.sendto(str.encode(json.dumps(msg)), (self.udp_host, self.udp_port))


service = {
    'host': "127.0.0.1",
    'port': random.randint(5000, 6000),
    'is_leader': None,
}

raft = RAFT(service['host'], 4444)
elections = raft.elections(service, 2)

if elections['role_assigned'] == "Leader":
    service['is_leader'] = True
else:
    service['is_leader'] = False

crud = CRUD(service['is_leader'], elections['followers'])

print(f"{service['host']}:{service['port']} - {elections['role_assigned']}")

app = Flask(__name__)


@app.route(f"/scooter/create", methods=['POST'])
def add():
    if crud.is_leader or (
            not crud.is_leader and ('Token' in dict(request.headers) and dict(request.headers)['Token'] == "Leader")):
        return_data, status_code = crud.create_record(request.json)
        return return_data, status_code
    else:
        return {'message': "Unauthorized"}, 403


@app.route(f"/scooter/get-scooters", methods=['GET'])
def read_records():
    return_data, status_code = crud.read_records()
    return return_data, status_code


@app.route(f"/scooter/update-scooter/<id>", methods=['PUT'])
def update(id):
    if crud.is_leader or (
            not crud.is_leader and ('Token' in dict(request.headers) and dict(request.headers)['Token'] == "Leader")):
        return_data, status_code = crud.update(id, request.json)
        return return_data, status_code
    else:
        return {'message': "Unauthorized"}, 403


@app.route(f"/scooter/delete-scooter/<id>", methods=['DELETE'])
def delete_records(id):
    if crud.is_leader or (
            not crud.is_leader and ('Token' in dict(request.headers) and dict(request.headers)['Token'] == "Leader")):
        return_data, status_code = crud.delete_records(id)
        return return_data, status_code
    else:
        return {'message': "Unauthorized"}, 403


app.run(
    host=service['host'],
    port=service['port']
)