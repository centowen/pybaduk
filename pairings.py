import os.path
import json

from git import GitEntry
from players import Player


class PairingModError(Exception):
    pass


def _generate_index(p1_index, p2_index):
    return '{0}-{1}'.format(p1_index, p2_index)


class Pairing(GitEntry):
    """Class to manage a pairing between two players."""
    def __init__(self, repo, path, pairing_index=None,
                 p1_index=None, p2_index=None):
        self.repo = repo
        self.fq_path = path
        params = None
        if pairing_index:
            self.index = pairing_index
        else:
            if not p1_index and not p2_index:
                raise PairingModError('A pairing must have at least one player')
            if not p1_index:
                p1_index = p2_index
                p2_index = None

            params ={'player1': p1_index, 'player2': p2_index}
            self.index = _generate_index(p1_index, p2_index)

        GitEntry.__init__(self, repo, params=params,
                git_table=self.fq_path, filename=self.index)


    def __unicode__(self):
        data = json.load(open(self.fq_path))
        player1_index = data.get('player1')
        player2_index = data.get('player2')
        player1 = Player(self.repo, index=player1_index)
        if player2_index:
            player2 = Player(self.repo, index=player2_index)
        else:
            player2 = 'No one'
        return u'{0} vs {1}'.format(player1, player2)

    def _rename_file(self, game_round, player1, player2):
        new_index = '{1}-{2}'.format(player1, player2)
        GitEntry._rename_file(self, PairingList.path, new_index)

    def __getitem__(self, key):
        return super(Pairing, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key == 'player1':
            if isinstance(value, Player):
                value = value.getindex()

            self._rename_file(value, self['player2'])
        elif key == 'player2':
            if isinstance(value, Player):
                value = value.getindex()

            self._rename_file(self['player1'], value)

        self._set_property(key, value)

    def __delitem__(self, key):
        super(Pairing, self).__delitem__(key)


class PairingList(object):
    """Class managing a git repository with a list of pairings."""

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

    def append(self, player1, player2=None):
        try:
            p1_index = player1.player_index
        except AttributeError:
            p1_index = player1

        try:
            p2_index = player2.player_index
        except AttributeError:
            p2_index = player2

        Pairing(self.repo, path=self.rel_pairingdir_path, 
                p1_index=p1_index, p2_index=p2_index)
