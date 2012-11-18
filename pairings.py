import os.path
import json
import glob

from git import GitEntry
from players import Player


class PairingModError(Exception):
    pass


class Pairing(GitEntry):
    """Class to manage a pairing between two players."""
    def __init__(self, repo, path, pairing_index=None,
                 p1_index=None, p2_index=None):
        self.repo = repo

        if pairing_index:
            filename = glob.glob1(os.path.join(repo.path, path),
                    '{}_*'.format(pairing_index))[0]
            self.index = pairing_index
            #TODO: Check for errors
            super(Pairing, self).__init__(repo, git_table=path,
                                          filename=filename)
        elif p1_index or p2_index:
            filenames = os.listdir(os.path.join(repo.path, path))
            old_indices = [int(filename.split('_')[0]) for filename in filenames]
            if old_indices:
                new_index = max(old_indices) + 1
            else:
                new_index = 0
            self.index = new_index

            if p1_index and p2_index:
                filename = '{}_{}_vs_{}'.format(self.index,
                        Player(repo, index=p1_index), Player(repo, index=p2_index))
            else:
                if not p1_index:
                    p1_index = p2_index
                    p2_index = None
                filename = '{}_{}_vs_{}'.format(self.index,
                        Player(repo, index=p1_index), 'None')
            params = {'p1_index': p1_index, 'p2_index': p2_index}
            super(Pairing, self).__init__(repo, params=params, git_table=path,
                                          filename=filename)
        else:
            raise PairingModError('A pairing must have at least one player or '
                                  'a pairing index.')

    def __unicode__(self):
        data = json.load(open(self.fq_path))
        p1_index = data['p1_index']
        p2_index = data['p2_index']
        player1 = Player(self.repo, index=p1_index)
        if p2_index:
            player2 = Player(self.repo, index=p2_index)
        else:
            player2 = 'None'
        return u'{0} vs {1}'.format(player1, player2)

    def _rename_file(self, game_round, player1, player2):
        new_index = '{0}-{1}-{2}'.format(game_round, player1, player2)
        GitEntry._rename_file(self, PairingList.path, new_index)

    def __getitem__(self, key):
        return super(Pairing, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key == 'game_round':
            self._rename_file(value, self['p1_index'], self['player2'])
        elif key == 'p1_index':
            if isinstance(value, Player):
                value = value.getindex()
            self._rename_file(self['game_round'], value, self['player2'])
        elif key == 'player2':
            if isinstance(value, Player):
                value = value.getindex()
            self._rename_file(self['game_round'], self['p1_index'], value)

        super(Pairing, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(Pairing, self).__delitem__(key)


class PairingList(object):
    """Class managing a git repository with a list of pairings."""

    def __init__(self, repo, path):
        self.repo = repo
        self.rel_pairingdir_path = path
        self.fq_pairingdir_path = os.path.join(repo.path, path)

        if not os.path.isdir(self.fq_pairingdir_path):
            os.mkdir(self.fq_pairingdir_path)

    def __len__(self):
        return len(os.listdir(self.fq_pairingdir_path))

    def __iter__(self):
        for filename in os.listdir(self.fq_pairingdir_path):
            yield Pairing(self.repo, self.rel_pairingdir_path,
                    pairing_index=filename.split('_')[0])

    def append(self, p1_index=None, p2_index=None):
        Pairing(self.repo, self.rel_pairingdir_path,
                p1_index=p1_index, p2_index=p2_index)
