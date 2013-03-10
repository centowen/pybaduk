import os.path
import json


class GitLoadError(Exception):
    pass


def json_load(filename):
    return json.load(open(filename, 'r'))


def json_dump(data, filename):
    json.dump(data, open(filename, 'w'), indent=4, sort_keys=True)


class GitEntry(object):
    def __init__(
            self, repo, git_table, filename,
            params=None, *args, **kwargs):
        super(GitEntry, self).__init__(*args, **kwargs)
        self.repo = repo
        self.session_id = '1337'

        self.rel_path = os.path.join(git_table, filename)
        self.fq_path = os.path.join(repo.path, self.rel_path) 

        if params:
            json_dump(params, self.fq_path)
            repo.stage(self.rel_path)
            repo.do_commit('Updating entry {0} in {1}.'.format(
                filename, git_table), committer=self.session_id)

    def getindex(self):
        return os.path.split(self.fq_path)[-1]

    def __str__(self):
        return self.getindex()

    def remove(self):
        commit_msg = 'Removing {} {}'.format(type(self).__name__.lower(), self)
        os.remove(self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit(commit_msg, committer=self.session_id)

    def _rename_file(self, git_table, new_index):
        new_rel_path = os.path.join(git_table, new_index)
        new_fq_path = os.path.join(self.repo.path, new_rel_path)
        commit_msg = 'Renaming file {} to {}'.format(self.rel_path, new_rel_path)
        os.rename(self.fq_path, new_fq_path)
        self.repo.stage(self.rel_path)
        self.repo.stage(new_rel_path)
        self.fq_path = new_fq_path
        self.rel_path = new_rel_path
        self.repo.do_commit(commit_msg, committer=self.session_id)

    def items(self):
        data = json_load(self.fq_path)
        return data.items()

    def __delitem__(self, key):
        data = json_load(self.fq_path)
        del data[key]
        json_dump(data, self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)

    def get(self, key, default=None):
        data = json_load(self.fq_path)
        return data.get(key, default)

    def __getitem__(self, key):
        data = json_load(self.fq_path)
        return data[key]

    def __setitem__(self, key, value):
        data = json_load(self.fq_path)
        data[key] = value
        json_dump(data, self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)
