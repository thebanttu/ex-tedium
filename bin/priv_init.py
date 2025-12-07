#!/usr/bin/python3

# Automatically add the ex-tedium lib directory to Python path
import os, sys

# Get the directory where this script is located (bin/)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level to ex-tedium root, then into lib/
lib_dir = os.path.join(os.path.dirname(script_dir), 'lib')

# Add to Python path if not already there
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)
