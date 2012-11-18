import os.path
import json


class GitLoadError(Exception):
    pass


class GitEntry(object):
    def __init__(self, repo, git_table, filename, params=None):
        super(GitEntry, self).__init__()
        self.repo = repo
        self.session_id = '1337'

        self.rel_path = os.path.join(git_table, filename)
        self.fq_path = os.path.join(repo.path, self.rel_path) 

        if params:
            json.dump(params, open(self.fq_path, 'w'))
            repo.stage(self.rel_path)
            repo.do_commit('Updating entry {0} in {1}.'.format(
                filename, git_table), committer=self.session_id)

    def getindex(self):
        return os.path.split(self.fq_path)[-1]

    def __str__(self):
        return self.getindex()

    def remove(self):
        os.remove(self.fq_path)
        self.repo.stage(self.rel_path)
        commit_msg = 'Removing {} {}'.format(type(self).__name__.lower(), self)
        self.repo.do_commit(commit_msg, committer=self.session_id)

    def _rename_file(self, git_table, new_index):
        new_rel_path = os.path.join(git_table, new_index)
        new_fq_path = os.path.join(repo.path, new_rel_path)
        commit_msg = 'Renaming file {} to {}'.format(self.rel_path, new_rel_path)
        os.rename(self.fq_path, new_fq_path)
        #TODO: Staging the file that will be removed doesn't do anything.
        #      We need to find the equivalent of 'git rm file'
        self.repo.stage(self.rel_path)
        self.repo.stage(new_rel_path)
        self.fq_path = new_fq_path
        self.rel_path = new_rel_path
        self.repo.do_commit(commit_msg, committer=self.session_id)

    def __delitem__(self, key):
        data = json.load(open(self.fq_path))
        del data[key]
        json.dump(data, open(self.fq_path, 'w'))
        #TODO: Staging the file that will be removed doesn't do anything.
        #      We need to find the equivalent of 'git rm file'
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)

    def __getitem__(self, key):
        data = json.load(open(self.fq_path))
        return data.get(key, None)

    def __setitem__(self, key, value):
        data = json.load(open(self.fq_path))
        data[key] = value
        json.dump(data, open(self.fq_path, 'w'))
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)
