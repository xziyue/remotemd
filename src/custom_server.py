from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
import os
from src.correct_path import htmlDir
import signal
import posixpath
import urllib


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
        self.fileBackend = kwargs['fileBackend']
        del kwargs['fileBackend']
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        # discard some output
        if code not in [304, 200]:
            super().log_request(code, size)

    def do_POST(self):
        words = self.path.split('/')
        try:
            if words[1] == 'save_content.do':
                # get content length
                contentLength = int(self.headers['Content-Length'])
                jsonStr = self.rfile.read(contentLength)
                print(jsonStr)
                self.send_response(HTTPStatus.OK, 'contents successully saved')
            else:
                raise RuntimeError('unknown target: ' + repr(words))

        except Exception as e:
            pass

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        words = path.split('/')
        words = list(filter(None, words))
        path = self.directory
        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path

class NewHS(HTTPServer):

    def __init__(self, ip, port, baseDir, fileBackend):
        self.baseDir = os.path.abspath(baseDir)
        os.chdir(self.baseDir)
        super().__init__((ip, port), NewHRH)

        self.fileBackend = fileBackend

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, fileBackend=self.fileBackend)


def run_server(ip, port, baseDir):

    # register signal
    signal.signal(signal.SIGINT, handle_sigint)

    httpd = NewHS(ip, port, baseDir, 'backend')
    sa = httpd.socket.getsockname()
    print('Starting HTTP server on {}:{}'.format(sa[0], sa[1]))

    httpd.serve_forever()


run_server('127.0.0.1', 8088, htmlDir)