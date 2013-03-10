# -*- coding: utf-8 -*-
import os
import codecs

import egdcodec
from tournament import Tournament, Field
from PyQt4.QtCore import QSettings


codecs.register_error('egd', egdcodec.egd_replace)


if __name__ == "__main__":
    settings = QSettings('weirdo', 'pybaduk')

    turnpath = str(settings.value('turnpath').toString())
    if not turnpath:
        turnpath = './turn'
        settings.setValue('turnpath', turnpath)
    if not (os.path.exists(turnpath)):
        os.makedirs(turnpath)
    print turnpath
    tournament = Tournament(turnpath, u'Göteborg Open 2013')

    players = tournament.players
    if not players:
        players.append({'Given name': u'Robert', 'Family name': u'Åhs', 'Rank': '1K'})
        eskil_id = players.append({'Given name': u'Eskil', 'Family name': u'Varenius', 'Rank': '4K'})
        lukas_id = players.append({'Given name': u'Lukas', 'Family name': u'Lindroos', 'Rank': '6K'})
        players.append({'Given name': u'Erik', 'Family name': u'Änterhake', 'Rank': '30K'})
        magnus_id = players.append({'Given name': u'Magnus', 'Family name': u'Sandén', 'Rank': '7K'})
        players.append({'Given name': u'Niklas', 'Family name': u'Örjansson', 'Rank': '2D'})

    tournament.add_player_field(Field(u'Has päjd', bool))
    players[magnus_id][u'Has päjd'] = True
    print players[magnus_id][u'Has päjd']
    print players[eskil_id][u'Has päjd']

    #round0_pairs = tournament.pairings[0]
    #if not round0_pairs:
    #    round0_pairs.append(magnus_id, eskil_id)
    #    round0_pairs.append(lukas_id)

    #for player in players:
    #    if player['Given name'] == 'Eskil':
    #        player.remove()
    #    elif player['Rank'] == '7K':
    #        player['Family name'] = 'Andersson'

    #for player in players:
    #    if player['Given name'] == 'Magnus':
    #        tournament.remove_player(player)
    #        break

    #for player in sorted(players, key=lambda player: player['Family name']):
    #    print(unicode(player))

    #for pairing in round0_pairs:
    #    print(unicode(pairing))
