import os.path
import json

from git import GitEntry
from players import Player


class PairingModError(Exception):
    pass


def _generate_filename(params):

    team1 = '_'.join(params['team1'])
    team2 = '_'.join(params['team2'])

    return '{0}-{1}'.format(team1, team2)


class Pairing(GitEntry):
    """Class to manage a pairing between two teams."""
    def __init__(self, repo, in_params=None, index=None, *args, **kwargs):

        self.repo = repo
        params = None

        if in_params:
            params = in_params.copy()

            if not 'team1' in params and 'player1' in params:
                params['team1'] = [params['player1']]
            if not 'team2' in params and 'player2' in params:
                params['team2'] = [params['player2']]

            if 'player1' in params:
                del params['player1']
            if 'player2' in params:
                del params['player2']

            params['team1'] = [player.player_index 
                               for player in params['team1']]
            params['team2'] = [player.player_index 
                               for player in params['team2']]

            self.pairing_index = _generate_filename(params)

        elif index is not None:
            self.pairing_index = index
        else:
            raise ValueError('One of the keyword arguments params '
                             'or index is required.')

        super(Pairing, self).__init__(repo, params=params, 
                git_table=PairingList.path, filename=self.pairing_index,
                *args, **kwargs)

    def __getitem__(self, key):
        return super(Pairing, self).__getitem__(key)

    def __delitem__(self, key):
        super(Pairing, self).__delitem__(key)


class PairingList(object):
    """Class managing a git repository with a list of pairings."""

    path = 'pairings'

    def __init__(self, repo, path):
        self.repo = repo
        self.rel_pairingdir_path = path
        self.fq_pairingdir_path = os.path.join(self.repo.path, path)
        if not os.path.isdir(self.fq_pairingdir_path):
            os.mkdir(self.fq_pairingdir_path)

    def __len__(self):
        return len(os.listdir(self.fq_pairingdir_path))

    def __iter__(self):
        for filename in os.listdir(self.fq_pairingdir_path):
            yield Pairing(self.repo, path=self.rel_pairingdir_path, pairing_index=filename)

    def append(self, params):
        return Pairing(self.repo, in_params=params)

