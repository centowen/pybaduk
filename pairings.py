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
import json

from git import GitEntry
from players import Player, generate_player_filename


class PairingModError(Exception):
    pass


def _generate_filename(params):

    player1 = generate_player_filename(params['Player 1'])
    player2 = generate_player_filename(params['Player 2'])
    return u'{0}-{1}-{2}'.format(player1, player2,
                                 params['Group']).encode('ascii', errors='egd')


class Pairing(GitEntry):
    """Class to manage a pairing between two teams."""

    required_fields = [u'Player 1', u'Player 2', u'Group']

    def __init__(self, repo, params=None, index=None, *args, **kwargs):

        self.repo = repo

        if params:
            for field in Pairing.required_fields:
                if field not in params:
                    raise PairingModError(
                        'Required field {0} missing.'.format(field))
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
        if key == u'Player 1' or key == u'Player 2':
            return Player(self.repo, index = super(Pairing, self).__getitem__(key))
        else:
            return super(Pairing, self).__getitem__(key)

    def __delitem__(self, key):
        super(Pairing, self).__delitem__(key)

    def serialize(self, data):
        data = data.copy()
        data[u'Player 1'] = data[u'Player 1'].getindex()
        data[u'Player 2'] = data[u'Player 2'].getindex()
        return data

    def __eq__(self, other):
        return self.pairing_index == other.pairing_index
    
    def __hash__(self):
        return hash(self.pairing_index)


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
            yield Pairing(self.repo, index=filename)

    def append(self, params):
        return Pairing(self.repo, params=params)

    def __contains__(self, pairing):
        for p in self:
            if p == pairing:
                return True
        return False

    def __getitem__(self, index):
        return Pairing(self.repo, index=index)

