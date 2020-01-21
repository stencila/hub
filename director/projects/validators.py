from django.core.exceptions import ValidationError

from lib.constants import DISALLOWED_PUBLISHED_ROOTS


def validate_publish_url_path(url_path: str) -> None:
    url_path = url_path.strip('/')
    if '?' in url_path or '&' in url_path or '#' in url_path:
        raise ValidationError('The URL path must not contain the characters "?", "&" or "#".')

    for i, component in enumerate(url_path.split('/')):
        if i == 0 and component.lower() in DISALLOWED_PUBLISHED_ROOTS:
            raise ValidationError('The URL path can\'t start with "{}/".'.format(component))

        if component == '':
            raise ValidationError('The URL Path must not contain empty components.')
        if component == '..' or component == '.':
            raise ValidationError('The URL Path must not contain the components ".." or ".".')
