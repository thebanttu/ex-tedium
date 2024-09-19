#!/usr/bin/env python3

from bantu.utils import TimeoutError
from bantu.utils import bantu_utils as bu
from bantu.utils import marangi
from bantu.utils import re, os, pp, sys
from pprint import pprint as pp
if not bu.is_installed("git"):
    bu.install("GitPython")
from git import Repo
from git.exc import GitCommandError

class BantuGitException(RuntimeError):
    pass


class bantu_git_repo(Repo):
    def __init__(self, d, **kwargs):
        self.repo = super().__init__(d)

    @classmethod
    def get_repo(cls, d, **kwargs):
        """
        Check if the .git dir is present in the passed dir
        If it isn't call other method to initialize a repo
        in the dir.
        If a remote repo url has been passed (as a keyword
        argument) add the url as a remote for the repo as
        well.
        If the directory passed is either empty or doesn't
        exist clone the repo at the url.
        After you have a repo object return it to caller.
        """
        git_dir = os.path.join(
            os.path.expanduser(d), '.git')
        if os.path.exists(git_dir):
            return cls(d)
        else:
            d = os.path.expanduser(d)
            if 'url' in kwargs:
                if (not os.path.isdir(d) or bu.is_dir_empty(d)):
                    repo = cls.clone_repo(kwargs["url"], d)
                else:
                    repo = cls.init_repo(d, url=kwargs["url"])
            else:
                repo = cls.init_repo(d)
        return repo

    @classmethod
    def init_repo(cls, d, **kwargs):
        repo = super().init(d)
        if 'url' in kwargs:
            print(f"Repo url passed -> {kwargs['url']}")
            origin = repo.create_remote("origin", kwargs["url"])
            try:
                origin.fetch()
                print(f"Successfully completed fetch from repo {kwargs['url']}")
            except GitCommandError:
                print(f"{marangi.FAIL}"
                      f"Problem performing initial fetch from the remote ({kwargs['url']}), please verify access to your repo."
                      f"{marangi.ENDC}")
                sys.exit(11)
            if "main" in origin.refs:
                # Create local branch "main" from remote "main".
                repo.create_head("main", origin.refs.main)
            else:
                main = repo.create_head("main")
                repo.heads.main.checkout()
            # Set local "main" to track remote "main.
            repo.heads.main.set_tracking_branch(origin.refs.main)
            repo.heads.main.checkout()
            origin.pull()
        return repo

    @classmethod
    def clone_repo(cls, url, d):
        """
        Not too different from the get_repo method,
        the differences being that their arguments
        are swapped and clone_repo gets the repo
        directly from the url.
        """
        bu.internet(msg=f"Aborting clone from {url} on account of no active internet connection.")
        try:
            repo = super().clone_from(url, d)
        except GitCommandError:
            print(
                f"{marangi.FAIL}"
                f"Problem cloning the repo URL ({url}). Please confirm it exists and you have the necessary perms."
                f"{marangi.ENDC}"
            )
            sys.exit(11)
        return repo

    def modified_files(self):
        return [item.a_path
            for item in self.index.diff(None)]

    def my_untracked_files(self):
        return [f for f in self.untracked_files]

    def stage_untracked_files(self):
        self.index.add(self.untracked_files)
        return

    def stage_modified_files(self):
        self.index.add(self.modified_files())
        return

    def stage_files(self, f):
        self.index.add(f)
        return

    def head_index_diff(self):
        diff = self.index.diff(
            self.head.commit)
        return diff

    def show_untracked_files(self):
        if self.untracked_files:
            print("Untracked Files:")
            for f in self.untracked_files:
                print(f"  - {f}")
            print()
        return

    def show_modifications(self, diff=None):
        if not diff:
            if self.is_dirty():
                diff = self.index.diff(None)
            else:
                print("No new changes to show.")
                return
        m = [ (i.change_type, i.a_path) for i in diff ]
        if m:
            print("Modified Files:")
            for t, f in m:
                print("{0}:{1:<3}{2}".format(t, " ", f))
            print()
        return

    def show_changes(self, diff=None):
        print(f"Showing changes from repo at -> {self.working_tree_dir}")
        self.show_untracked_files()
        if diff:
            self.show_modifications(diff)
        else:
            self.show_modifications()

    def commit_changes(self, m):
        self.index.commit(m)
        return

    def pull_changes(self, r='origin'):
        remote = self.remote(r)
        f = remote.url
        bu.internet(msg=f"{marangi.FAIL}Aborting pull from {f} on account of no active internet connection.{marangi.ENDC}")
        try:
            remote.pull()
        except GitCommandError:
            print(f"{marangi.FAIL}"
                  f"Problem pulling changes from the remote ({f}), please verify access to your repo."
                  f"{marangi.ENDC}")
            sys.exit(11)
        print(f"Repo {self.working_tree_dir} successfully pushed to {f}")
        return

    def push_changes(self, r='origin'):
        remote = self.remote(r)
        f = remote.url
        bu.internet(msg=f"{marangi.FAIL}Aborting push to {f} on account of no active internet connection.{marangi.ENDC}")
        try:
            remote.push()
        except GitCommandError:
            print(f"{marangi.FAIL}"
                  f"Problem pushing changes to the remote ({f}), please verify access to your repo."
                  f"{marangi.ENDC}")
            sys.exit(11)
        print(f"Repo {self.working_tree_dir} successfully pushed to {f}")
        return


    def repo_behind_remote(self, r='origin'):
        remote = self.remote(r)
        bu.internet(msg=f"{marangi.FAIL}Aborting fetch from {remote} on account of no active internet connection.{marangi.ENDC}")
        try:
            remote.fetch()
        except GitCommandError:
            print(f"{marangi.FAIL}"
                  f"Problem fetching from the remote ({remote.url}), please verify access to your repo."
                  f"{marangi.ENDC}")
            return False
        latest_remote_commit = remote.refs[self.active_branch.name].commit
        latest_local_commit = self.head.commit
        return latest_local_commit != latest_remote_commit

    def update_repo(self, msg=None, **kwargs):
        if self.is_dirty() or self.untracked_files:
            print(f"Updating repo at -> {self.working_tree_dir}")
            self.stage_untracked_files()
            self.stage_modified_files()
            self.commit_changes(msg)
        if self.repo_behind_remote():
            self.push_changes()
        else:
            print("Remote is up to date with your HEAD. Nothing to do.")
