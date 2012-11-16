# -*- coding: utf-8 -*-
from dulwich.repo import Repo
from time import time

import dulwich.errors
import os.path
import json

import codecs
import egdcodec

codecs.register_error('egd', egdcodec.egd_replace)

class PairingModError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
class PlayerModError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
class GitLoadError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

class GitEntry(object):
    def __init__(self, repo, params=None, git_table=None, index=None):
        self.repo = repo
        if not isinstance(git_table, str):
            raise GitLoadError('Invalid git_table (players, pairings, etc...) specified.')
        elif not isinstance(index, str):
            raise GitLoadError('Invalid index (filename) specified: "{0}".'.format(index))

        self.rel_path = os.path.join(git_table, index)
        self.fq_path = os.path.join(repo.path, self.rel_path) 


        if params:
            json.dump(params, open(self.fq_path, 'w'))
            repo.stage(self.rel_path)
            repo.do_commit('Updating entry {0} in {1}.'.format(index, git_table),
                    committer = 'Should have some session id here.')

    def getindex(self):
        return os.path.split(self.fq_path)[-1]

    def __str__(self):
        return self.getindex()

    def remove(self):
        os.remove(self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('removing', committer = 'Should have some session id here.')

    def _rename_file(self, git_table, new_index):
        new_rel_path = os.path.join(git_table, new_index)
        new_fq_path = os.path.join(repo.path, new_rel_path)
        os.rename(self.fq_path, new_fq_path)
        self.repo.stage(self.rel_path)
        self.fq_path = new_fq_path
        self.rel_path = new_rel_path

    def _del_property(self, key):
        data = json.load(open(self.fq_path))
        del data[key]
        json.dump(data, open(self.fq_path, 'w'))
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer = 'Should have some session id here.')

    def _get_property(self, key):
        data = json.load(open(self.fq_path))
        return data.get(key,None)

    def _set_property(self, key, value):
        data = json.load(open(self.fq_path))
        data[key] = value
        json.dump(data, open(self.fq_path, 'w'))
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer = 'Should have some session id here.')

class Player(GitEntry):
    """Class to manage a player with corresponding git file.""" 
    def __init__(self, repo, params=None, index=None):
        self.repo = repo

        if params:
            try:
                given_name = params['given_name']
                family_name = params['family_name']
            except KeyError:
                raise PlayerModError('Require given_name and family_name for every player.')

        if not index:
            index = u'{0}_{1}'.format(
                    params['given_name'], params['family_name']).encode('ascii', errors='egd')

        GitEntry.__init__(self, repo, params=params, git_table=PlayerList.path, index=index)



    def __unicode__(self):
        data = json.load(open(self.fq_path))
        rank = data.get('rank', 'No rank')
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)

    def _rename_file(self, given_name, family_name):
        new_index = u'{0}_{1}'.format(
                given_name, family_name).encode('ascii', errors='egd')
        GitEntry._rename_file(self, PlayerList.path, new_index)

    def __getitem__(self, key):
        return self._get_property(key)
    def __setitem__(self, key, value):
        if key == 'given_name':
            self._rename_file(value, self._get_property('family_name'))
        elif key == 'family_name':
            self._rename_file(self._get_property('given_name'), value)

        self._set_property(key, value)

    def __delitem__(self, key):
        if key == 'given_name':
            raise PlayerModError('Can not remove given_name from player.')
        elif key == 'family_name':
            raise PlayerModError('Can not remove family_name from player.')

        self._del_property(key)

class Pairing(GitEntry):
    """Class to manage a player with corresponding git file.""" 
    def __init__(self, repo, game_round=None, index=None, player1=None, player2=None):
        self.repo = repo
        params = None
        if not index:
            if not game_round:
                raise PairingModError('A pairing must have a game round.')
            if not player1 and not player2:
                raise PairingModError('A pairing must have at least one player')
            if not player1:
                player1 = player2
                player2 = None

            index = '{0}-{1}-{2}'.format(game_round, player1, player2)
            params ={'player1':player1, 'player2':player2, 'game_round':game_round}


        GitEntry.__init__(self, repo, params=params,
                git_table=PairingList.path, index=index)

    def __unicode__(self):
        data = json.load(open(self.fq_path))
        player1_index = data.get('player1')
        player2_index = data.get('player2')
        player1 = ''
        player2 = ''
        if player1_index:
            player1 = Player(self.repo,index=str(player1_index))
        if player2_index:
            player2 = Player(self.repo,index=str(player2_index))
#         rank = data.get('rank', 'No rank')
        return u'{0} vs {1}'.format(unicode(player1), unicode(player2))

    def _rename_file(self, game_round, player1, player2):
        new_index = '{0}-{1}-{2}'.format(game_round, player1, player2)
        GitEntry._rename_file(self, PairingList.path, new_index)

    def __getitem__(self, key):
        return self._get_property(key)
    def __setitem__(self, key, value):
        if key == 'game_round':
            self._rename_file(value, self['player1'], self['player2'])
        elif key == 'player1':
            if isinstance(value, Player):
                value = value.getindex()

            self._rename_file(self['game_round'], value, self['player2'])
        elif key == 'player2':
            if isinstance(value, Player):
                value = value.getindex()

            self._rename_file(self['game_round'], self['player1'], value)

        self._set_property(key, value)
    def __delitem__(self, key):
        self._del_property(key)

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
            yield Player(repo, index=player)

    def __getitem__(self, index):
        if isinstance(index,str):
            return Player(self.repo, index=index)
        return None

    def append(self, params):
        Player(self.repo, params=params)

class PairingList(object):
    """Class managing a git repository with a list of pairings."""
    path = 'pairings'

    def __init__(self, repo):
        self.repo = repo
        self.fq_pairingdir_path = os.path.join(repo.path, PairingList.path)
        if not os.path.isdir(self.fq_pairingdir_path):
            os.mkdir(self.fq_pairingdir_path)

    def __len__(self):
        return len(os.listdir(self.fq_pairingdir_path))

    def __iter__(self):
        for pairing in os.listdir(self.fq_pairingdir_path):
            yield Pairing(repo, index=pairing)

    def append(self, params):
        try:
            game_round = params['game_round']
        except KeyError:
            raise PairingModError('Can not add pairing with no game round specified.')
        player1 = params.get('player1')
        player2 = params.get('player2')

        Pairing(self.repo, game_round=game_round, player1=player1, player2=player2)

if __name__ == "__main__":
    try:
        repo = Repo('/data/lindroos/pybaduk/turn')
    except dulwich.errors.NotGitRepository, error:
        os.mkdir('/data/lindroos/pybaduk/turn')
        repo = Repo.init("/data/lindroos/pybaduk/turn")

    players = PlayerList(repo)
    if len(players) == 0:
        players.append({'given_name': u'Robert', 'family_name': u'Åhs'})
        players.append({'given_name': u'Eskil', 'family_name': u'Varenius', 'rank': '4K'})
        players.append({'given_name': u'Lukas', 'family_name': u'Lindroos', 'rank': '6K'})
        players.append({'given_name': u'Erik', 'family_name': u'Änterhake'})
        players.append({'given_name': u'Magnus', 'family_name': u'Sandén', 'rank': '7K'})
        players.append({'given_name': u'Niklas', 'family_name': u'Örjansson'})

    pairinglist = PairingList(repo)
    if len(pairinglist) == 0:
        pairinglist.append({'game_round':1, 'player1': 'Magnus_Sanden', 'player2': 'Eskil_Varenius'})
        pairinglist.append({'game_round':1, 'player1': 'Lukas_Lindroos'})

    for player in players:
        if player['given_name'] == 'Eskil':
            player.remove()
    
    for player in sorted(list(players), key=lambda player: player['family_name']):
        print unicode(player)
