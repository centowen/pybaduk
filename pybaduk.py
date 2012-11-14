# -*- coding: utf-8 -*-
from dulwich.repo import Repo
import os.path
import json

import codecs
egd_replace = codecs.replace_errors
codecs.register_error('egd', egd_replace)


class Player(object):
    def __init__(self, repo, params=None, path=None):
        self.repo = repo
        if path:
            self.fq_player_path = path
        elif params:
            given_name = params['given_name']
            family_name = params['family_name']
            filename = u'{0}_{1}'.format(
                    given_name, family_name).encode('ascii', errors='egd')
            self.fq_player_path = os.path.join(repo.path, PlayerList.path, filename)
            json.dump(params, open(self.fq_player_path, 'w'))

    def __unicode__(self):
        data = json.load(open(self.fq_player_path))
#         rank = data.get('rank', default='No rank')
        rank = data.get('rank', 'No rank')
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)


class PlayerList(object):
    """Class managing a git repository with a list of players."""
    path = 'players'

    def __init__(self, repo):
        self.repo = repo
        self.fq_playerdir_path = os.path.join(repo.path, PlayerList.path)
        print self.fq_playerdir_path
        if not os.path.isdir(self.fq_playerdir_path):
            os.mkdir(self.fq_playerdir_path)

    def __len__(self):
        return len(os.listdir(self.fq_playerdir_path))

    def __iter__(self):
        for player in os.listdir(self.fq_playerdir_path):
            yield Player(repo, path=os.path.join(self.fq_playerdir_path, player))

    def add(self, params):
        Player(self.repo, params=params)


if __name__ == "__main__":
    repo = Repo('/data/lindroos/pybaduk/turn')
    p = PlayerList(repo)
    print len(p)
    p.add({'given_name': u'Magnus', 'family_name': u'Sandén'})
    for player in p:
        print unicode(player)
