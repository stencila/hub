'''
Allow for one S3 bucket with different roots for static and "media" (user uploads)

See:
	http://stackoverflow.com/questions/10390244/how-to-set-up-a-django-project-with-django-storages-and-amazon-s3-but-with-diff
	https://gist.github.com/defrex/82680e858281d3d3e6e4
	http://www.laurii.info/2013/05/improve-s3boto-djangostorages-performance-custom-settings/
'''
from storages.backends.s3boto import S3BotoStorage


class StaticS3BotoStorage(S3BotoStorage):
	'''
	Used for "STATIC_ROOT" which is for static files
	'''
	location = 'static'


class UploadsS3BotoStorage(S3BotoStorage):
	'''
	Used for "MEDIA_ROOT" which is for user uploads
	'''
	location = 'uploads'
