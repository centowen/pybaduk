# -*- coding: utf-8 -*-
import codecs

import egdcodec
from tournament import Tournament


codecs.register_error('egd', egdcodec.egd_replace)


if __name__ == "__main__":
#     turnpath = '/home/freidrichen/tmp/turn'
    turnpath = '/data/lindroos/pybaduk/turn'
    gbgopen = Tournament(turnpath, u'Göteborg Open 2013')

    players = gbgopen.players
    if not players:
        players.append({'given_name': u'Robert', 'family_name': u'Åhs'})
        eskil_id = players.append({'given_name': u'Eskil',
                                   'family_name': u'Varenius', 'rank': '4K'})
        lukas_id = players.append({'given_name': u'Lukas', 'family_name': u'Lindroos',
                                   'rank': '6K'})
        players.append({'given_name': u'Erik', 'family_name': u'Änterhake'})
        magnus_id = players.append({'given_name': u'Magnus', 'family_name': u'Sandén',
                                    'rank': '7K'})
        players.append({'given_name': u'Niklas', 'family_name': u'Örjansson'})

    round0_pairs = gbgopen.pairings[0]
    if not round0_pairs:
#         round0_pairs.append(magnus_id, eskil_id)
        round0_pairs.append(lukas_id)

    #for player in players:
    #    if player['given_name'] == 'Eskil':
    #        player.remove()
    #    elif player['rank'] == '7K':
    #        player['family_name'] = 'Andersson'

    tmp = sorted(players, key=lambda player: player['family_name'])
    print tmp
    for player in tmp:
        if player['given_name'] == 'Magnus':
            player.remove()
            break

    for player in sorted(players, key=lambda player: player['family_name']):
        print(unicode(player))

    for pairing in round0_pairs:
        print(unicode(pairing))
