#!/usr/bin/python3

# IMPORTANT: change the dir path to where your
# cloned dir is located.
import os, sys
user = os.environ.get("USER")
dir = os.path.expanduser('~' + user + '/Projects/code/python/private')
sys.path.insert(0, dir)
