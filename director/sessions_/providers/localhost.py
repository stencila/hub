import sh
import subprocess
import os


class Localhost:
    '''
    Localhost provider for session Workers.
    Just a stub for a locally run worker.
    '''

    def launch(self, worker):
        print 'You should have run `make worker-rundev` or similar already'

    def terminate(self, worker):
        print 'You need to stop the worker.py process yourself!'
