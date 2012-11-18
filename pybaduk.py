# -*- coding: utf-8 -*-
import os.path

from dulwich.repo import Repo
import dulwich.errors

import players
import pairings


if __name__ == "__main__":
    turnpath = '/home/freidrichen/tmp/turn'
    try:
        repo = Repo(turnpath)
    except dulwich.errors.NotGitRepository, error:
        if not os.path.isdir(turnpath):
            os.mkdir(turnpath)
        repo = Repo.init(turnpath)

    players = players.PlayerList(repo)
    if len(players) == 0:
        players.append({'given_name': u'Robert', 'family_name': u'Åhs'})
        players.append({'given_name': u'Eskil', 'family_name': u'Varenius',
                        'rank': '4K'})
        players.append({'given_name': u'Lukas', 'family_name': u'Lindroos',
                        'rank': '6K'})
        players.append({'given_name': u'Erik', 'family_name': u'Änterhake'})
        players.append({'given_name': u'Magnus', 'family_name': u'Sandén',
                        'rank': '7K'})
        players.append({'given_name': u'Niklas', 'family_name': u'Örjansson'})

    pairinglist = pairings.PairingList(repo)
    if len(pairinglist) == 0:
        pairinglist.append({'game_round': 1,
            'player1': 'Magnus_Sanden', 'player2': 'Eskil_Varenius'})
        pairinglist.append({'game_round': 1, 'player1': 'Lukas_Lindroos'})

    for player in players:
        if player['given_name'] == 'Eskil':
            player.remove()

    for player in sorted(players, key=lambda player: player['family_name']):
        print unicode(player)
