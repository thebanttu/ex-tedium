#!/usr/bin/env python3

from bantu.utils import bantu_utils as bu
from bantu.utils import os, re, subprocess, sys
from pprint import pprint as pp
if not bu.is_installed("youtube_search"):
    bu.install("youtube-search")
from youtube_search import YoutubeSearch
if not bu.is_installed("yt_dlp"):
    bu.install("yt-dlp")
from yt_dlp import YoutubeDL
bu.internet()
yt_url = 'https://youtube.com'

class yt_opts:
    opts = {
        "continuedl": True,
        "format_sort": {
            "res": 720,
        },
        "paths": {
            "home": os.path.expanduser('~/Videos/Downloads'),
            "temp": os.path.expanduser('~/.local/tmp'),
        },
    }

class bantu_yt_search:
    @staticmethod
    def search(s, max=18):
        results = YoutubeSearch(s, max_results=max).to_dict()
        return results

    @staticmethod
    def display_search_results(r):
        c = 1; s = ''
        s = s + '{count:<3} {title:<55} {channel:<20} {duration:<10} {publish_time}'
        print(s.format(
            count='', title='Title', channel='Channel',
            duration='Duration', publish_time='Publish Time'))
        for result in r:
            title = result['title']; channel = result['channel']
            if len(title) > 55:
                result['title'] = title[:52] + '...'
            if len(channel) > 20:
                result['channel'] = channel[:17] + '...'
            print(s.format(count=str(c)+'.', **result))
            c += 1
        return

    @staticmethod
    def search_dwim(s, max=18):
        r = __class__.search(s)
        __class__.display_search_results(r)
        return r

    @staticmethod
    def choose_video(r):
        l = len(r)
        while True:
            try:
                choice = input("Select video >>> ")
                if re.match(r'[Qq]', choice):
                    sys.exit(11)
                if not re.match(r'\d+', choice):
                    raise ValueError
                if not int(choice) > 0 and int(choice) < l + 1:
                    raise RuntimeError
                break
            except ValueError:
                print("Invalid input (only numbers and q permitted), try again.")
                continue
            except RuntimeError:
                print(f"Invalid input, enter a number between 1 and {l}.")
                continue
            except EOFError:
                sys.exit(12)
        return yt_url + r[int(choice) - 1]['url_suffix']

    @staticmethod
    def play_video(s):
        r = __class__.search(s)
        while True:
            __class__.display_search_results(r)
            v = __class__.choose_video(r)
            cmd = ['mpv', v]
            subprocess.run(cmd, capture_output=True)
        return

    @staticmethod
    def download_video(s):
        """TODO: Add options to configure
        yt-dlp a little better"""
        r = __class__.search(s)
        while True:
            __class__.display_search_results(r)
            v = __class__.choose_video(r)
            with YoutubeDL(yt_opts.opts) as ydl:
                ydl.download(v)
        return
