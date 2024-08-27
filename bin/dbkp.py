#!/usr/pkg/bin/python3

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
    home + '/.ssh/': \
    backup_target + 'bkp/ssh/',
    # disposable-bins
    home + '/disposable-bins/': \
    backup_target + 'bkp/disposable-bins/',
    # Books
    home + '/Books/': \
    backup_target + 'bkp/Books/',
    # Projects
    home + '/Projects/': \
    backup_target + 'bkp/Projects/',
    # Downloads
    home + '/Downloads/': \
    backup_target + 'bkp/Downloads/',
    # isos
    home + '/isos/': \
    backup_target + 'ISOs/',
    # Pictures
    home + '/Pictures/': \
    backup_target + 'bkp/Pictures/',
    # Music
    home + '/Music/': \
    backup_target + 'MUSIC/',
    # Movies
    'movies': {
        'files': [
            home + '/Videos/Movies/Lone Star (1996) [WEBRip] [720p] [YTS.LT]',
            home + '/Videos/Movies/Leon The Professional Extended (1994)',
            home + '/Videos/Movies/Clear and Present Danger (1994)',
            home + '/Videos/Movies/Body Heat (1981) [YTS.AG]',
            home + '/Videos/Movies/The Ref (1994) [720p] [WEBRip] [YTS.MX]',
        ],
        'target': backup_target + 'MOVIES/Goodies/',
    },
    # TV
    home + '/Videos/TV/House.Of.The.Dragon': \
    backup_target + 'SHAD/TVSHOWS/',
    # Research
    home + '/Videos/Research/': \
    backup_target + 'SHAD/Research/',
    # Documentaries
    home + '/Videos/Documentaries/': \
    backup_target + 'SHAD/Documentaries/',
    # Tech
    home + '/Videos/Tech/': \
    backup_target + 'SHAD/Tech/',
    # Clips
    home + '/Videos/clips/': \
    backup_target + 'SHAD/Clips/',
}

def create_backup_destination_tree():
    for d in sources_and_destinations.values():
        if type(d) is dict:
            d = d['target']
        if not os.path.exists(d):
            print(f"Creating directory -> {d}")
        os.makedirs(d, exist_ok=True)
    return

def sync_homedir_data():
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
    sync_homedir_data()
