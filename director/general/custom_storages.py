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

'''
Allow for one S3 bucket with different roots for static and "media" (user uploads)

See:
	http://stackoverflow.com/questions/10390244/how-to-set-up-a-django-project-with-django-storages-and-amazon-s3-but-with-diff
	https://gist.github.com/defrex/82680e858281d3d3e6e4
	http://www.laurii.info/2013/05/improve-s3boto-djangostorages-performance-custom-settings/

See https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py#L189
for available settings.

We need to define S3BotoStorage options in `__init__` because of way `storages` initialises
them from env vars on module import. Related to http://stackoverflow.com/a/24750663/4625911.

We use the following set ups to provide HTTPS secure access to snapshots. We could
do a redirect in nginx.conf as we do for get.stenci.la but that seems unessary for these

	self.url_protocol = 'https'
	self.custom_domain = 's3-us-west-2.amazonaws.com/snapshots.stencila.io'
	self.secure_urls = True
'''
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import FileSystemStorage


class StaticS3BotoStorage(S3BotoStorage):
	'''
	Used for "STATIC_ROOT" which is for static files
	'''
	def __init__(self):
		self.host = 's3-us-west-2.amazonaws.com'
		self.bucket_name = 'static.stenci.la'
		self.secure_urls = False
		S3BotoStorage.__init__(self)


class UploadsS3BotoStorage(S3BotoStorage):
	'''
	Used for "MEDIA_ROOT" which is for user uploads
	'''

	def __init__(self):
		self.host = 's3-us-west-2.amazonaws.com'
		self.bucket_name = 'uploads.stencila.io'
		# See note above about the following settings
		self.url_protocol = 'https'
		self.custom_domain = 's3-us-west-2.amazonaws.com/uploads.stencila.io'
		self.secure_urls = True
		S3BotoStorage.__init__(self)


class SnapshotsS3BotoStorage(S3BotoStorage):
	'''
	Used for `components.models.Snapshot`
	'''

	def __init__(self):
		self.host = 's3-us-west-2.amazonaws.com'
		self.bucket_name = 'snapshots.stencila.io'
		# See note above about the following settings
		self.url_protocol = 'https'
		self.custom_domain = 's3-us-west-2.amazonaws.com/snapshots.stencila.io'
		self.secure_urls = True
		S3BotoStorage.__init__(self)


class SnapshotsFileSystemStorage(FileSystemStorage):
	'''
	Used for `components.models.Snapshot` when in local mode
	'''
	location = 'snapshots'


if settings.MODE=='local':
	SnapshotsStorage = SnapshotsFileSystemStorage
else:
	SnapshotsStorage = SnapshotsS3BotoStorage
