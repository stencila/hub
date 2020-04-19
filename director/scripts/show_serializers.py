"""
Print representations of the API's model serializers.

DRF provides verbose representations of `ModelSerializers`.
These are useful for debugging how serializer fields are
automagically generated from models.
See https://www.django-rest-framework.org/api-guide/serializers/#inspecting-a-modelserializer

One quick way to develop a serializer is to use "_all__" fields e.g.

    class JobSerializer(serializers.ModelSerializer):

        class Meta:
            model = Job
            fields = "__all__"

Then run this script and copy and paste and edit, the fields as needed e.g.

    class JobSerializer(serializers.ModelSerializer):

        id = CharField(read_only=True)

        class Meta:
            model = Job
            fields = "__all__"


This script prints representations for several model
serializers. Feel free to add them as needed.
"""

from jobs.api.serializers import JobSerializer
from projects.api.serializers import ProjectSerializer, SnapshotSerializer
from users.api.serializers import TokenSerializer, UserSerializer

serializers = [
    JobSerializer,
    ProjectSerializer,
    SnapshotSerializer,
    TokenSerializer,
    UserSerializer,
]


def run(*args):
    for Serializer in serializers:
        print(repr(Serializer()), "\n")
