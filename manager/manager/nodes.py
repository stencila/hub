"""
Utility functions for dealing with Stencila Schema nodes.
"""


def node_text_content(node) -> str:
    """
    Get the text content of a node.
    """
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return " ".join(map(node_text_content, node))
    if isinstance(node, dict):
        if "text" in node:
            return node_text_content(node["text"])
        if "content" in node:
            return node_text_content(node["content"])
        if "items" in node:
            return node_text_content(node["items"])
    return str(node)
