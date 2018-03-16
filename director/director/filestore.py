from django.conf import settings
import boto3

class Client(object):

    def __init__(self, bucket=None):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        self.bucket = bucket if bucket else settings.AWS_STORAGE_BUCKET_NAME

    def list(self, prefix):
        if len(prefix) > 0 and not prefix.endswith('/'):
            prefix += '/'
        response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
        return response.get('Contents', [])

    def upload(self, prefix, files):
        for f in files:
            key = "%s/%s" % (prefix, f.name)
            self.client.upload_fileobj(f, self.bucket, key)

    def download(self, prefix, filename, to):
        if len(prefix) > 0 and not prefix.endswith('/'):
            prefix += '/'
        key = prefix + filename
        self.client.download_fileobj(self.bucket, key, to)
