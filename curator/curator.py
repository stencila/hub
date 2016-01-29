import os
import sys
import tempfile
import json

# sh : for convienient running of shell commands
from sh import git, chgrp, chmod, cp

# Werkzeug : for a simple HTTP server
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.serving import run_simple

# Other utilities
import glob2
from flanker.addresslib.address import parse as parse_email
import requests

# Stencila : for reading and manipulating components
os.environ['STENCILA_STORES'] = '/srv/stencila/store'
import stencila

DEV_MODE = len(sys.argv) > 1 and sys.argv[1] == 'dev'

# Token for communication between roles
if DEV_MODE:
    COMMS_TOKEN = 'an-insecure-token-only-used-in-development'
else:
    COMMS_TOKEN = file(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', 'secrets', 'stencila-comms-token.txt'
        )
    ).read()


class Curator:
    '''
    Provides a server interface to component repositories
    '''

    # Filesystems path to the directory where components are stored
    store = '/srv/stencila/store'

    @staticmethod
    def store_temporary():
        '''
        Change the store to a temporary directory.

        This is intended for use during testing only.
        It's supposed to be a bit like the temporary testing
        databases that Django sets up. You should call this
        method at the start of tests.
        '''
        Curator.store = tempfile.mkdtemp()

    @staticmethod
    def path(address, extra=''):
        '''
        Get the path to a component's working directory
        '''
        return os.path.join(Curator.store, address, extra)

    @staticmethod
    def address(path):
        '''
        Get the address of a component from it's working directory path
        '''
        return os.path.relpath(path, Curator.store)

    @staticmethod
    def component(address):
        '''
        Get a component at an address. Used in methods below.
        '''
        path = Curator.path(address).encode("utf-8")
        return stencila.grab(path)

    def git(self, path, *args, **kwargs):
        '''
        Runs a git command in the component repository.

        This is a convienience method which sets the --git-dir and --work-tree arguments
        so that it is not necessary to cd into the component directory to do stuff
        '''
        return git(
            # Set directory arguments
            '--git-dir=%s' % os.path.join(path, '.git'),
            '--work-tree=%s' % path,
            # Git produces different output on a TTY than on a pipe
            # Force a pipe so don't get strange, invisible characters in output
            _tty_out=False,
            # Give other arguments
            *args,
            **kwargs
        )

    def revision(self, path):
        '''
        Given a path to a repository, return the commit ID of HEAD.
        '''
        return self.git(path, 'rev-parse', 'HEAD').strip()

    def setup(self, path):
        '''
        Sets up a component repository so it can be served

        This method is used by `self.init()` and `self.clone()` when a
        new component is created using either of these methods.
        '''

        # Copy post-receive into .git/hooks so necessary operations can
        # be run on the repository after pushes
        # This script must be executable, that is done below
        cp('-f', 'git-post-receive.sh', os.path.join(path, '.git/hooks/post-receive'))

        # Allow the (non-bare) repostory to be pushed to by setting
        # receive.denyCurrentBranch to ignore
        # By default Git does not allow pushing to a repo with a working dir
        # because the working tree can become out of sync.
        # Our post-receive hook (above) deals with that
        self.git(path, 'config', 'receive.denyCurrentBranch', 'ignore')

        # Set the default user for the repository
        # If you don't do this, then when doing a git commit as user www-data,
        # Git will complain that these config values are not set. That could be done globally
        # for the www-data user, but doing this seems cleaner
        self.git(path, 'config', 'user.name', 'Stencila Hub')
        self.git(path, 'config', 'user.email', 'hub@stenci.la')

        # These filesystem permissions fail when `/srv/stencila/store` is a NFS mount
        # So currently commented out until we work out best way to deal with permissions
        # on the store

        # Change the group of the new component recursively so that
        # users including www-data can modify it
        chgrp('-R', 'stencila', path)

        # Set permissions on the repository so that post-receive.sh is executable
        # and content can be read by Nginx for serving
        chmod('-R', '775', path)

    def init(self, address, type):
        '''
        Create a new component repository
        '''
        path = self.path(address)
        if os.path.exists(path):
            raise Exception('Component repository already exists at %s' % path)
        git.init(path)
        self.setup(path)

        # Add necessary files and create a first commit. If there are no
        # files added then commit will fail
        if type == 'stencil':
            file(os.path.join(path, 'stencil.cila'), 'w').write('')
            self.git(path, 'add', 'stencil.cila')
        elif type == 'sheet':
            file(os.path.join(path, 'sheet.tsv'), 'w').write('')
            self.git(path, 'add', 'sheet.tsv')
        else:
            raise Exception('No file added for initial commit')
        self.git(path, 'commit', '-m', 'Initial commit')

        # Save the component page as index.html
        com = self.component(address)
        com.page('index.html')

    def clone(self, origin, address):
        '''
        Clone a component repository
        '''
        from_path = self.path(origin)
        to_path = self.path(address)
        if os.path.exists(to_path):
            raise Exception('Component repository already exists at %s' % to_path)
        git.clone(from_path, to_path)
        self.setup(to_path)

    def fork(self, source, dest):
        '''
        Fork a component repository

        Makes the forkee repo the "upstream" remote
        '''
        source_path = self.path(source)
        dest_path = self.path(dest)
        if os.path.exists(dest_path):
            raise Exception('Component repository already exists at %s' % dest_path)
        git.clone(source_path, dest_path)
        self.git(dest_path, 'remote', 'rename', 'origin', 'upstream')
        self.setup(dest_path)

    def content(self, address, format):
        path = self.path(address)
        com = self.component(address)
        if format == 'html':
            current_content = com.html()
        elif format == 'cila':
            current_content = com.cila()
        else:
            # This should never happen thanks to validation above
            raise Exception("Unknown format when getting stencil content")
        return dict(
            revision=self.revision(path),
            format=format,
            content=current_content,
        )

    def save(self, address, format, content, revision, author_name, author_email):
        '''
        Apply a diff to a component repository

        Reports back on the success or failure of the diff application
        '''
        path = self.path(address)
        # TODO: obtain a lock for performing this operation
        # Make sure the author is valid
        author_email = parse_email(author_email)
        if not author_email:
            raise Exception('"author" is in invalid form.')
        assert format in ['html', 'cila']
        # Create stencila object for the address
        com = self.component(address)
        # Ensure that the caller has the latest revision. If not, updating is disallowed, to stop people using
        # this endpoint overwriting changes that someone may have pushed directly to the git repository
        current_head = self.revision(path)
        if current_head != revision:
            current_content = None
            if format == 'html':
                current_content = com.html()
            elif format == 'cila':
                current_content = com.cila()
            else:
                # This should never happen thanks to validation above
                raise Exception("Unknown format when getting stencil content")
            return dict(
                status=1,
                revision=current_head,
                content=current_content,
            )

        # Update the stencil to be based off the content/format that we've been sent
        if format == 'html':
            com.html(str(content))
        else:
            com.cila(str(content))
        # Save the stencil
        com.write('')

        # If we don't have any changes, early exit
        if not self.git(path, 'status', '--porcelain'):
            return dict(
                status=0,
                revision=current_head,
            )

        # Add the changes to git
        self.git(path, 'add', com.source())

        # Commit the changes to the repository
        self.git(
            path,
            'commit',
            '-m', 'Saved by API call',
            '--author="%s <%s>"' % (author_name, author_email)
        )

        # Tell the caller about our new revision
        new_revision = self.revision(path)
        return dict(
            status=0,
            revision=new_revision,
        )

    ###########################################################################
    # Component reading, compiling etc

    def meta(self, address):
        '''
        Get metadata for a component at address
        '''
        com = self.component(address)
        return dict(
            type=com.__class__.__name__.lower(),
            title=com.title(),
            summary=com.description(),
        )

    def commits(self, address):
        '''
        Get list of commits for a component at address
        '''
        com = self.component(address)
        return com.commits()

    def received(self, directory):
        '''
        Called when a working directory has been updated by a `git push` by the
        `git-post-receive.sh` script. Currently,

            - compiles component to `page.html`
            - pings `director` to let it know a change has been made

        '''
        # Extract and address from the directory path
        address = self.address(directory)
        # Get the component
        com = self.component(address)
        # Create index.html page
        com.page('index.html')
        # Ping director
        requests.put('https://stenci.la/%s@received' % address, json={
            'token': COMMS_TOKEN
        })

    ###########################################################################
    # Administration
    #
    # Methods that operate over several component repos

    def resetup(self, address=None):
        '''
        Re-setup component directories e.g. when the `git-post-receive.sh` script
        is updated
        '''
        if address is None:
            root = self.store + '/'
        else:
            root = self.path(address)
        result = []
        for git_dir in glob2.glob(root+'**/.git'):
            com_dir = os.path.dirname(git_dir)
            com_address = self.address(com_dir)
            self.setup(com_dir)
            result.append(com_address)
        return result

    ###########################################################################
    # HTTP serving

    urls = Map([
        Rule('/init', endpoint='init', methods=['POST']),
        Rule('/clone', endpoint='clone', methods=['POST']),
        Rule('/fork', endpoint='fork', methods=['POST']),
        Rule('/content', endpoint='content', methods=['POST']),
        Rule('/save', endpoint='save', methods=['POST']),
        Rule('/meta', endpoint='meta', methods=['POST']),
        Rule('/commits', endpoint='commits', methods=['POST']),
        Rule('/received', endpoint='received', methods=['POST']),

        Rule('/resetup', endpoint='resetup', methods=['POST']),
    ])

    def __call__(self, environ, start_response):
        '''
        WSGI application interface

        Does conversion of JSON request data into method args and
        method output back into a JSON response
        '''
        request = Request(environ)
        adapter = self.urls.bind_to_environ(request.environ)
        try:
            endpoint, kwargs = adapter.match(method=request.method)
            method = getattr(self, endpoint)
            input = json.loads(request.data) if request.data else {}
            output = method(**input)
            data = json.dumps(output) if output is not None else '{}'
            response = Response(data, mimetype='application/json')
        except HTTPException, e:
            response = e
        except Exception, e:
            response = Response(json.dumps({'error': repr(e)}), status=400)
        return response(environ, start_response)

    @staticmethod
    def run():
        '''
        Run the HTTP server

        To reduce dependencies use the werkzeug simple server.
        Whilst not recommended for production, this server runs
        on a private network and only has one client (stenci.la) so
        risks should be dramatically reduced
        '''

        if DEV_MODE:
            print 'Running in development mode. File will reload on changes.'

        # Run the server
        curator = Curator()
        run_simple(
            '0.0.0.0',
            7310,
            curator,
            use_debugger=DEV_MODE,
            use_reloader=DEV_MODE,
            threaded=True
        )

if __name__ == '__main__':
    Curator.run()
