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
        self.value = self.value_fn(serializer_field.context)

    def __call__(self):
        return self.value
