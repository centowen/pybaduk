import os.path

from dulwich.repo import Repo
import dulwich.errors

import players
import pairings


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

    @property
    def pairings(self):
        return self._pairings

    @property
    def players(self):
        return self._players
