#!/usr/bin/env python3

import bantu.utils
import os, re, subprocess, sys, time
import os.path as osp
from shutil import move
from bantu.utils import bantu_utils as bu
from bantu.patterns import bantu_patterns as bp
from pprint import pprint as pp

basket = osp.expanduser('~/Downloads/Basket')

class bantu_media:
    @staticmethod
    def check_movies(d):
        items = set()
        for parent, dirs, files in os.walk(d):
            for file in files:
                if os.path.isdir(file):
                    items += check_movies(file)
                if bp.ptrn.get("movie_pattern").match(file):
                    #print(f"{file} is movie like")
                    f = osp.join(parent, file).replace(d+'/', '') \
                        .split('/')[0]
                    items.add(f)
        print(f"Target candidate set -> {items}")
        return items

    @staticmethod
    def check_tv(d):
        items = set()
        for parent, dirs, files in os.walk(d):
            for file in files:
                if os.path.isdir(file):
                    items += check_tv(file)
                if bp.ptrn.get("tv_pattern").match(file):
                    #print(f"{file} is a tv show episode or closely related")
                    f = osp.join(parent, file).replace(d+'/', '') \
                        .split('/')[0]
                    items.add(f)
        print(f"Target candidate set -> {items}")
        return items

    @staticmethod
    def move_items_from_the_basket():
        m = __class__.check_movies(basket)
        dst = osp.expanduser("~/Videos/Movies")
        if len(m) > 0:
            for item in m:
                src = osp.join(basket, item)
                move(src, dst)
        t = __class__.check_tv(basket)
        dst = osp.expanduser("~/Videos/TV")
        if len(t) > 0:
            for item in t:
                src = osp.join(basket, item)
                move(src, dst)

    @staticmethod
    def sync_downloaded_media(s=None,host='zeus'):
        bu.internet()
        excludes = [
            osp.expanduser('~/.excludes/media.exclude.txt'),
        ]
        source_host = host
        prefix = source_host + ':.downloads/'
        destination = basket
        if len(s) == 0:
            source = prefix
        else:
            source = [ prefix + item + "*" for item in s ]
        c = bu.fetch(source, destination, ex=excludes)
        return c
