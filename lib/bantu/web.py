#!/usr/bin/env python3

import webbrowser as wb
import urllib.parse

class bantu_web:
    @staticmethod
    def search_google(q):
        url = "https://google.com/search?q="
        query = url + urllib.parse.quote_plus(q)
        wb.open(query, new=1)

    @staticmethod
    def open_google():
        url = "https://google.com/"
        wb.open(url, new=1)
