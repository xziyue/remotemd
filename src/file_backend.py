import os
import json
from src.common_def import *
from src.common_def import _assert
import urllib
import html

class FileBackend:

    def __init__(self, filename):
        filename = os.path.abspath(filename)
        self.filename = filename
        self.check_file()

    def check_file(self):
        _assert(os.path.exists(self.filename), "file does not exist: " + self.filename)
        _assert(os.access(self.filename, os.W_OK), "no right to access file: " + self.filename)


    def read_file(self):
        self.check_file()
        with open(self.filename, 'r', encoding='utf8') as infile:
            data = infile.read()
        return data

    def update_file(self, jsonStr):
        val = json.loads(jsonStr)
        _assert('filename' in val and 'content' in val, 'invalid JSON response')
        unquoteFilename = html.unescape(val['filename'])
        _assert(self.filename == unquoteFilename, 'inconsistent filename: expected "{}", got "{}"'.format(self.filename, val['filename']))
        self.check_file()

        # read the file first
        with open(self.filename, 'r', encoding='utf8') as infile:
            backup = infile.read()

        outfile = open(self.filename, 'w', encoding='utf8')
        try:
            outfile.write(val['content'])
        except Exception:
            # try writing the old version...
            outfile.truncate(0)
            outfile.write(backup)
        outfile.close()
