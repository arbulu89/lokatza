"""
:author: xarbulu
:organization: SUSE LLC
:contact: xarbulu@suse.com

:since: 2023-01-31
"""

import json

class Player(object):
    '''
    Player
    '''

    def __init__(self, id, name, phone, cyclists):
        self.id = id
        self.name = name
        self.phone = phone
        self.cyclists = cyclists

    def print(self):
        print("""Player:
ID: %d,
Name: %s,
Phone: %s,
Cyclists: %s""" % (self.id, self.name, self.phone, self.cyclists))

class Players(object):
    '''
    Players management service
    '''

    def __init__(self, db):
        self._db = db

    def add_player(self, id, name, phone, cyclists):
        self._db.add_player(
            id, name, phone, json.dumps(cyclists))

    def add_player_from_object(self, player):
        self.add_player(player.id, player.name, player.phone, player.cyclists)

    def get_players(self):
        players = []
        players_raw = self._db.get_players()
        for player in players_raw:
            cyclists = json.loads(player[3])
            players.append(Player(player[0], player[1], player[2], cyclists))

        return players

    def delete_players(self):
        self._db.delete_players()
