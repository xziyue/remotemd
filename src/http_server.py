from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
from src.correct_path import htmlDir
import signal


def handle_sigint(signal, frame):
    userInput = input('Do you want to terminate the server? (y/n)').lower()
    if len(userInput) > 0 and userInput[0] == 'y':
        exit(0)
    elif userInput[0] == 'n':
        print('Termination aborted')
    else:
        print('Invalid input, termination aborted')


class NewHRH(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        # discard some output
        if code not in [304, 200]:
            super().log_request(code, size)

def run_server(ip, port, baseDir):
    # chdir to the serving directory
    baseDir = os.path.abspath(baseDir)
    os.chdir(baseDir)

    httpd = HTTPServer((ip, port), NewHRH)
    sa = httpd.socket.getsockname()
    print('Starting HTTP server on {}:{}'.format(sa[0], sa[1]))

    # register signal
    signal.signal(signal.SIGINT, handle_sigint)

    # run server
    httpd.serve_forever()


run_server('127.0.0.1', 8088, htmlDir)

