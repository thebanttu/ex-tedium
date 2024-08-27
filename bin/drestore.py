#!/usr/bin/python3

import priv_init
import bantu.utils
from bantu.utils import bantu_utils as bu
from bantu.utils import os, re, subprocess, sys, time
from os import access, R_OK, X_OK
from os.path import isfile
from pprint import pprint as pp

home = os.environ['HOME']
backup_target = '/mnt/usb/'
default_excludes = [
    home + '/.excludes/junk.txt',
]
"""
Backup configuration dict:
Typically the key is the source and the value the target.

In case one has a list of files already or extra exclude files are
present, use the alternate convention where one has an arbitrary key
and a dict as a value.

For a predetermined list of files, create a files key with a list
value containing the files.  For extra exclude file(s) create an
exclude key with a list value of the exclude files.
"""
sources_and_destinations = {
    # ssh
    # backup_target + 'bkp/ssh/': \
    # home + '/.ssh/',
    # disposable-bins
    backup_target + 'bkp/disposable-bins/': \
    home + '/disposable-bins/',
    # Books
    backup_target + 'bkp/Books/': \
    home + '/Books/',
    # Projects
    # backup_target + 'bkp/Projects/': \
    # home + '/Projects/',
    # Downloads
    backup_target + 'bkp/Downloads/': \
    home + '/Downloads/',
    # isos
    backup_target + 'ISOs/': \
    home + '/isos/',
    # Pictures
    backup_target + 'bkp/Pictures/': \
    home + '/Pictures/',
    # Music
    backup_target + 'MUSIC/': \
    home + '/Music/',
    # Movies
    'movies': {
        'files': [
            backup_target + 'MOVIES/Goodies/Calibre (2018) [WEBRip] [720p] [YTS.AM]',
            backup_target + 'MOVIES/Goodies/Leon The Professional Extended (1994)',
            backup_target + 'MOVIES/Goodies/Circle - Psychological Horror 2015 Eng Subs 720p [H264-mp4]',
            backup_target + 'MOVIES/Goodies/Murder.By.Numbers',
            backup_target + 'MOVIES/Goodies/Rounders.1998',
            backup_target + 'MOVIES/Goodies/Crimson.Tide.1995',
            backup_target + 'MOVIES/Goodies/Along Came A Spider (2001)',
        ],
        'target': home + '/Videos/Movies/',
    },
    # TV
    # backup_target + 'SHAD/TVSHOWS/': \
    # home + '/Videos/TV/House.Of.The.Dragon',
    # Research
    backup_target + 'SHAD/Research/': \
    home + '/Videos/Research/',
    # Documentaries
    backup_target + 'SHAD/Documentaries/': \
    home + '/Videos/Documentaries/',
    # Tech
    backup_target + 'SHAD/Tech/': \
    home + '/Videos/Tech/',
    # Clips
    backup_target + 'SHAD/Clips/': \
    home + '/Videos/clips/',
}

def create_backup_destination_tree():
    for d in sources_and_destinations.values():
        if type(d) is dict:
            d = d['target']
        if not os.path.exists(d):
            print(f"Creating directory -> {d}")
        os.makedirs(d, exist_ok=True)
    return

def restore_homedir_data():
    #create_backup_destination_tree()
    for source, destination in sources_and_destinations.items():
        kwargs = {}
        if type(destination) is dict:
            if 'exclude' in destination:
                kwargs['ex'] = [ x for x in default_excludes ] + destination['exclude']
            else:
                kwargs['ex'] = default_excludes
            if 'files' in destination:
                source = destination['files']
            else:
                source = destination['source']
            destination = destination['target']
        else:
            kwargs['ex'] = default_excludes
        #kwargs['dry'] = 1
        #pp((source, destination, kwargs))
        bu.xrsync(source, destination, **kwargs)
    return

if __name__ == "__main__":
    restore_homedir_data()
