#  This file is part of Stencila Hub.
#  
#  Copyright (C) 2015-2016 Stencila Ltd.
#  
#  Stencila Hub is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Stencila Hub is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

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
