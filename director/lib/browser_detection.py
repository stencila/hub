import typing


def user_agent_is_internet_explorer(user_agent: typing.Optional[str]) -> bool:
    if not user_agent:  # if no user agent, be safe and assume not IE
        return False

    for search_string in ('MSIE', 'Trident/7.0'):
        if search_string in user_agent:
            return True

    return False
