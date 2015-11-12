import sh
import subprocess
import os


class VirtualBox:
    '''
    VirtualBox provider for session Workers
    '''

    def launch(self, worker):
        # `vagrant up` is slow even when VM is already running so bypass that with a
        # grep of the process name
        if not subprocess.call(
            "ps aux | grep '[V]BoxHeadless --comment stencila-worker'",
            shell=True,
            stdout=open(os.devnull, 'w')
        ) == 0:
            sh.make('worker-launch-vagrant')
        worker.ip = "10.0.1.100"
        worker.platform_id = "vbox-on-localhost"

    def terminate(self, worker):
        sh.vagrant('halt', 'worker')
