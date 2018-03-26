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

    def key(self, prefix, filename):
        if len(prefix) > 0 and not prefix.endswith('/'):
            prefix += '/'
        return prefix + filename

    def upload(self, prefix, files):
        for f in files:
            self.client.upload_fileobj(f, self.bucket, self.key(prefix, f.name))

    def download(self, prefix, filename, to):
        self.client.download_fileobj(self.bucket, self.key(prefix, filename), to)

    def delete(self, prefix, filename):
        self.client.delete_object(Bucket=self.bucket, Key=self.key(prefix, filename))
