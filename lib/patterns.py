#!/usr/bin/env python3

import re

class bantu_patterns:
    ptrn = {
        "tv_pattern": re.compile(r"""
        ^
        (?P<show>[a-zA-Z1-9\.\-]+[^\.])
        \.[Ss]?(?P<season>\d{1,2})[EeXx](?P<episode>\d{1,2})
        (\.(?P<title>[a-zA-Z1-9\.]+[^\.]))?
        \.(?P<resolution>\d{3,4}p)
        \.(?P<quality>[a-zA-Z\-]{1,6})
        \.(?P<codec>[a-zA-Z0-9\.]+\d)
        ([\.\-](?P<team>.+))?
        $
        """, re.X),
        "movie_pattern": re.compile(r"""
        ^
        (?P<title>.+?)[. ](?P<year>\d{4})
        (?:[._ ](?P<release>UNRATED|REPACK|INTERNAL|PROPER|LIMITED|RERiP))*
        (?:[._ ](?P<format>480p|576p|720p|1080p|1080i|2160p))?
        (?:[._ ](?P<srctag>[a-z]{1,9}))?
        (?:[._ ](?P<source>BDRip|BRRip|HDRip|DVDRip|DVD[59]?|PAL|NTSC|Web|WebRip|WEB-DL|Blu-ray|BluRay|BD25|BD50))?
        (?:[._ ](?P<sound1>MP3|DD.?[25]\.[01]|AC3|AAC(?:2.0)?|FLAC(?:2.0)?|DTS(?:-HD)?))?
        (?:[._ ](?P<codec>xvid|divx|avc|x264|h\.?264|hevc|h\.?265))
        (?:[._ ](?P<sound2>MP3|DD.?[25]\.[01]|AC3|AAC(?:2.0)?|FLAC(?:2.0)?|DTS(?:-HD)?))?
        (?:[-.](?P<group>.+?))
        (?P<extension>\.avi|\.mkv|\.mp4|\.m4v)?
        $
        """ , flags=re.I | re.X)
    }
