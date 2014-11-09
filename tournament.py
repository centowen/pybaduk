# The GNU General Public License is a free, copyleft license for
# software and other kinds of works.
# 
# The licenses for most software and other practical works are designed
# to take away your freedom to share and change the works. By contrast,
# the GNU General Public License is intended to guarantee your freedom
# to share and change all versions of a program--to make sure it remains
# free software for all its users. We, the Free Software Foundation, use
# the GNU General Public License for most of our software; it applies
# also to any other work released this way by its authors. You can apply
# it to your programs, too.
# 
# When we speak of free software, we are referring to freedom, not
# price. Our General Public Licenses are designed to make sure that you
# have the freedom to distribute copies of free software (and charge for
# them if you wish), that you receive source code or can get it if you
# want it, that you can change the software or use pieces of it in new
# free programs, and that you know you can do these things.
# 
# To protect your rights, we need to prevent others from denying you
# these rights or asking you to surrender the rights. Therefore, you
# have certain responsibilities if you distribute copies of the
# software, or if you modify it: responsibilities to respect the freedom
# of others.
# 
# For example, if you distribute copies of such a program, whether
# gratis or for a fee, you must pass on to the recipients the same
# freedoms that you received. You must make sure that they, too, receive
# or can get the source code. And you must show them these terms so they
# know their rights.
# 
# Developers that use the GNU GPL protect your rights with two steps:
# (1) assert copyright on the software, and (2) offer you this License
# giving you legal permission to copy, distribute and/or modify it.
# 
# For the developers' and authors' protection, the GPL clearly explains
# that there is no warranty for this free software. For both users' and
# authors' sake, the GPL requires that modified versions be marked as
# changed, so that their problems will not be attributed erroneously to
# authors of previous versions.
# 
# Some devices are designed to deny users access to install or run
# modified versions of the software inside them, although the
# manufacturer can do so. This is fundamentally incompatible with the
# aim of protecting users' freedom to change the software. The
# systematic pattern of such abuse occurs in the area of products for
# individuals to use, which is precisely where it is most unacceptable.
# Therefore, we have designed this version of the GPL to prohibit the
# practice for those products. If such problems arise substantially in
# other domains, we stand ready to extend this provision to those
# domains in future versions of the GPL, as needed to protect the
# freedom of users.
# 
# Finally, every program is threatened constantly by software patents.
# States should not allow patents to restrict development and use of
# software on general-purpose computers, but in those that do, we wish
# to avoid the special danger that patents applied to a free program
# could make it effectively proprietary. To prevent this, the GPL
# assures that patents cannot be used to render the program non-free.
# 
# The precise terms and conditions for copying, distribution and
# modification follow.
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
