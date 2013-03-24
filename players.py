import os.path

from git import GitEntry


def _generate_filename(params):
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
            self.player_index = _generate_filename(params)
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
