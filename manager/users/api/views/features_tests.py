from manager.testing import DatabaseTestCase
from users.models import Flag


class FeaturesTestCase(DatabaseTestCase):
    """Tests getting and setting of feature flags by users."""

    @classmethod
    def setUpClass(cls):
        """Add some features to be able to get and set"""
        super().setUpClass()

        Flag.objects.create(
            name="feature_a", label="Feature A", default="on", settable=True
        )
        Flag.objects.create(
            name="feature_b", label="Feature B", default="off", settable=True
        )

    def test_ok(self):
        features = self.retrieve(self.ada, "api-features").data
        assert features == {"feature_a": "on", "feature_b": "off"}

        features = self.update(
            self.ada, "api-features", {"feature_a": "off", "feature_b": "on"}
        ).data
        assert features == {"feature_a": "off", "feature_b": "on"}

        features = self.update(
            self.ada, "api-features", {"feature_a": True, "feature_b": False}
        ).data
        assert features == {"feature_a": "on", "feature_b": "off"}

        features = self.update(
            self.ada, "api-features", {"feature_a": "false", "feature_b": "true"}
        ).data
        assert features == {"feature_a": "off", "feature_b": "on"}

    def test_errors(self):
        response = self.update(self.ada, "api-features", {"foo": "bar"})
        assert response.status_code == 400
        assert response.data["errors"][0]["message"] == 'Invalid feature name "foo"'

        response = self.update(self.ada, "api-features", {"feature_a": "nope"})
        assert response.status_code == 400
        assert response.data["errors"][0]["message"] == 'Invalid feature state "nope"'
