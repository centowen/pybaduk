import os.path
import json

from git import GitEntry


def _generate_filename(params):
    return u'{0}_{1}'.format(params['given_name'],
        params['family_name']).encode('ascii', errors='egd')


class PlayerModError(Exception):
    pass


class Player(GitEntry):
    """Class to manage a player with corresponding git file.""" 

    # TODO: Perhaps should be called req_field_names instead since
    # type is not included here but now instead constructed in 
    # get_player_fields.
    required_fields = [u'given_name', u'family_name', u'rank']

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
        data = json.load(open(self.fq_path))
        rank = data['rank']
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)

    def __str__(self):
        return unicode(self).encode('ascii', 'egd')

    def _rename_file(self, given_name, family_name):
        new_index = u'{0}_{1}'.format(
                given_name, family_name).encode('ascii', errors='egd')
        GitEntry._rename_file(self, PlayerList.path, new_index)

    def get_extra_fields(self):
        extra_fields = []
        fields = super(Player, self).items()
        for name, value in fields:
            if name in Player.required_fields:
                continue
            else:
                extra_fields.append((name, type(value)))

        return extra_fields

    def get(self, field, default=None):
        return super(Player, self).get(field, default)

    def __getitem__(self, field):
        return super(Player, self).__getitem__(field)

    def __setitem__(self, field, value):
        if field == 'given_name':
            self._rename_file(value, self['family_name'])
        elif field == 'family_name':
            self._rename_file(self['given_name'], value)
        super(Player, self).__setitem__(field, value)

    def __delitem__(self, field):
        if field in Player.required_fields:
            raise PlayerModError(
                'Can not remove required field {0}.'.format(field))
        super(Player, self).__delitem__(field)

    def __eq__(self, other):
        """Compare players by index."""
        return self.player_index == other.player_index


class PlayerList(object):
    """Class managing a git repository with a list of players."""

    path = 'players'

    def __init__(self, repo, *args, **kwargs):
        super(PlayerList, self).__init__(*args, **kwargs)
        self.repo = repo
        self.fq_playerdir_path = os.path.join(repo.path, PlayerList.path)
        if not os.path.isdir(self.fq_playerdir_path):
            os.mkdir(self.fq_playerdir_path)

    def __getitem__(self, i):
        for j, filename in enumerate(os.listdir(self.fq_playerdir_path)):
            if i == j:
                return Player(self.repo, index=filename)

    def append(self, params):
        p = Player(self.repo, params=params)
        return p.player_index

    def __len__(self):
        return len(os.listdir(self.fq_playerdir_path))

    def __iter__(self):
        for filename in os.listdir(self.fq_playerdir_path):
            yield Player(self.repo, index=filename)
