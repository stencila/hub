from rest_framework import negotiation


class IgnoreClientContentNegotiation(negotiation.DefaultContentNegotiation):
    """
    Custom content negotiator that ignores the client requested format.

    Returns the first default renderer (usually JSON).
    Used to bypass DRF content negotiation for actions that
    do the content negotiation and rendering themselves.
    The renderer selected below will be used for other actions and for any errors.
    Without this DRF will complain that the client specified format is not supported
    or the endpoint can not be found.
    """

    def select_renderer(self, request, renderers, format_suffix):
        return (renderers[0], renderers[0].media_type)
