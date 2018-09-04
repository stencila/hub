from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from rest_framework import generics

from users.serializers import UserSerializer

User = get_user_model()

USER_QUERY_MIN_LENGTH = 3


class UserSearch(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self) -> QuerySet:
        if 'q' not in self.request.query_params:
            raise ValueError('Missing query parameter q')

        query = self.request.query_params['q']

        if len(query) < USER_QUERY_MIN_LENGTH:
            raise ValueError('Query q is too short, minimum length is {}'.format(USER_QUERY_MIN_LENGTH))

        return User.objects.filter(username__istartswith=query)
