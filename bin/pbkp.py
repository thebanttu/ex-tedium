#!/usr/bin/env python3

import priv_init
import bantu.utils
import os, re, subprocess, sys, time
from bantu.utils import bantu_utils as bu
from bantu.git import bantu_git_repo as bgr
from os import access, R_OK, X_OK
from os.path import isfile
from pprint import pprint as pp

home = os.environ.get('HOME')
backup_target = home + '/Projects/backup/env/'
python_version = "" + \
    f"{sys.version_info.major}." + \
    f"{sys.version_info.minor}"
default_excludes = [
    home + '/.excludes/junk.txt',
]
repos = {
    "env": "git@github.com:thebanttu/bantu-env.git",
    "notes": "git@gitlab.com:thebanttu/my-org.git",
    "extedium": "git@github.com:thebanttu/ex-tedium.git",
}
"""
Backup configuration dict:
Typically the key is the source and the value the target.

In case one has a list of files already or extra exclude files are
present, use the alternate convention where one has an arbitrary key
and a dict as a value.

For a predetermined list of files, create a files key with a list
value containing the files.  For extra exclude file(s) create an
exclude key with a list value of the exclude files.

The files key and the source key are mutually exclusive.
"""
sources_and_destinations = {
    # shell utils
    'bantu_env#' + home + '/bin/': \
    backup_target + 'bin/',
    # Bantu's python libs
    'bantu_env#' + home + '/Projects/code/python/private/bantu/': \
    backup_target + 'lib/',
    # emacs configs
    'emacs_configs': {
        'source': home + '/.emacs.d/',
        'target': backup_target + 'config/emacs/',
        'exclude': [
            home + '/.excludes/emacs.exclude.txt'
        ]
    },
    # my dotfiles
    'dotfiles': {
        'files': [
            home + '/.gitconfig',
            home + '/.rgignore',
            home + '/.rtorrent.rc',
            home + '/.tmux.conf',
            home + '/.vim',
            home + '/.xbindkeysrc',
            home + '/.xinitrc',
            home + '/.zshrc',
            home + '/.Xresources',
        ],
        'target': backup_target + 'config/dotfiles/',
    },
    # mpv configs
    home + '/.config/mpv/': \
    backup_target + 'config/mpv/',
    # package list
    home + '/.pkg-list.txt':
    backup_target + 'config/pkg/',
    # exclude lists (for use with rsync mostly)
    home + '/.excludes/': \
    backup_target + 'exclude',
    # ex-tedium bins
    'ex_tedium#' + home + '/bin/': \
    home + '/Projects/code/python/ex-tedium/bin',
    # ex-tedium libs
    'ex_tedium#' + home + '/Projects/code/python/private/bantu/': \
    home + '/Projects/code/python/ex-tedium/lib/bantu',
}

def create_backup_destination_tree():
    for d in sources_and_destinations.values():
        if type(d) is dict:
            d = d['target']
        if not os.path.exists(d):
            print(f"Creating directory -> {d}")
        os.makedirs(d, exist_ok=True)
    return

def sync_shell_utilities_and_configs():
    create_backup_destination_tree()
    for source, destination in sources_and_destinations.items():
        kwargs = {}
        if type(destination) is dict:
            if 'exclude' in destination:
                kwargs['ex'] = [ x for x in default_excludes ] + destination['exclude']
            else:
                kwargs['ex'] = default_excludes
            if 'files' in destination:
                source = [ f
                           for f in filter(
                               lambda f : isfile(f) and access(f, R_OK),
                               destination['files']) ]
            else:
                source = destination['source']
            destination = destination['target']
        else:
            kwargs['ex'] = default_excludes
            source = clean_source(source)
        #pp((source, destination, kwargs))
        bu.xrsync(source, destination, **kwargs)
    return

def clean_source(s) -> str:
    r = re.compile(r'^\w+#')
    sr = re.compile(r'^(?>\w*)#')
    if r.match(s):
        return re.split(sr, s)[1]
    else:
        return s

def make_commit_message():
    t = time.ctime()
    return f"Automatic backup check in done at {t}."

def sync_personal_bkp_repo():
    repo = bgr.get_repo(backup_target, url=repos["env"])
    sync_shell_utilities_and_configs()
    repo.show_changes()
    repo.update_repo(make_commit_message())
    return

def sync_notes_repo():
    d = "~/.Notes"
    repo = bgr.get_repo(d, url=repos["notes"])
    repo.show_changes()
    repo.update_repo(make_commit_message())
    return

def sync_ex_tedium_repo():
    d = '~/Projects/code/python/ex-tedium'
    repo = bgr.get_repo(d, url=repos["extedium"])
    repo.show_changes()
    repo.update_repo(make_commit_message())
    return

def sync_repo(d, u=None):
    if u:
        repo = bgr.get_repo(d, url=url)
    else:
        repo = bgr.get_repo(d)
    repo.show_changes()
    repo.update_repo(make_commit_message())
    return

if __name__ == "__main__":
    if sys.argv[0].endswith("pbkp.py"):
        sync_personal_bkp_repo()
        sync_notes_repo()
        sync_ex_tedium_repo()
