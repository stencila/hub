class FromContextDefault:
    """
    A serializer field default that gets the value from the serializer context.

    This is similar to `CurrentUserDefault` etc.
    See https://www.django-rest-framework.org/api-guide/validators/#advanced-field-defaults

    Thanks to https://stackoverflow.com/a/43909534.
    """

    def __init__(self, value_fn):
        self.value_fn = value_fn

    def set_context(self, serializer_field):
        """Set the value from the context."""
        self.value = self.value_fn(serializer_field.context)

    def __call__(self):
        """Return the default value."""
        return self.value
