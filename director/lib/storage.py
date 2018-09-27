import fnmatch

from storages.backends.gcloud import GoogleCloudStorage
from storages.utils import setting


class CustomPublicGoogleCloudStorage(GoogleCloudStorage):
    """
    Override the `write` method of `GoogleCloudStorage` to set the paths that match a glob in the
    `GS_PUBLIC_READABLE_PATHS` setting list to readable after upload
    """
    public_readable_paths = setting('GS_PUBLIC_READABLE_PATHS', [])

    def _save(self, name, content):
        cleaned_name = super()._save(name, content)
        for public_readable_path in self.public_readable_paths:
            if fnmatch.fnmatch(cleaned_name, public_readable_path):
                encoded_name = self._encode_name(name)
                blob = self.bucket.blob(encoded_name)
                blob.make_public()

                break

        return cleaned_name
