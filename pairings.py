import os.path
import json

from git import GitEntry


class PairingModError(Exception):
    pass


class Pairing(GitEntry):
    """Class to manage a pairing between two players."""
    def __init__(self, repo, game_round=None, index=None,
                 player1=None, player2=None):
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
        if player1_index:
            player1 = Player(self.repo, index=str(player1_index))
        if player2_index:
            player2 = Player(self.repo, index=str(player2_index))
        return u'{0} vs {1}'.format(unicode(player1), unicode(player2))

    def _rename_file(self, game_round, player1, player2):
        new_index = '{0}-{1}-{2}'.format(game_round, player1, player2)
        GitEntry._rename_file(self, PairingList.path, new_index)

    def __getitem__(self, key):
        return super(Pairing, self).__getitem__(key)

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
