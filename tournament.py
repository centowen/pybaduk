import os.path

from dulwich.repo import Repo
import dulwich.errors

import players
import pairings
import codecs
import egdcodec
from git import GitEntry


class Field(object):
    def __init__(self, name, datatype, visible=True, default=None):
        self.name = name
        self.datatype = datatype
        self.visible = visible
        self.default = default

    def __eq__(self, other):
        return self.name == other.name


class RemovePlayerError(Exception):
    """Exception raised when trying to delete a player exists in pairings.
    
    The relevant pairings can be found in the list: pairings."""

    def __init__(self, message, pairings, *args, **kwargs):
        super(RemovePlayerError, self).__init__(message, *args, **kwargs)
        self.pairings = pairings


class TournamentConfig(GitEntry):
    def __init__(self, repo, name, *args, **kwargs):
        self.repo = repo
        filename = 'tournament.conf'

        if not os.path.isfile(os.path.join(repo.path, filename)):
            params = {
                    'name': name,
                    'player_fields': [Field(u'Given name', 'text'),
                                      Field(u'Family name', 'text'),
                                      Field(u'Rank', 'rank')],
                    'tournament_type': 'dummy_lottning'}
        else:
            params = None

        super(TournamentConfig, self).__init__(
            repo, params=params, git_table='.',
            filename=filename, *args, **kwargs)

        self['tournament_type'] = os.path.basename(self['tournament_type'])
        print 'plugins.' + self['tournament_type']

        import importlib
        mod = importlib.import_module('.'+self['tournament_type'], 'plugins')
        self.tournament_type = mod.TournamentType()


class Tournament(object):
    """Manages a tournament and its players, pairings and results."""

    def __init__(self, path, name, *args, **kwargs):
        try:
            #TODO: Should this be done here? Or at all?
            name = name.encode('ascii', 'egd')
        except AttributeError:
            pass

        self.repopath = os.path.join(path, name)
        try:
            repo = Repo(self.repopath)
            #TODO: Check that there is an tournament.conf file
        except dulwich.errors.NotGitRepository:
            if not os.path.isdir(self.repopath):
                os.mkdir(self.repopath)
            repo = Repo.init(self.repopath)

        self.config = TournamentConfig(repo, name)
        self._players = players.PlayerList(repo)
        #if not os.path.isdir(os.path.join(self.repopath, 'pairings')):
        #    os.mkdir(os.path.join(self.repopath, 'pairings'))
        #TODO: Obso1337 code

        path = 'pairings'
        self._pairings = pairings.PairingList(repo, path)

        #for game_round in range(game_rounds):
        #    path = os.path.join('pairings', 'round{}'.format(game_round))
        #    self._pairings.append(pairings.PairingList(repo, path))

    def add_player_field(self, field):
        """Add a field to each player."""
        if field in self.config['player_fields']:
            raise KeyError((u'Field name {0} already exists in players '
                            u'table.').format(field.name))

        #TODO: Create a special class for self.config['player_fields']
        temp = self.config['player_fields']
        self.config['player_fields'] = temp + [field]
        for player in self._players:
            # Set field value to default for this type
            player[field.name] = field.default

    def remove_player_field(self, fieldname):
        """Remove a field from each player."""
        for i, field in enumerate(self.config['player_fields']):
            if field.name == fieldname:
                #TODO: Create a special class for self.config['player_fields']
                temp = self.config['player_fields']
                del temp[i]
                self.config['player_fields'] = temp
                break
        else:
            raise KeyError((u"Field name {0} doesn't exists in players "
                            u"table.").format(fieldname))

        for player in self._players:
            del player[fieldname]

    def get_player_fields(self):
        """Return a list of player fields."""
        return self.config['player_fields']

    def add_player(self, params):
        for field in self.config['player_fields']:
            if field.name not in params:
                params[field.name] = field.default
        index = self._players._append(params)
        return self._players[index]

    def add_pairing(self, params):
        self._pairings.append(params)

    def remove_player(self, player):
        """Tries to remove a player.
        
        Raises RemovePlayerError if the player exists in any pairings."""
        # pairings = []
        # for round_ in self._pairings:
        #     for pairing in round_:
        #         if (pairing['player1'] == player.player_index or
        #                 pairing['player2'] == player.player_index):
        #             pairings.append(pairing)
        # if pairings:
        #     raise RemovePlayerError("Remove pairings before removing player.",
        #                             pairings)

        player.remove()

    def remove_pairing(self, pairing):
        pairing.remove()

    @property
    def pairings(self):
        return self._pairings

    @property
    def players(self):
        return self._players
