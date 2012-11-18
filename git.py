import os.path
import json


class GitLoadError(Exception):
    pass


class GitEntry(object):
    def __init__(self, repo, params=None, git_table=None, index=None):
        super(GitEntry, self).__init__()
        self.repo = repo
        # Checks like this aren't very pythonic:
        # Think duck typing: Anything that supports the subset of str interface
        # that we use here should be supported by this class. For example
        # unicode strings
        #if not isinstance(git_table, str):
        #    raise GitLoadError('Invalid git_table (players, pairings, etc...)'
        #                       'specified.')
        #elif not isinstance(index, str):
        #    raise GitLoadError('Invalid index (filename) specified: "{0}".'
        #                       .format(index))

        self.rel_path = os.path.join(git_table, index)
        self.fq_path = os.path.join(repo.path, self.rel_path) 

        if params:
            json.dump(params, open(self.fq_path, 'w'))
            repo.stage(self.rel_path)
            repo.do_commit('Updating entry {0} in {1}.'.format(index, git_table),
                    committer = 'Should have some session id here.')

    def getindex(self):
        return os.path.split(self.fq_path)[-1]

    def __str__(self):
        return self.getindex()

    def remove(self):
        os.remove(self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('removing', committer = 'Should have some session id here.')

    def _rename_file(self, git_table, new_index):
        new_rel_path = os.path.join(git_table, new_index)
        new_fq_path = os.path.join(self.repo.path, new_rel_path)
        os.rename(self.fq_path, new_fq_path)
        self.repo.stage(self.rel_path)
        self.fq_path = new_fq_path
        self.rel_path = new_rel_path

    def __delitem__(self, key):
        data = json.load(open(self.fq_path))
        del data[key]
        json.dump(data, open(self.fq_path, 'w'))
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer = 'Should have some session id here.')

    def __getitem__(self, key):
        data = json.load(open(self.fq_path))
        return data.get(key, None)

    def __setitem__(self, key, value):
        data = json.load(open(self.fq_path))
        data[key] = value
        json.dump(data, open(self.fq_path, 'w'))
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer = 'Should have some session id here.')
