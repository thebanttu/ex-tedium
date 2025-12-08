#!/usr/bin/python3

# Automatically add the ex-tedium lib directory to Python path
import os, sys

# Get the directory where this script is located (bin/)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine lib directory based on whether we're in ex-tedium or deployed to ~/bin
parent_dir = os.path.dirname(script_dir)
if os.path.basename(parent_dir) == 'ex-tedium':
    # Running from ex-tedium repo
    lib_dir = os.path.join(parent_dir, 'lib')
else:
    # Deployed to ~/bin, look for ex-tedium in home directory
    home = os.path.expanduser('~')
    lib_dir = os.path.join(home, 'ex-tedium', 'lib')

# Add to Python path if not already there
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)
