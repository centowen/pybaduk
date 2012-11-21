import os.path
import json
import glob

from git import GitEntry


def _generate_filename(params):
    return u'{0}_{1}'.format(params['given_name'],
        params['family_name']).encode('ascii', errors='egd')


class PlayerModError(Exception):
    pass


class Player(GitEntry):
    """Class to manage a player with corresponding git file.""" 

    def __init__(self, repo, params=None, index=None):
        self.repo = repo

        if params:
            try:
                given_name = params['given_name']
                family_name = params['family_name']
            except KeyError:
                raise PlayerModError('Require given_name and family_name'
                                     'for every player.')
            self.player_index = _generate_filename(params)

        elif index is not None:
            self.player_index = index
            pass
        else:
            raise ValueError('One of the keyword arguments params '
                             'or index is required.')

        super(Player, self).__init__(repo, params=params,
              git_table=PlayerList.path, filename=self.player_index)

    def __unicode__(self):
        data = json.load(open(self.fq_path))
        rank = data.get('rank', 'No rank')
        given_name = data['given_name']
        family_name = data['family_name']
        return u'{0} {1} ({2})'.format(given_name, family_name, rank)

    def __str__(self):
        return unicode(self).encode('ascii', 'egd')

    def _rename_file(self, given_name, family_name):
        new_index = u'{0}_{1}'.format(
                given_name, family_name).encode('ascii', errors='egd')
        GitEntry._rename_file(self, PlayerList.path, new_index)

    def __getitem__(self, key):
        return super(Player, self).__getitem__(key)

    def __setitem__(self, key, value):
        if key == 'given_name':
            self._rename_file(value, self['family_name'])
        elif key == 'family_name':
            self._rename_file(self['given_name'], value)
        super(Player, self).__setitem__(key, value)

    def __delitem__(self, key):
        if key == 'given_name':
            raise PlayerModError('Can not remove given_name from player.')
        elif key == 'family_name':
            raise PlayerModError('Can not remove family_name from player.')
        super(Player, self).__delitem__(key)


class PlayerList(object):
    """Class managing a git repository with a list of players."""

    path = 'players'

    def __init__(self, repo):
        super(PlayerList, self).__init__()
        self.repo = repo
        self.fq_playerdir_path = os.path.join(repo.path, PlayerList.path)
        if not os.path.isdir(self.fq_playerdir_path):
            os.mkdir(self.fq_playerdir_path)

    def append(self, params):
        p = Player(self.repo, params=params)
        return p.player_index

    def __len__(self):
        return len(os.listdir(self.fq_playerdir_path))

    def __iter__(self):
        for filename in os.listdir(self.fq_playerdir_path):
            yield Player(self.repo, index=filename)
