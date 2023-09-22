import xml.etree.ElementTree as ET

import player_pb2
from player import Player
from google.protobuf.json_format import MessageToDict
from google.protobuf.json_format import ParseDict

class PlayerFactory:
    def to_json(self, players):
        return [
            {
                "nickname": player.nickname,
                "email": player.email,
                "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d"),
                "xp": player.xp,
                "class": player.cls
            }
            for player in players
        ]

    def from_json(self, list_of_dict):
        return [
            Player(
                data["nickname"],
                data["email"],
                data["date_of_birth"],
                data["xp"],
                data["class"]
            )
            for data in list_of_dict
        ]

    def from_xml(self, xml_string):
        players = []
        root = ET.fromstring(xml_string)
        for player_elem in root.findall('player'):
            nickname = player_elem.find('nickname').text
            email = player_elem.find('email').text
            date_of_birth = player_elem.find('date_of_birth').text
            xp = int(player_elem.find('xp').text)
            cls = player_elem.find('class').text
            player = Player(nickname, email, date_of_birth, xp, cls)
            players.append(player)
        return players

    def to_xml(self, list_of_players):
        root = ET.Element("data")
        for player in list_of_players:
            player_elem = ET.Element("player")
            nickname_elem = ET.Element("nickname")
            nickname_elem.text = player.nickname
            email_elem = ET.Element("email")
            email_elem.text = player.email
            dob_elem = ET.Element("date_of_birth")
            dob_elem.text = player.date_of_birth.strftime("%Y-%m-%d")
            xp_elem = ET.Element("xp")
            xp_elem.text = str(player.xp)
            class_elem = ET.Element("class")
            class_elem.text = player.cls
            player_elem.extend([nickname_elem, email_elem, dob_elem, xp_elem, class_elem])
            root.append(player_elem)
        return ET.tostring(root, encoding="utf-8").decode("utf-8")

    def from_protobuf(self, binary):
        players_list_protobuf = player_pb2.PlayersList()
        players_list_protobuf.ParseFromString(binary)

        players = []
        for player_protobuf in players_list_protobuf.player:
            player_dict = MessageToDict(player_protobuf)
            date_of_birth = player_dict.pop('dateOfBirth', None)
            if date_of_birth:
                player_dict['date_of_birth'] = date_of_birth
            cls = player_dict.get('cls')
            if isinstance(cls, int):
                player_dict['cls'] = player_pb2.Class.Name(cls)
            player = Player(**player_dict)
            players.append(player)

        return players


    def to_protobuf(self, players):
        players_list_protobuf = player_pb2.PlayersList()

        for player in players:
            player_dict = player.__dict__
            player_dict['date_of_birth'] = player_dict['date_of_birth'].strftime("%Y-%m-%d")
            player_dict['cls'] = player_pb2.Class.Value(player_dict['cls'])
            player_protobuf = players_list_protobuf.player.add()
            ParseDict(player_dict, player_protobuf)

        binary = players_list_protobuf.SerializeToString()

        return binary


