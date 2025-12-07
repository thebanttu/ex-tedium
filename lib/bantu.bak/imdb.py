#!/usr/bin/env python3

from bantu.utils import bantu_utils as bu
import sys
if not bu.is_installed("imdb"):
    bu.install("IMdbPy")
from imdb import Cinemagoer, IMDbError
#, IMDb

class BantuImdbError(IMDbError):
    pass

class bantu_imdb:
    def __init__(self):
        bu.internet()
        self.im = Cinemagoer()
        #self.im = IMDb()

    def imdb_do(self, v, t, arg='', info=None):
        action = getattr(self.im, v + "_" + t)
        if len(arg) == 0:
            raise BantuImdbError(
                f"Provide a thing for {action} to operate on.")
        try:
            if info is not None:
                result = action(arg, info)
            else:
                result = action(arg)
        except IMDbError as e:
            print(e)
            sys.exit(2)

        return result
