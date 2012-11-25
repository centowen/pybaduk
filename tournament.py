import os.path

from dulwich.repo import Repo
import dulwich.errors

import players
import pairings
import codecs
import egdcodec


class RemovePlayerError(Exception):
    """Exception raised when trying to delete a player exists in pairings.
    
    The relevant pairings can be found in the list: pairings."""

    def __init__(self, message, pairings, *args, **kwargs):
        super(RemovePlayerError, self).__init__(message, *args, **kwargs)
        self.pairings = pairings


class Tournament(object):
    """Manages a tournament and its players, pairings and results."""

    def __init__(self, path, name, game_rounds=1):
        try:
            name = name.encode('ascii', 'egd')
        except AttributeError:
            pass

        self.repopath = os.path.join(path, name)
        try:
            repo = Repo(self.repopath)
        except dulwich.errors.NotGitRepository:
            if not os.path.isdir(self.repopath):
                os.mkdir(self.repopath)
            repo = Repo.init(self.repopath)

        self._players = players.PlayerList(repo)
        if not os.path.isdir(os.path.join(self.repopath, 'pairings')):
            os.mkdir(os.path.join(self.repopath, 'pairings'))
        self._pairings = []
        for game_round in range(game_rounds):
            path = os.path.join('pairings', 'round{}'.format(game_round))
            self._pairings.append(pairings.PairingList(repo, path))

    def add_player(self, params):
        self._players.append(params)

    def add_pairing(self, game_round, player1, player2=None):
        self._pairings[game_round].append(player1, player2)

    def remove_player(self, player):
        """Tries to remove a player.
        
        Raises RemovePlayerError if the player exists in any pairings."""
        pairings = []
        for round_ in self._pairings:
            for pairing in round_:
                if (pairing['player1'] == player.player_index or
                        pairing['player2'] == player.player_index):
                    pairings.append(pairing)
        if pairings:
            raise RemovePlayerError("Remove pairings before removing player.",
                                    pairing)

        player.remove()

    def remove_pairing(self, pairing):
        pairing.remove()

    @property
    def pairings(self):
        return self._pairings

    @property
    def players(self):
        return self._players
