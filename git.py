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
import pickle


class GitLoadError(Exception):
    pass


def load_file(filename):
    return pickle.load(open(filename, 'r'))


def dump_file(data, filename):
    pickle.dump(data, open(filename, 'w'))


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
            dump_file(self.serialize(params), self.fq_path)
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
        data = load_file(self.fq_path)
        return data.items()

    def __delitem__(self, key):
        data = load_file(self.fq_path)
        del data[key]
        dump_file(self.serialize(data), self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)

    def get(self, key, default=None):
        data = load_file(self.fq_path)
        return data.get(key, default)

    def __getitem__(self, key):
        data = load_file(self.fq_path)
        return data[key]

    def __setitem__(self, key, value):
        data = load_file(self.fq_path)
        data[key] = value
        dump_file(self.serialize(data), self.fq_path)
        self.repo.stage(self.rel_path)
        self.repo.do_commit('Modifying .', committer=self.session_id)

    def serialize(self, data):
        return data
