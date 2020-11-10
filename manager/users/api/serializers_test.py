from users.api.serializers import UserSerializer
from users.models import User


def test_user_serializer_no_personal_account():
    """
    A regression test for issue https://github.com/stencila/hub/issues/813.
    """
    user = User()
    data = UserSerializer(user).data
    assert data == dict(
        display_name=None,
        first_name="",
        id=None,
        image=None,
        last_name="",
        location=None,
        public_email=None,
        username="",
        website=None,
    )
