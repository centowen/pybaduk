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

from git import GitEntry


def generate_player_filename(params):
    return u'{0}_{1}'.format(params['Given name'],
        params['Family name']).encode('ascii', errors='egd')


class PlayerModError(Exception):
    pass


class Player(GitEntry):
    """Class to manage a player with corresponding git file.""" 

    # TODO: Perhaps should be called req_field_names instead since
    # type is not included here but now instead constructed in 
    # get_player_fields.
    required_fields = [u'Given name', u'Family name']

    def __init__(self, repo, params=None, index=None, *args, **kwargs):
        self.repo = repo

        if params:
            for field in Player.required_fields:
                if field not in params:
                    raise PlayerModError(
                        'Required field {0} missing.'.format(field))
            self.player_index = generate_player_filename(params)
        elif index is not None:
            self.player_index = index
        else:
            raise ValueError('One of the keyword arguments params '
                             'or index is required.')

        super(Player, self).__init__(
            repo, params=params, git_table=PlayerList.path,
            filename=self.player_index, *args, **kwargs)

    def __unicode__(self):
        rank = self.get('Rank', default='No rank')
        given_name = self['Given name']
        family_name = self['Family name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)

    def __str__(self):
        return unicode(self).encode('ascii', 'egd')

    def _rename_file(self, given_name, family_name):
        new_index = u'{0}_{1}'.format(
                given_name, family_name).encode('ascii', errors='egd')
        self.player_index = new_index
        GitEntry._rename_file(self, PlayerList.path, new_index)

    def __setitem__(self, field, value):
        if field == 'Given name':
            self._rename_file(value, self['Family name'])
        elif field == 'Family name':
            self._rename_file(self['Given name'], value)
        super(Player, self).__setitem__(field, value)

    def __delitem__(self, field):
        if field in Player.required_fields:
            raise PlayerModError(
                'Can not remove required field {0}.'.format(field))
        super(Player, self).__delitem__(field)

    def __eq__(self, other):
        """Compare players by index."""
        return self.player_index == other.player_index

    def __hash__(self):
        """Build hash from index."""
        return hash(self.player_index)


class PlayerList(object):
    """Class managing a git repository with a list of players."""

    path = 'players'

    def __init__(self, repo, *args, **kwargs):
        super(PlayerList, self).__init__(*args, **kwargs)
        self.repo = repo
        self.fq_playerdir_path = os.path.join(repo.path, PlayerList.path)
        if not os.path.isdir(self.fq_playerdir_path):
            os.mkdir(self.fq_playerdir_path)

    def __getitem__(self, index):
        return Player(self.repo, index=index)

    def _append(self, params):
        p = Player(self.repo, params=params)
        return p.player_index

    def __len__(self):
        return len(os.listdir(self.fq_playerdir_path))

    def __iter__(self):
        for filename in os.listdir(self.fq_playerdir_path):
            yield Player(self.repo, index=filename)

    def __contains__(self, player):
        for p in self:
            if p == player:
                return True
        return False
