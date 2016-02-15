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
        connection = self.connection()

        # Specify size of root device; the default 8Gb was found
        # to be insufficient
        dev_sda1 = boto.ec2.blockdevicemapping.EBSBlockDeviceType()
        dev_sda1.size = 100 # size in Gigabytes
        dev_sda1.volume_type = 'gp2' # General Purpose (SSD) instead of the defaul 'standard' (magnetic)
        block_device_map = boto.ec2.blockdevicemapping.BlockDeviceMapping()
        block_device_map['/dev/sda1'] = dev_sda1

        reservation = connection.run_instances(
            image_id=self.ami(),
            min_count=1,
            max_count=1,
            key_name='stencila-aws-us-west-2-key-pair-1',
            instance_type='t2.small',
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
