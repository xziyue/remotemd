from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
import os
from src.correct_path import htmlDir, projectDir
import signal
import posixpath
import urllib
from src.file_backend import FileBackend
from src.common_def import *
from src.common_def import _assert
import html

class NewHRH(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.fileBackend = self._fetch_kwargs(kwargs, 'fileBackend')
        self.baseDir = self._fetch_kwargs(kwargs, 'baseDir')
        self.remotemdCallback = self._fetch_kwargs(kwargs, 'remotemdCallback')
        super().__init__(*args, **kwargs)

    def _fetch_kwargs(self, dictionary, key):
        val = dictionary[key]
        del dictionary[key]
        return val

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
                # save the file
                self.fileBackend.update_file(jsonStr)
                self.send_response(HTTPStatus.OK, 'contents successully saved')
                self.flush_headers()
                print('Saved changes to ' + self.fileBackend.filename)
                #print('sent success response')
            else:
                raise RuntimeError('unknown target: ' + repr(words))

        except Exception as e:
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR, repr(e))
            self.flush_headers()
            print('Failed to save changes to {}:\n{}'.format(self.fileBackend.filename, repr(e)))
            #print('sent failure response')


    def do_GET(self):
        if self.path in ('/', ''):
            # check it it's trying to access the default page
            content = self.remotemdCallback()
            self.send_response(HTTPStatus.OK, 'default page generation successful')
            self.send_header("Content-type", 'text/html; charset=UTF-8')
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Last-Modified", self.date_time_string())
            self.end_headers()
            self.wfile.write(content.encode('utf8'))
        else:
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()



    # change directory mapping of editor.md files and how default dir is handled
    def translate_path(self, path):
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

        if len(words) > 0 and words[0] == 'editor.md':
            # redirect editor.md requests to our directory
            path = projectDir
        else:
            # leave the rest in source directory
            path = self.baseDir

        for word in words:
            if os.path.dirname(word) or word in (os.curdir, os.pardir):
                # Ignore components that are not a simple file/directory name
                continue
            path = os.path.join(path, word)


        if trailing_slash:
            path += '/'

        return path

    def send_response(self, code, message=None):
        """Add the response header to the headers buffer and log the
        response code.

        Also send two standard headers with the server software
        version and the current date.

        """
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string() + ' (modified for RemoteMD)')
        self.send_header('Date', self.date_time_string())


class NewHS(HTTPServer):

    def __init__(self, ip, port, baseDir, fileBackend, remotemdCallback):
        super().__init__((ip, port), NewHRH)
        self.baseDir = os.path.abspath(baseDir)
        self.fileBackend = fileBackend
        self.remotemdCallback = remotemdCallback

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, fileBackend=self.fileBackend, baseDir = self.baseDir,
                                 remotemdCallback=self.remotemdCallback)


class CustomServer:

    def __init__(self, ip, port, baseDir, sourceFilename, additionalHead=''):
        self.ip = ip
        self.port = port
        self.sourceFilename = os.path.abspath(sourceFilename)
        # create file backend
        self.fileBackend = FileBackend(self.sourceFilename)
        self.baseDir = os.path.abspath(baseDir)
        self.additionalHead = additionalHead
        self.sigintCount = 0

        assert os.path.exists(self.baseDir)
        assert os.path.isdir(self.baseDir)

    def run(self):

        # register signal
        signal.signal(signal.SIGINT, self._handle_sigint)

        httpd = NewHS(self.ip, self.port, self.baseDir, self.fileBackend, self.get_remotemd_html)
        sa = httpd.socket.getsockname()
        print('Starting HTTP server on {}:{}'.format(sa[0], sa[1]))

        httpd.serve_forever()


    def _handle_sigint(self, signal, frame):
        if self.sigintCount > 0:
            print('Terminating the server...')
            exit(0)

        self.sigintCount = 1
        userInput = input('Do you want to terminate the server? (y/n)').lower()
        self.sigintCount = 0

        if len(userInput) > 0 and userInput[0] == 'y':
            exit(0)
        elif userInput[0] == 'n':
            print('Termination aborted')
        else:
            print('Invalid input, termination aborted')


    def get_remotemd_html(self):
        # read remotemd template
        with open(os.path.join(htmlDir, 'remotemd.html'), 'r') as infile:
            template = infile.read()
        # replace contents
        _assert('!!!!filename' in template, 'invalid template: cannot find filename field')
        _assert('!!!!content' in template, 'invalid template: cannot find content field')
        _assert('!!!!head' in template, 'invalid template: cannot find content field')
        pathData = html.escape(self.sourceFilename)
        fileData = self.fileBackend.read_file()
        fileData = html.escape(fileData)
        pageHtml = template.replace('!!!!filename', pathData).replace('!!!!content', fileData).replace('!!!!head', self.additionalHead)
        return pageHtml
