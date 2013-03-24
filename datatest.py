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
    tournament = Tournament(turnpath, u'Göteborg Open 2013')
    tournament.add_player_field(Field(u'Club', datatype=unicode, default=u'Göteborg'))
    tournament.add_player_field(Field(u'Country', unicode))

    players = tournament.players
    if not players:
        tournament.add_player({'Given name': u'Robert', 'Family name': u'Åhs', 'Rank': '1K'})
        eskil = tournament.add_player({'Given name': u'Eskil', 'Family name': u'Varenius', 'Rank': '4K'})
        lukas = tournament.add_player({'Given name': u'Lukas', 'Family name': u'Lindroos', 'Rank': '6K'})
        tournament.add_player({'Given name': u'Erik', 'Family name': u'Änterhake', 'Rank': '30K'})
        magnus = tournament.add_player({'Given name': u'Magnus', 'Family name': u'Sandén', 'Rank': '7K'})
        tournament.add_player({'Given name': u'Niklas', 'Family name': u'Örjansson', 'Rank': '2D'})

    tournament.add_player_field(Field(u'Has päjd', bool))
    magnus[u'Has päjd'] = True
