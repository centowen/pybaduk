# -*- coding: utf-8 -*-
import os
import codecs
import shutil
import sys

import egdcodec
from tournament import Tournament, Field
from PyQt4.QtCore import QSettings


codecs.register_error('egd', egdcodec.egd_replace)


if __name__ == "__main__":
    settings = QSettings('weirdo', 'pybaduk')
    turnname = u'Göteborg Open 2013'

    turnpath = str(settings.value('turnpath').toString())
    if turnpath in ('/', '.', '..', '*', '~', '//'):
        print "OMG!!!!!"
        sys.exit(255)
    if not turnpath:
        turnpath = './turn'
        settings.setValue('turnpath', turnpath)
    if not (os.path.exists(turnpath)):
        os.makedirs(turnpath)
    elif os.path.exists(os.path.join(turnpath, turnname.encode('ascii', 'egd'))):
        print u'Tournament {0} in turnpath {1} exists. Type \'remove\' to remove it.'.format(turnname, turnpath)
        if raw_input() == 'remove':
            shutil.rmtree(os.path.join(turnpath, turnname.encode('ascii', 'egd')))

    tournament = Tournament(turnpath, turnname)
    tournament.add_player_field(Field(u'Club', datatype='text', default=u'Göteborg'))
    tournament.add_player_field(Field(u'Country', 'text'))

    players = tournament.players
    if not players:
        tournament.add_player({'Given name': u'Robert', 'Family name': u'Åhs', 'Rank': '1k'})
        eskil = tournament.add_player({'Given name': u'Eskil', 'Family name': u'Varenius', 'Rank': '4k'})
        lukas = tournament.add_player({'Given name': u'Lukas', 'Family name': u'Lindroos', 'Rank': '6k'})
        tournament.add_player({'Given name': u'Erik', 'Family name': u'Änterhake', 'Rank': '30k'})
        magnus = tournament.add_player({'Given name': u'Magnus', 'Family name': u'Sandén', 'Rank': '4d'})
        tournament.add_player({'Given name': u'Niklas', 'Family name': u'Örjansson', 'Rank': '2d'})
        tournament.add_player({'Given name': u'Niklas', 'Family name': u'Eriksson', 'Rank': None})
        tournament.add_player({'Given name': u'Erika', 'Family name': u'Eriksson', 'Rank': '4p'})
        tournament.add_player({'Given name': u'Kajsa', 'Family name': u'Eriksson', 'Rank': '4p'})

#     tournament.add_player_field(Field(u'Has päjd', bool))
#     magnus[u'Has päjd'] = True
