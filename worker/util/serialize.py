from stencila.schema.types import Entity


def serialize(node):
    """
    Serialize a node into a Python object.

    Allow us to return a Stencila Schema node as the result of
    a job. This function would be best in `stencila.schema`.
    But it's not, so it's here. For now.
    """
    if isinstance(node, Entity):
        node_dict = {"type": node.__class__.__name__}
        node_dict.update(serialize(node.__dict__))
        return node_dict
    elif isinstance(node, list):
        return [serialize(child) for child in node]
    elif isinstance(node, dict):
        return dict([(key, serialize(value)) for key, value in node.items()])
    else:
        return node
