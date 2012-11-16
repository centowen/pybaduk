# -*- coding: utf-8 -*-
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit, parse_timezone
from time import time

import dulwich
import os.path
import json

import codecs
# egd_replace = codecs.replace_errors

def egd_replace(e):
    if e.object[e.start:e.end] == u'ö':
        return (u'oe', e.end)
    elif e.object[e.start:e.end] == u'Ö':
        return (u'Oe', e.end)
    elif e.object[e.start:e.end] == u'Ä':
        return (u'Ae', e.end)
    elif e.object[e.start:e.end] == u'ä':
        return (u'ae', e.end)
    elif e.object[e.start:e.end] == u'Å':
        return (u'Aa', e.end)
    elif e.object[e.start:e.end] == u'å':
        return (u'aa', e.end)
    elif e.object[e.start:e.end] == u'é':
        return (u'e', e.end)
    return codecs.ignore_errors(e)

codecs.register_error('egd', egd_replace)

class Player(object):
    def __init__(self, repo, params=None, path=None):
        self.repo = repo
        if path:
            self.rel_player_path = path
            self.fq_player_path = os.path.join(repo.path, self.rel_player_path) 
        elif params:
            given_name = params['given_name']
            family_name = params['family_name']
            filename = u'{0}_{1}'.format(
                    given_name, family_name).encode('ascii', errors='egd')
            self.rel_player_path = os.path.join(PlayerList.path, filename)
            self.fq_player_path = os.path.join(repo.path, self.rel_player_path) 
            json.dump(params, open(self.fq_player_path, 'w'))
            repo.stage(self.rel_player_path)
            repo.do_commit('appending new player.', committer = 'Should have some session id here.')


    def __str__(self):
        data = json.load(open(self.fq_player_path))
#         rank = data.get('rank', default='No rank')
        rank = data.get('rank', 'No rank')
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank).encode('ascii', errors='egd')

    def __unicode__(self):
        data = json.load(open(self.fq_player_path))
#         rank = data.get('rank', default='No rank')
        rank = data.get('rank', 'No rank')
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)

    def get_given_name(self):
        return self.get_player_property('given_name')
    def get_family_name(self):
        return self.get_player_property('family_name')
    def get_rank(self):
        return self.get_player_property('rank')
    def set_rank(self, rank):
        self.set_player_property('rank', rank)

    def set_given_name(self, given_name):
        newfilename = u'{0}_{1}'.format(
                given_name, self.get_family_name()).encode('ascii', errors='egd')
        
        print 'staging',self.rel_player_path

        new_rel_player_path = os.path.join(PlayerList.path, newfilename)
        new_fq_player_path = os.path.join(repo.path, new_rel_player_path)
        os.rename(self.fq_player_path, new_fq_player_path)
        repo.stage(self.rel_player_path)
        self.fq_player_path = new_fq_player_path
        self.rel_player_path = new_rel_player_path

        self.set_player_property('given_name', given_name)

    def set_family_name(self, family_name):
        newfilename = u'{0}_{1}'.format(
                self.get_given_name(), family_name).encode('ascii', errors='egd')
        
        new_rel_player_path = os.path.join(PlayerList.path, newfilename)
        new_fq_player_path = os.path.join(repo.path, new_rel_player_path)
        os.rename(self.fq_player_path, new_fq_player_path)
        repo.stage(self.rel_player_path)
        self.fq_player_path = new_fq_player_path
        self.rel_player_path = new_rel_player_path

        self.set_player_property('family_name', family_name)

    given_name = property(get_given_name, set_given_name)
    family_name = property(get_family_name, set_family_name)
    rank = property(get_rank, set_rank)

    def get_player_property(self, key):
        data = json.load(open(self.fq_player_path))
        return data[key]

    def set_player_property(self, key, value):
        data = json.load(open(self.fq_player_path))
        data[key] = value
        json.dump(data, open(self.fq_player_path, 'w'))
        repo.stage(self.rel_player_path)
        repo.do_commit('Modifying player.', committer = 'Should have some session id here.')


class PlayerList(object):
    """Class managing a git repository with a list of players."""
    path = 'players'

    def __init__(self, repo):
        self.repo = repo
        self.fq_playerdir_path = os.path.join(repo.path, PlayerList.path)
        if not os.path.isdir(self.fq_playerdir_path):
            os.mkdir(self.fq_playerdir_path)

    def __len__(self):
        return len(os.listdir(self.fq_playerdir_path))

    def __iter__(self):
        for player in os.listdir(self.fq_playerdir_path):
            yield Player(repo, path=os.path.join(self.path, player))

    def append(self, params):
        Player(self.repo, params=params)


if __name__ == "__main__":
    try:
        repo = Repo('/data/lindroos/pybaduk/turn')
    except dulwich.errors.NotGitRepository, error:
        os.mkdir('/data/lindroos/pybaduk/turn')
        repo = Repo.init("/data/lindroos/pybaduk/turn")
    p = PlayerList(repo)
#     print len(p)
    p.append({'given_name': u'Robert', 'family_name': u'Åhs'})
    p.append({'given_name': u'Eskil', 'family_name': u'Varenius'})
    p.append({'given_name': u'Lukas', 'family_name': u'Lindroos'})
    p.append({'given_name': u'Erik', 'family_name': u'Änterhake'})
    p.append({'given_name': u'Magnus', 'family_name': u'Sandén'})
    p.append({'given_name': u'Niklas', 'family_name': u'Örjansson'})

#     for player in p:
#         print unicode(player)

    list(p)[0].rank = '6K'
    for player in sorted(list(p), key=lambda player: player.family_name):
#         player.given_name = 'Jonas'
        print unicode(player)
#         print player.get_player_property('family_name')
