# -*- coding: utf-8 -*-
import os
import codecs

import egdcodec
from tournament import Tournament
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
        players.append({'given_name': u'Robert', 'family_name': u'Åhs', 'rank': '1K'})
        eskil_id = players.append({'given_name': u'Eskil', 'family_name': u'Varenius', 'rank': '4K'})
        lukas_id = players.append({'given_name': u'Lukas', 'family_name': u'Lindroos', 'rank': '6K'})
        players.append({'given_name': u'Erik', 'family_name': u'Änterhake', 'rank': '30K'})
        magnus_id = players.append({'given_name': u'Magnus', 'family_name': u'Sandén', 'rank': '7K'})
        players.append({'given_name': u'Niklas', 'family_name': u'Örjansson', 'rank': '2D'})

    round0_pairs = tournament.pairings[0]
    if not round0_pairs:
        round0_pairs.append(magnus_id, eskil_id)
        round0_pairs.append(lukas_id)

    #for player in players:
    #    if player['given_name'] == 'Eskil':
    #        player.remove()
    #    elif player['rank'] == '7K':
    #        player['family_name'] = 'Andersson'

    for player in players:
        if player['given_name'] == 'Magnus':
            tournament.remove_player(player)
            break

    for player in sorted(players, key=lambda player: player['family_name']):
        print(unicode(player))

    for pairing in round0_pairs:
        print(unicode(pairing))
