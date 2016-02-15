import sys
import subprocess
import datetime
import json
import socket
import threading
from collections import OrderedDict

import requests.exceptions

# For simple web server
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.serving import run_simple

# Docker API for more advanced usage of Docker
# Some don't like this module (e.g. http://blog.bordage.pro/avoid-docker-py/)
# but it seems to be close to the official https://docs.docker.com/reference/api/docker_remote_api/
# even though it is sometimes annoyingly different to the CLI. It has the advantage of
# giving us JSON-like results we can forward on to hub
#
# See https://docker-py.readthedocs.org/en/latest/api/
import docker as dockerapi
docker = dockerapi.Client(base_url='unix://var/run/docker.sock')

# For info on the machine
import psutil

# Determine deployment MODE
try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = None

dev = len(sys.argv) > 1 and sys.argv[1] == 'dev'

if dev:
    MODE = 'local'
elif HOSTNAME == 'stencila-worker-vagrant':
    MODE = 'vagrant'
else:
    MODE = 'prod'


class Worker:
    '''
    Starts and stops sessions and returns information on them and this machine
    '''

    def response(self, data, convert=True):
        if convert:
            data = json.dumps(data)
        response = Response(data, mimetype='application/json')
        return response

    def start(self, request):
        '''
        Starts a session
        '''
        # Get and check for parameters
        data = json.loads(request.data)
        pars = {}
        for par in 'image', 'command', 'memory', 'cpu', 'token':
            value = data.get(par, None)
            if value is None:
                return self.response({'error': 'argument not supplied: '+par})
            else:
                pars[par] = value

        # Environment variables
        environment = {
            'STENCILA_HUB_TOKEN': pars['token']
        }

        # When running in a local or Vagrant environment, containers need to get
        # components from the director running in the private network on HTTP
        if MODE == 'local':
            environment['STENCILA_HUB_ROOT'] = 'http://10.0.1.25:7300'
        elif MODE == 'vagrant':
            environment['STENCILA_HUB_ROOT'] = 'http://10.0.1.25'

        host_config = docker.create_host_config(
            # See http://docker-py.readthedocs.org/en/latest/hostconfig/ for all options
            publish_all_ports=True,
            mem_limit=pars['memory']
        )
        session = docker.create_container(
            image=pars['image'],           # image (str): The image to run
            command=pars['command'],       # command (str or list): The command to be run in the container
                                           # hostname (str): Optional hostname for the container
                                           # user (str or int): Username or UID
            detach=True,                   # detach (bool): Detached mode: run container in the background and print new container Id
                                           # stdin_open (bool): Keep STDIN open even if not attached
                                           # tty (bool): Allocate a pseudo-TTY
            ports=[7373],                  # ports (list of ints): A list of port numbers
            environment=environment,        # environment (dict or list): A dictionary or a list of strings in the following format ["PASSWORD=xxx"] or {"PASSWORD": "xxx"}.
                                            # dns (list): DNS name servers
                                            # volumes (str or list):
                                            # volumes_from (str or list): List of container names or Ids to get volumes from. Optionally a single string joining container id's with commas
                                            # network_disabled (bool): Disable networking
                                            # name (str): A name for the container
                                            # entrypoint (str or list): An entrypoint
            cpu_shares=pars['cpu'],         # cpu_shares (int or float): CPU shares (relative weight)
                                            # working_dir (str): Path to the working directory
                                            # domainname (str or list): Set custom DNS search domains
                                            # memswap_limit (int):
            host_config=host_config         # host_config (dict): A HostConfig dictionary
                                            # mac_address (str): The Mac Address to assign the container
                                            # labels (dict or list): A dictionary of name-value labels (e.g. {"label1": "value1", "label2": "value2"}) or a list of names of labels to set with empty values (e.g. ["label1", "label2"])
        )
        docker.start(
            session.get('Id'),              # container (str): The container to start
        )
        return self.response(OrderedDict(
            uuid=session.get('Id'),
            warning=session.get('Warnings')
        ))

    def get(self, request, uuid=None):
        '''
        Get running sessions
        '''
        data = []
        for container in docker.containers():
            # Get id
            id = container.get('Id')
            # Convert created timestamp to a datetime called 'started'
            started = container.get('Created')
            started = datetime.datetime.utcfromtimestamp(int(started)).strftime('%Y-%m-%dT%H:%M:%SZ')
            # Get the port that the session is published on the host
            port = docker.port(id, 7373)[0].get('HostPort')
            # Check if session is ready on that port. It is not enough to
            # just use netstat to see if a process is listening on that
            # port. Have to actually get a HTTP OK response indicating that
            # the session server is started
            try:
                ready = len(subprocess.check_output(
                    'curl -is 127.0.0.1:%s | grep "HTTP/1.1 200 OK"' % port,
                    shell=True
                )) > 0
            except subprocess.CalledProcessError:
                # CalledProcessError occurs if for example, port does not exist
                ready = False
            # Serialiaze
            desc = OrderedDict(
                uuid=id,
                image=container.get('Image'),
                command=container.get('Command'),
                started=started,
                port=port,
                ready=ready,
                status=container.get('Status'),
            )
            if id == uuid:
                return self.response(desc)
            else:
                data.append(desc)
        # If specified a uuid and we get to here it means that
        # the uuid was not matched and we will return an empty 
        # list (as expected by director's `Worker.get()` method)
        if uuid is not None:
            data = []

        return self.response(data)

    def stats(self, request, uuid):
        '''
        Get detailed stats on a session
        '''
        # Check session is still alive
        active = False
        for container in docker.containers():
            if container.get('Id') == uuid:
                active = True
                break
        if not active:
            return self.response({'error': 'session appears to have stopped'})
        # The stats() method returns a generator (for
        # iterating over time). The generator creates Json Strings
        # so no conversion is needed. Just return the
        # first set of stats
        try:
            generator = docker.stats(uuid)
        except requests.exceptions.ReadTimeout:
            return self.response({'error': 'session appears to have stopped'})
        else:
            for stats in generator:
                return self.response(stats, convert=False)

    def logs(self, request, uuid):
        '''
        Get stdoutt and stderr for a session and return
        as text
        '''
        logs = docker.logs(
            container=uuid,
            stdout=True,
            stderr=True,
            timestamps=True
        )
        return self.response({'logs': logs})

    def stop(self, request, uuid):
        '''
        Stop a session

        Currently this forces an almost immeadiate kill of container.
        Need to workout how to do this more gracefully.
        In particular, getting an R session with a runnng Stencila server to shut itself down.
        '''
        docker.stop(
            uuid,  # container (str): The container to stop
            1      # timeout (int): Timeout in seconds to wait for the container to stop before sending a SIGKILL
        )
        return self.response({'ok': 1})

    def info(self, request):
        '''
        Return info on this worker computer e.g CPU usage, number of processes.

        This method return details based on system wide metrics available with psutil.
        See https://code.google.com/p/psutil/wiki/Documentation#System_related_functions

        Bytes are converted to megabytes (1MB = 1048576 bytes)
        '''
        info = OrderedDict([
            ('hostname', HOSTNAME),
            ('mode', MODE)
        ])
        # Timestamp
        info['time'] = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        # Number of sessions
        info['sessions'] = len(docker.containers())
        # Number of processes
        info['processes'] = len(psutil.pids())
        # Users. Convert list of named tuples to a JSON string
        info['users'] = json.dumps(psutil.users())
        # CPU percent: When interval is 0.0 or None compares system CPU times elapsed since last
        # call or module import, returning immediately
        info['cpu_percent'] = psutil.cpu_percent(interval=None)
        # CPU times
        cpu = psutil.cpu_times()
        for attr in 'user', 'system', 'idle', 'nice', 'iowait', 'irq', 'softirq':
            info['cpu_'+attr] = getattr(cpu, attr)
        # Virtual memory usage
        mem = psutil.virtual_memory()
        for attr in 'total', 'available', 'percent', 'used', 'free', 'active', 'inactive', 'cached':
            value = getattr(mem, attr)
            if attr != 'percent':
                value /= 1048576
            info['mem_'+attr] = value
        # Swap memory usage
        swap = psutil.swap_memory()
        for attr in 'total', 'used', 'free', 'percent', 'sin', 'sout':
            value = getattr(swap, attr)
            if attr != 'percent':
                value /= 1048576
            info['swap_'+attr] = value
        # Disk usage
        disk_use = psutil.disk_usage('/')
        for attr in 'total', 'used', 'free', 'percent':
            value = getattr(disk_use, attr)
            if attr != 'percent':
                value /= 1048576
            info['disk_use_'+attr] = value
        # Disk IO
        disk_io = psutil.disk_io_counters()
        for attr in 'read_count', 'write_count', 'read_bytes', 'write_bytes', 'read_time', 'write_time':
            value = getattr(disk_io, attr)
            if 'bytes' in attr:
                value /= 1048576
            info['disk_io_'+attr] = value
        # Network IO
        net_io = psutil.net_io_counters()
        for attr in 'bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv', 'errin', 'errout', 'dropin', 'dropout':
            value = getattr(net_io, attr)
            if 'bytes' in attr:
                value /= 1048576
            info['net_io_'+attr] = getattr(net_io, attr)

        return self.response(info)

    def pull(self, request):
        '''
        Pull all images. Usually called by director in response to a build notification.
        Because pulls are long running, uses a thread.
        '''
        image = None
        if len(request.data):
            image = json.loads(request.data).get('image', None)
        if image is None:
            images = ['ubuntu-14.04-python-2.7', 'ubuntu-14.04-r-3.2']
        else:
            images = [image]

        # Don't pull all images in the repo (there are many, one for each 
        # successful build), just latest. Other versions can be pulled "on-demand"
        tag = 'latest'

        def doit():
            for image in images:
                print docker.pull('stencila/%s:%s' % (image, tag))
        thread = threading.Thread(target=doit)
        thread.start()

        return self.response({})

    ###########################################################################
    # HTTP serving

    urls = Map([
        Rule('/start',                   endpoint='start', methods=['POST']),
        Rule('/get',                     endpoint='get',  methods=['GET']),
        Rule('/get/<string:uuid>',       endpoint='get',  methods=['GET']),
        Rule('/stats/<string:uuid>',     endpoint='stats',  methods=['GET']),
        Rule('/logs/<string:uuid>',      endpoint='logs',  methods=['GET']),
        Rule('/stop/<string:uuid>',      endpoint='stop',  methods=['DELETE']),
        Rule('/info',                    endpoint='info',  methods=['GET']),
        Rule('/pull',                    endpoint='pull',  methods=['PUT']),
    ])

    def __call__(self, environ, start_response):
        request = Request(environ)
        adapter = self.urls.bind_to_environ(request.environ)
        try:
            endpoint, kwargs = adapter.match(method=request.method)
            method = getattr(self, endpoint)
            response = method(request, **kwargs)
        except HTTPException, e:
            response = e
        except Exception, e:
            response = Response(json.dumps({'error': str(e)}), status=400)
        return response(environ, start_response)

    @staticmethod
    def run():
        # To reduce dependencies use the werkzeug simple server.
        # Whilst not recommended for production, this server runs
        # on a private network and only has one client (stenci.la)

        if dev:
            print 'Running in development mode. File will reload on changes.'

        # Run the server
        worker = Worker()
        run_simple(
            '0.0.0.0',
            7320,
            worker,
            threaded=True,
            use_debugger=dev,
            use_reloader=dev,
        )


Worker.run()
