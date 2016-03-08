'''
Allow for one S3 bucket with different roots for static and "media" (user uploads)

See:
	http://stackoverflow.com/questions/10390244/how-to-set-up-a-django-project-with-django-storages-and-amazon-s3-but-with-diff
	https://gist.github.com/defrex/82680e858281d3d3e6e4
	http://www.laurii.info/2013/05/improve-s3boto-djangostorages-performance-custom-settings/

See https://github.com/jschneier/django-storages/blob/master/storages/backends/s3boto.py#L189
for available settings.
'''
from django.conf import settings
from storages.backends.s3boto import S3BotoStorage
from django.core.files.storage import FileSystemStorage

class StaticS3BotoStorage(S3BotoStorage):
	'''
	Used for "STATIC_ROOT" which is for static files
	'''
	host = 's3-us-west-2.amazonaws.com'
	bucket_name = 'static.stenci.la'
	secure_urls = False


class UploadsS3BotoStorage(S3BotoStorage):
	'''
	Used for "MEDIA_ROOT" which is for user uploads
	'''
	host = 's3-us-west-2.amazonaws.com'
	bucket_name = 'uploads.stenci.la'
	secure_urls = False


class SnapshotsS3BotoStorage(S3BotoStorage):
	'''
	Used for `components.models.Snapshot`
	'''

	def __init__(self):
		self.host = 's3-us-west-2.amazonaws.com'
		self.bucket_name = 'snapshots.stenci.la'
		self.secure_urls = False
		SnapshotsS3BotoStorage.__init__(self)

class SnapshotsFileSystemStorage(FileSystemStorage):
	'''
	Used for `components.models.Snapshot` when in local mode
	'''
	location = 'snapshots'

if settings.MODE=='local':
	SnapshotsStorage = SnapshotsFileSystemStorage
else:
	SnapshotsStorage = SnapshotsS3BotoStorage
