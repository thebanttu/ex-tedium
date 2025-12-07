#!/usr/bin/env python3

import os
import re
import sys

pattern = re.compile(
    r"^(?P<title>.+?)[. ](?P<year>\d{4})"
    r"(?:[._ ](?P<release>UNRATED|REPACK|INTERNAL|PROPER|LIMITED|RERiP))*"
    r"(?:[._ ](?P<format>480p|576p|720p|1080p|1080i|2160p))?"
    r"(?:[._ ](?P<srctag>[a-z]{1,9}))?"
    r"(?:[._ ](?P<source>BDRip|BRRip|HDRip|DVDRip|DVD[59]?|PAL|NTSC|Web|WebRip|WEB-DL|Blu-ray|BluRay|BD25|BD50))"
    r"(?:[._ ](?P<sound1>MP3|DD.?[25]\.[01]|AC3|AAC(?:2.0)?|FLAC(?:2.0)?|DTS(?:-HD)?))?"
    r"(?:[._ ](?P<codec>xvid|divx|avc|x264|h\.?264|hevc|h\.?265))"
    r"(?:[._ ](?P<sound2>MP3|DD.?[25]\.[01]|AC3|AAC(?:2.0)?|FLAC(?:2.0)?|DTS(?:-HD)?))?"
    r"(?:[-.](?P<group>.+?))"
    r"(?P<extension>\.avi|\.mkv|\.mp4|\.m4v)?$", re.I
)

d = os.environ.get('HOME') + '/Videos/Movies'
t = os.environ.get('HOME') + '/Videos/TV'

def check_movies(d):
    for parent, dirs, files in os.walk(d):
        for file in files:
            if os.path.isdir(file):
                check_movies(file)
            if pattern.match(file):
                print(f"{file} is a movie")

if __name__ == "__main__":
    check_movies(t)
