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

import time

from django.conf import settings

import boto.ec2


class EC2:
    '''
    Amazon EC2 provider for session Workers
    '''

    def connection(self):
        '''
        Get a EC2 connection to use in start() and stop()
        '''
        return boto.ec2.connect_to_region(
            'us-west-2',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def ami(self):
        '''
        Get the id of the AMI (Amazon Machine Image)
        for the worker. This changes everytime the worker
        image is updated so needs to be fetched by name.

        It is tempting to store the id but that means it could go stale when updates
        are done. Since workers won't be started that often better just to suffer the
        slight wait to get the image id.
        '''
        connection = self.connection()
        image = connection.get_all_images(
            filters={'name': 'stencila-worker-image'}
        )[0]
        return image.id

    def launch(self, worker):
        '''
        Translates the worker's attributes into attributes of an EC2 instance and launches it
        '''
        connection = self.connection()

        # Determine the instance type
        # Currently a very simplistic choice of instance type
        # until various optimisations are done.
        # See https://aws.amazon.com/ec2/pricing/
        instance_type = 't2.micro'
        # Note these if statements act like a series of instance
        # type upgrades, not a branching if/else.
        # Also, because discrete combinations of CPU and memory
        # there is no guarantee that your exact combination will
        # be met
        if worker.cpus >= 1 and worker.memory >= 2:
            instance_type = 't2.small'
        if worker.cpus >= 2 and worker.memory >= 4:
            instance_type = 't2.medium'
        if worker.cpus >= 2 and worker.memory >= 8:
            instance_type = 't2.large'

        # Specify root storage device
        dev_sda1 = boto.ec2.blockdevicemapping.BlockDeviceType(
            size=int(worker.storage),
            volume_type='gp2',  # General Purpose (SSD) instead of the defaul 'standard' (magnetic)
            delete_on_termination=True  # Defaults to False in which case blocks will persist and need to be deleted manually
        )
        block_device_map = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        block_device_map['/dev/sda1'] = dev_sda1

        reservation = connection.run_instances(
            image_id=self.ami(),
            min_count=1,
            max_count=1,
            key_name='stencila-aws-us-west-2-key-pair-1',
            instance_type=instance_type,
            # stencila-private-subnet-1
            subnet_id='subnet-a0599cf9',
            # When launching into a subnet apparently `security_group_ids` must
            # be used instead of `security_groups` (names)
            security_group_ids=[
                # stencila-worker-sg
                'sg-930401f6'
            ],
            block_device_map=block_device_map
        )
        instance = reservation.instances[0]

        # Number of seconds to fail timeout waiting for server to launch
        timeout = 120
        start = time.time()
        while True:
            status = instance.update()
            if status != 'pending':
                break
            if time.time()-start > timeout:
                raise Exception('Timed out trying to start worker: %s' % worker)
            time.sleep(1)

        if status == 'running':
            worker.provider_id = instance.id
            worker.ip = instance.private_ip_address
            instance.add_tag("Name", "stencila-worker")
        else:
            raise Exception('Failed to start worker: %s : %s' % (worker, status))

    def terminate(self, worker):
        connection = self.connection()
        connection.terminate_instances(
            instance_ids=[worker.provider_id]
        )
