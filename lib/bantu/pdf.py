#!/usr/bin/env python3

from bantu.utils import TimeoutError
from bantu.utils import bantu_utils as bu
from bantu.utils import re, os, pp, sys
if not bu.is_installed("PyPDF2"):
    bu.install("PyPDF2")
from PyPDF2 import PdfReader

class bantu_pdf:
    def __init__(self, f):
        f = os.path.expanduser(f)
        self.reader = PdfReader(f)

    def get_text(self):
        p = 0
        for page in self.reader.pages:
            p += 1
            print(f"========== Page {p} ==========")
            print(page.extract_text())
